# =============================================================================
#  ToneForgeAI  —  main.py
#  Full backend with 4 endpoints across original + 2 new feature owners
#
#  ENDPOINT SUMMARY
#  ─────────────────────────────────────────────────────────────────────────
#  POST /formalize_email     → Original feature (polish email + translate)
#  POST /generate_reply      → Original feature (smart reply generator)
#  POST /negotiate_email     → PERSON A  (multi-agent negotiator)
#  POST /parse_legal_email   → PERSON B  (contract / legal email parser)
# =============================================================================

import json
import os
from typing import Literal, Optional
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing import TypedDict

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI(
    title="ToneForgeAI",
    description=(
        "AI-powered email assistant: formalize, translate, reply, "
        "negotiate, and parse legal emails."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


# =============================================================================
#  1. LLM INSTANCES
# =============================================================================

# — Core (original) —
analyser_llm = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0.0, groq_api_key=GROQ_API_KEY
)
business_llm = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0.4, groq_api_key=GROQ_API_KEY
)
academic_llm = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0.4, groq_api_key=GROQ_API_KEY
)
corporate_llm = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0.4, groq_api_key=GROQ_API_KEY
)
translator_llm = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0.2, groq_api_key=GROQ_API_KEY
)
reply_llm = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0.5, groq_api_key=GROQ_API_KEY
)

# — PERSON A: Multi-Agent Negotiator —
proposer_llm = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0.5, groq_api_key=GROQ_API_KEY
)
responder_llm = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0.6, groq_api_key=GROQ_API_KEY
)
evaluator_llm = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0.0, groq_api_key=GROQ_API_KEY
)

# — PERSON B: Legal Parser —
legal_llm = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0.0, groq_api_key=GROQ_API_KEY
)


# =============================================================================
#  2. PYDANTIC MODELS
# =============================================================================


# — Core models —
class AnalysisOutput(BaseModel):
    already_formal: bool = Field(description="True if the email is already formal")
    detected_category: Literal["business", "academic", "corporate", "unknown"]
    main_points: str = Field(description="Extracted or original main content")


class StructuredEmail(BaseModel):
    subject: str
    sender: str
    to: str
    cc: Optional[str]
    body: str


class TranslatedEmail(BaseModel):
    subject: str
    sender: str
    to: str
    cc: Optional[str]
    body: str
    language: str = Field(description="Language this email was translated into")


class SmartReplyOutput(BaseModel):
    subject: str = Field(description="Reply subject prefixed with Re:")
    sender: str
    to: str
    body: str = Field(description="Fully composed reply email body")


# — PERSON A models —
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


# — PERSON B models —
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


# =============================================================================
#  3. STATE TYPEDDICTS
# =============================================================================


class EmailState(TypedDict):
    raw_email: str
    category: Literal["business", "academic", "corporate"]
    language: Optional[str]
    analysis: Optional[AnalysisOutput]
    final_email: Optional[StructuredEmail]
    translated_email: Optional[TranslatedEmail]


class ReplyState(TypedDict):
    original_email: str
    category: Literal["business", "academic", "corporate"]
    smart_reply: Optional[SmartReplyOutput]


# PERSON A
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


# PERSON B
class LegalParseState(TypedDict):
    raw_email: str
    parse_result: Optional[LegalParseOutput]


# =============================================================================
#  4. PARSERS
# =============================================================================

analysis_parser = PydanticOutputParser(pydantic_object=AnalysisOutput)
email_parser = PydanticOutputParser(pydantic_object=StructuredEmail)
translated_parser = PydanticOutputParser(pydantic_object=TranslatedEmail)
reply_parser = PydanticOutputParser(pydantic_object=SmartReplyOutput)
negotiation_parser = PydanticOutputParser(pydantic_object=NegotiationEmail)  # PERSON A
evaluator_parser = PydanticOutputParser(pydantic_object=EvaluatorDecision)  # PERSON A
legal_parser = PydanticOutputParser(pydantic_object=LegalParseOutput)  # PERSON B


# =============================================================================
#  5. SHARED HELPERS
# =============================================================================


def _escape_fmt(parser: PydanticOutputParser) -> str:
    """Escape curly braces in format instructions for f-string safety."""
    return parser.get_format_instructions().replace("{", "{{").replace("}", "}}")


# =============================================================================
#  6. EMAIL STYLE TEMPLATES  (shared across core + PERSON A)
# =============================================================================

BUSINESS_TEMPLATE = """
Business Email Structure Guidelines:
- Subject: Clear, concise, action-oriented.
- Body must:
    • Begin with: Dear [Receiver Name],
    • State purpose in first paragraph.
    • Include supporting explanation.
    • End with a call to action.
    • Close with: Sincerely, [Sender Name]
Tone: Professional, concise, polite, results-driven.
"""

ACADEMIC_TEMPLATE = """
Academic Email Structure Guidelines:
- Subject: Specific, academic-focused.
- Body must:
    • Begin with: Dear Professor/Dr. [Last Name],
    • Include polite opening line.
    • Mention course/research context.
    • Clearly state request.
    • Close with: Best regards, [Full Name + Institution]
Tone: Respectful, formal, academic.
"""

CORPORATE_TEMPLATE = """
Corporate Email Structure Guidelines:
- Subject: Project/update oriented.
- Body must:
    • Begin with: Hello [Recipient/Team],
    • Clearly explain update or issue.
    • Provide structured information.
    • Mention next steps or deadlines.
    • Close with: Kind regards, [Name + Designation + Company]
Tone: Professional, structured, direct.
"""

TEMPLATE_MAP = {
    "business": BUSINESS_TEMPLATE,
    "academic": ACADEMIC_TEMPLATE,
    "corporate": CORPORATE_TEMPLATE,
}


# =============================================================================
#  7. PROMPT BUILDERS
# =============================================================================


# — Core —
def _build_analysis_prompt() -> ChatPromptTemplate:
    fmt = _escape_fmt(analysis_parser)
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
You are an intelligent email analyzer.
1. Determine if the email is already formal.
2. Detect its category: business | academic | corporate | unknown.
3. If already formal keep content unchanged; otherwise extract main points.
Return ONLY JSON.\n{fmt}
""",
            ),
            ("human", "{raw_email}"),
        ]
    )


def _build_email_prompt(style: str, template: str) -> ChatPromptTemplate:
    fmt = _escape_fmt(email_parser)
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
You are an expert {style} email writer. STRICTLY follow:
{template}
Use the provided main points to generate the email. Return ONLY JSON.\n{fmt}
""",
            ),
            ("human", "{main_points}"),
        ]
    )


def _build_translation_prompt() -> ChatPromptTemplate:
    fmt = _escape_fmt(translated_parser)
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
You are a professional email translator.
Translate every field into the target language preserving tone and formality.
Keep proper nouns unchanged. Set "language" to the target language.
Return ONLY JSON.\n{fmt}
""",
            ),
            (
                "human",
                "Target language: {target_language}\n\nEmail JSON:\n{email_json}",
            ),
        ]
    )


def _build_reply_prompt(style: str, template: str) -> ChatPromptTemplate:
    fmt = _escape_fmt(reply_parser)
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
You are an expert {style} email reply writer. STRICTLY follow:
{template}
Subject must start with "Re: ". Return ONLY JSON.\n{fmt}
""",
            ),
            ("human", "Original email:\n{original_email}"),
        ]
    )


# — PERSON A —
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


# — PERSON B —
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
#  8. ORIGINAL LANGGRAPH  —  /formalize_email + /generate_reply
# =============================================================================

analysis_prompt = _build_analysis_prompt()


async def _node_analyze(state: EmailState) -> EmailState:
    chain = analysis_prompt | analyser_llm | analysis_parser
    state["analysis"] = await chain.ainvoke({"raw_email": state["raw_email"]})
    return state


def _route_after_analysis(state: EmailState) -> str:
    a = state["analysis"]
    if a.already_formal and a.detected_category == state["category"]:
        return "return_direct"
    return state["category"]


def _node_return_direct(state: EmailState) -> EmailState:
    a = state["analysis"]
    state["final_email"] = StructuredEmail(
        subject="(Original Subject Preserved)",
        sender="(Original Sender)",
        to="(Original Receiver)",
        cc=None,
        body=a.main_points,
    )
    return state


async def _node_business(state: EmailState) -> EmailState:
    chain = (
        _build_email_prompt("Business", BUSINESS_TEMPLATE) | business_llm | email_parser
    )
    state["final_email"] = await chain.ainvoke(
        {"main_points": state["analysis"].main_points}
    )
    return state


async def _node_academic(state: EmailState) -> EmailState:
    chain = (
        _build_email_prompt("Academic", ACADEMIC_TEMPLATE) | academic_llm | email_parser
    )
    state["final_email"] = await chain.ainvoke(
        {"main_points": state["analysis"].main_points}
    )
    return state


async def _node_corporate(state: EmailState) -> EmailState:
    chain = (
        _build_email_prompt("Corporate", CORPORATE_TEMPLATE)
        | corporate_llm
        | email_parser
    )
    state["final_email"] = await chain.ainvoke(
        {"main_points": state["analysis"].main_points}
    )
    return state


async def _node_translate(state: EmailState) -> EmailState:
    target = (state.get("language") or "english").strip().lower()
    fe = state["final_email"]
    if target == "english":
        state["translated_email"] = TranslatedEmail(
            **fe.model_dump(), language="English"
        )
        return state
    chain = _build_translation_prompt() | translator_llm | translated_parser
    state["translated_email"] = await chain.ainvoke(
        {
            "target_language": target,
            "email_json": json.dumps(fe.model_dump()),
        }
    )
    return state


_wf = StateGraph(EmailState)
_wf.add_node("analyze", _node_analyze)
_wf.add_node("return_direct", _node_return_direct)
_wf.add_node("business", _node_business)
_wf.add_node("academic", _node_academic)
_wf.add_node("corporate", _node_corporate)
_wf.add_node("translate", _node_translate)
_wf.add_edge(START, "analyze")
_wf.add_conditional_edges(
    "analyze",
    _route_after_analysis,
    {
        "return_direct": "return_direct",
        "business": "business",
        "academic": "academic",
        "corporate": "corporate",
    },
)
for _n in ("return_direct", "business", "academic", "corporate"):
    _wf.add_edge(_n, "translate")
_wf.add_edge("translate", END)
main_graph = _wf.compile()


# Reply graph
async def _node_reply(state: ReplyState) -> ReplyState:
    prompt = _build_reply_prompt(
        state["category"].capitalize(),
        TEMPLATE_MAP[state["category"]],
    )
    chain = prompt | reply_llm | reply_parser
    state["smart_reply"] = await chain.ainvoke(
        {"original_email": state["original_email"]}
    )
    return state


_rw = StateGraph(ReplyState)
_rw.add_node("reply", _node_reply)
_rw.add_edge(START, "reply")
_rw.add_edge("reply", END)
reply_graph = _rw.compile()


# =============================================================================
#  9. PERSON A — NEGOTIATION LANGGRAPH  —  /negotiate_email
#
#  Flow:
#  START → proposer → responder → evaluator
#              ↑                       │
#              └───────────────────────┘  loop (no agreement & rounds left)
#                                         END when agreement reached OR max_rounds hit
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
#  10. PERSON B — LEGAL PARSER LANGGRAPH  —  /parse_legal_email
#
#  Flow:  START → legal_parse → END
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
#  11. REQUEST SCHEMAS
# =============================================================================


class EmailRequest(BaseModel):
    raw_email: str
    category: Literal["business", "academic", "corporate"]
    language: Optional[str] = Field(
        default="english",
        description="Target output language. Omit or pass 'english' to skip translation.",
    )


class ReplyRequest(BaseModel):
    original_email: str = Field(description="The incoming email you want to reply to.")
    category: Literal["business", "academic", "corporate"]


# PERSON A
class NegotiationRequest(BaseModel):
    topic: str = Field(description="What is being negotiated")
    our_position: str = Field(description="Your desired outcome")
    their_position: str = Field(description="The other party's stated position")
    category: Literal["business", "corporate"]
    max_rounds: int = Field(
        default=3, ge=1, le=6, description="Back-and-forth rounds (1-6)"
    )


# PERSON B
class LegalParseRequest(BaseModel):
    raw_email: str = Field(
        description="Full text of the legal/contract email to analyse."
    )


# =============================================================================
#  12. ENDPOINTS
# =============================================================================


@app.post("/formalize_email")
async def formalize_email(request: EmailRequest):
    """
    Rewrites a raw email in the chosen professional tone.
    Optionally translates the result if `language` is provided (e.g. "French", "Hindi").
    """
    result = await main_graph.ainvoke(
        {
            "raw_email": request.raw_email,
            "category": request.category,
            "language": request.language or "english",
            "analysis": None,
            "final_email": None,
            "translated_email": None,
        }
    )
    response = {
        "category": request.category,
        "email": result["final_email"].model_dump(),
    }
    if (request.language or "english").strip().lower() != "english":
        response["translated_email"] = result["translated_email"].model_dump()
    return response


@app.post("/generate_reply")
async def generate_reply(request: ReplyRequest):
    """
    Generates a polished, tone-matched reply to an incoming email.
    """
    result = await reply_graph.ainvoke(
        {
            "original_email": request.original_email,
            "category": request.category,
            "smart_reply": None,
        }
    )
    return {
        "category": request.category,
        "smart_reply": result["smart_reply"].model_dump(),
    }


# ── PERSON A ──────────────────────────────────────────────────────────────────
@app.post("/negotiate_email")
async def negotiate_email(request: NegotiationRequest):
    """
    [PERSON A] Runs a multi-agent email negotiation between two simulated parties.

    Three AI agents collaborate in a loop:
    - Proposer  — drafts emails representing your side
    - Responder — simulates the other party's realistic replies
    - Evaluator — decides if agreement is reached; guides concessions if not

    Loops until agreement OR max_rounds exhausted.
    Returns the full email thread + final agreement summary.
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


# ── PERSON B ──────────────────────────────────────────────────────────────────
@app.post("/parse_legal_email")
async def parse_legal_email(request: LegalParseRequest):
    """
    [PERSON B] Parses a legal or contract email and returns structured risk analysis.

    Extracts:
    - obligations  — explicit duties either party must fulfil
    - deadlines    — all time-based constraints
    - clauses      — identified legal clause types, each rated low/medium/high risk
    - risk_flags   — specific high-risk words or phrases
    - overall_risk — low | medium | high
    - plain_summary — plain-English explanation of what the email commits to
    """
    result = await legal_graph.ainvoke(
        {
            "raw_email": request.raw_email,
            "parse_result": None,
        }
    )
    return result["parse_result"].model_dump()
