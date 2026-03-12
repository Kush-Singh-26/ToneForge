import json
import os
from typing import Literal, Optional
from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing import TypedDict

# =============================================================================
#  0. ENVIRONMENT CONFIGURATION
# =============================================================================
load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    # This guard prevents the app from crashing with cryptic errors later
    raise ValueError("GROQ_API_KEY is missing. Ensure it is defined in your .env file.")

router = APIRouter()

# =============================================================================
#  1. LLM INSTANCES
# =============================================================================
# Negotiation and Legal require high reasoning - using the 70B versatile model
proposer_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)
responder_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.6)
evaluator_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
legal_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)


# =============================================================================
#  2. PYDANTIC MODELS
# =============================================================================
class NegotiationEmail(BaseModel):
    """One email turn in the negotiation thread."""

    role: Literal["proposer", "responder"] = Field(description="Who sent this email")
    subject: str
    body: str


class EvaluatorDecision(BaseModel):
    agreement_reached: bool = Field(description="True if both sides agreed on terms")
    summary: str = Field(description="Current state or final agreed terms")
    next_move: Optional[str] = Field(
        description="Concession/next step if no agreement yet"
    )


class LegalClause(BaseModel):
    clause_type: str = Field(description="e.g. Liability, Confidentiality, Payment")
    text: str = Field(description="Extracted clause text or paraphrase")
    risk_level: Literal["low", "medium", "high"]


class LegalParseOutput(BaseModel):
    obligations: list[str] = Field(description="Explicit obligations/duties found")
    deadlines: list[str] = Field(description="Dates, deadlines, or time constraints")
    clauses: list[LegalClause] = Field(
        description="Identified legal clauses with risk levels"
    )
    risk_flags: list[str] = Field(description="High-risk words or phrases")
    overall_risk: Literal["low", "medium", "high"] = Field(
        description="Overall legal risk rating"
    )
    plain_summary: str = Field(description="Plain-English explanation of commitments")


class NegotiationRequest(BaseModel):
    topic: str = Field(description="What is being negotiated")
    our_position: str = Field(description="Your desired outcome")
    their_position: str = Field(description="The other party's stated position")
    category: Literal["business", "corporate"]
    max_rounds: int = Field(
        default=3, ge=1, le=6, description="Back-and-forth rounds (1-6)"
    )


class LegalParseRequest(BaseModel):
    raw_email: str = Field(
        description="Full text of the legal/contract email to analyse."
    )


# =============================================================================
#  3. STATE TYPEDDICTS
# =============================================================================
class NegotiationState(TypedDict):
    topic: str
    our_position: str
    their_position: str
    category: Literal["business", "corporate"]
    rounds: int
    max_rounds: int
    history: list
    evaluator_decision: Optional[EvaluatorDecision]
    agreement_reached: bool


class LegalParseState(TypedDict):
    raw_email: str
    parse_result: Optional[LegalParseOutput]


# =============================================================================
#  4. PARSERS
# =============================================================================
negotiation_parser = PydanticOutputParser(pydantic_object=NegotiationEmail)
evaluator_parser = PydanticOutputParser(pydantic_object=EvaluatorDecision)
legal_parser = PydanticOutputParser(pydantic_object=LegalParseOutput)


# =============================================================================
#  5. SHARED HELPERS
# =============================================================================
def _escape_fmt(parser: PydanticOutputParser) -> str:
    """Escape curly braces in format instructions for f-string safety."""
    return parser.get_format_instructions().replace("{", "{{").replace("}", "}}")


# =============================================================================
#  6. PROMPT BUILDERS
# =============================================================================
def _build_proposer_prompt() -> ChatPromptTemplate:
    fmt = _escape_fmt(negotiation_parser)
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
You are a professional negotiator (PROPOSER — our side).
- Write a polite, firm email stating our current position.
- Acknowledge the other party's last response if one exists.
- Make a concrete proposal or concession toward agreement.
- Set role to "proposer". Return ONLY JSON.\n{fmt}
""",
            ),
            (
                "human",
                """
Topic: {topic}
Our position: {our_position}
Their position: {their_position}
Category: {category}
History so far:\n{history}
Suggested next move: {next_move}
""",
            ),
        ]
    )


def _build_responder_prompt() -> ChatPromptTemplate:
    fmt = _escape_fmt(negotiation_parser)
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
You are simulating the OTHER PARTY (RESPONDER — their side).
- Reply to the proposer's latest email.
- You may accept, partially accept, or counter-propose.
- Stay realistic — do not concede immediately.
- Set role to "responder". Return ONLY JSON.\n{fmt}
""",
            ),
            (
                "human",
                """
Topic: {topic}
Their original position: {their_position}
Our original position: {our_position}
Full history:\n{history}
Latest proposer email:\n{latest_email}
""",
            ),
        ]
    )


def _build_evaluator_prompt() -> ChatPromptTemplate:
    fmt = _escape_fmt(evaluator_parser)
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
You are a neutral negotiation evaluator.
1. Has agreement been reached? (both sides explicitly accepted the same terms)
2. If not, what concession should the proposer make next?
Be objective and concise. Return ONLY JSON.\n{fmt}
""",
            ),
            (
                "human",
                """
Topic: {topic}
Our position: {our_position}
Their position: {their_position}
Full history:\n{history}
""",
            ),
        ]
    )


def _build_legal_prompt() -> ChatPromptTemplate:
    fmt = _escape_fmt(legal_parser)
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
You are an expert legal email analyst. Extract ALL of the following:
1. Obligations  — explicit duties or commitments either party must fulfil.
2. Deadlines    — dates, time limits, or time-based conditions.
3. Clauses      — identifiable legal clause types (Liability, Confidentiality,
   Payment Terms, Termination, Indemnification, IP Ownership) each with risk level.
4. Risk Flags   — specific words/phrases carrying legal risk
   (e.g. "indemnify", "without limitation", "irrevocable", "sole discretion").
5. Overall Risk — low | medium | high.
6. Plain Summary — 2-4 plain-English sentences on what this email commits to
   and what the reader should watch out for.
Return ONLY JSON.\n{fmt}
""",
            ),
            ("human", "Email to analyse:\n\n{raw_email}"),
        ]
    )


# =============================================================================
#  7. NEGOTIATION LANGGRAPH
# =============================================================================
def _history_text(history: list) -> str:
    if not history:
        return "(No messages yet)"
    lines = []
    for i, e in enumerate(history, 1):
        role = e.role if hasattr(e, "role") else e["role"]
        subject = e.subject if hasattr(e, "subject") else e["subject"]
        body = e.body if hasattr(e, "body") else e["body"]
        lines.append(f"--- Turn {i} [{role.upper()}] ---\nSubject: {subject}\n{body}\n")
    return "\n".join(lines)


async def _node_proposer(state: NegotiationState) -> NegotiationState:
    next_move = ""
    if state["evaluator_decision"]:
        next_move = state["evaluator_decision"].next_move or ""
    chain = _build_proposer_prompt() | proposer_llm | negotiation_parser
    result = await chain.ainvoke(
        {
            "topic": state["topic"],
            "our_position": state["our_position"],
            "their_position": state["their_position"],
            "category": state["category"],
            "history": _history_text(state["history"]),
            "next_move": next_move,
        }
    )
    state["history"] = state["history"] + [result]
    state["rounds"] = state["rounds"] + 1
    return state


async def _node_responder(state: NegotiationState) -> NegotiationState:
    latest = state["history"][-1]
    chain = _build_responder_prompt() | responder_llm | negotiation_parser
    result = await chain.ainvoke(
        {
            "topic": state["topic"],
            "their_position": state["their_position"],
            "our_position": state["our_position"],
            "history": _history_text(state["history"]),
            "latest_email": f"Subject: {latest.subject}\n{latest.body}",
        }
    )
    state["history"] = state["history"] + [result]
    return state


async def _node_evaluator(state: NegotiationState) -> NegotiationState:
    chain = _build_evaluator_prompt() | evaluator_llm | evaluator_parser
    result = await chain.ainvoke(
        {
            "topic": state["topic"],
            "our_position": state["our_position"],
            "their_position": state["their_position"],
            "history": _history_text(state["history"]),
        }
    )
    state["evaluator_decision"] = result
    state["agreement_reached"] = result.agreement_reached
    return state


def _route_negotiation(state: NegotiationState) -> str:
    if state["agreement_reached"] or state["rounds"] >= state["max_rounds"]:
        return "end"
    return "continue"


_nw = StateGraph(NegotiationState)
_nw.add_node("proposer", _node_proposer)
_nw.add_node("responder", _node_responder)
_nw.add_node("evaluator", _node_evaluator)
_nw.add_edge(START, "proposer")
_nw.add_edge("proposer", "responder")
_nw.add_edge("responder", "evaluator")
_nw.add_conditional_edges(
    "evaluator",
    _route_negotiation,
    {
        "continue": "proposer",
        "end": END,
    },
)
neg_graph = _nw.compile()


# =============================================================================
#  8. LEGAL PARSER LANGGRAPH
# =============================================================================
async def _node_legal_parse(state: LegalParseState) -> LegalParseState:
    chain = _build_legal_prompt() | legal_llm | legal_parser
    state["parse_result"] = await chain.ainvoke({"raw_email": state["raw_email"]})
    return state


_lw = StateGraph(LegalParseState)
_lw.add_node("parse", _node_legal_parse)
_lw.add_edge(START, "parse")
_lw.add_edge("parse", END)
legal_graph = _lw.compile()


# =============================================================================
#  9. ENDPOINTS
# =============================================================================
@router.post("/negotiate_email")
async def negotiate_email(request: NegotiationRequest):
    """
    [PERSON A] Runs a multi-agent email negotiation between two simulated parties.
    """
    result = await neg_graph.ainvoke(
        {
            "topic": request.topic,
            "our_position": request.our_position,
            "their_position": request.their_position,
            "category": request.category,
            "rounds": 0,
            "max_rounds": request.max_rounds,
            "history": [],
            "evaluator_decision": None,
            "agreement_reached": False,
        }
    )
    return {
        "topic": request.topic,
        "rounds_completed": result["rounds"],
        "agreement_reached": result["agreement_reached"],
        "summary": result["evaluator_decision"].summary
        if result["evaluator_decision"]
        else "Incomplete.",
        "email_thread": [
            {"role": e.role, "subject": e.subject, "body": e.body}
            for e in result["history"]
        ],
    }


@router.post("/parse_legal_email")
async def parse_legal_email(request: LegalParseRequest):
    """
    [PERSON B] Parses a legal or contract email and returns structured risk analysis.
    """
    result = await legal_graph.ainvoke(
        {
            "raw_email": request.raw_email,
            "parse_result": None,
        }
    )
    return result["parse_result"].model_dump()
