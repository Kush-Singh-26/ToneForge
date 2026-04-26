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

load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY is missing. Ensure it is defined in your .env file.")

router = APIRouter()

analyser_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.0)
business_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.4)
academic_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.4)
corporate_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.4)
translator_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)
reply_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.5)

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

analysis_parser = PydanticOutputParser(pydantic_object=AnalysisOutput)
email_parser = PydanticOutputParser(pydantic_object=StructuredEmail)
translated_parser = PydanticOutputParser(pydantic_object=TranslatedEmail)
reply_parser = PydanticOutputParser(pydantic_object=SmartReplyOutput)

def _escape_fmt(parser: PydanticOutputParser) -> str:
    """Escape curly braces in format instructions for f-string safety."""
    return parser.get_format_instructions().replace("{", "{{").replace("}", "}}")

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

analysis_prompt = _build_analysis_prompt()


async def _node_analyze(state: EmailState) -> EmailState:
    chain = analysis_prompt | analyser_llm | analysis_parser
    state["analysis"] = await chain.ainvoke({"raw_email": state["raw_email"]})
    return state


def _route_after_analysis(state: EmailState) -> str:
    a = state["analysis"]
    if a and a.already_formal and a.detected_category == state["category"]:
        return "return_direct"
    return state["category"]


def _node_return_direct(state: EmailState) -> EmailState:
    a = state["analysis"]
    if not a:
        return state
    state["final_email"] = StructuredEmail(
        subject="(Original Subject Preserved)",
        sender="(Original Sender)",
        to="(Original Receiver)",
        cc=None,
        body=a.main_points,
    )
    return state


async def _node_business(state: EmailState) -> EmailState:
    a = state["analysis"]
    if not a:
        return state
    chain = (
        _build_email_prompt("Business", BUSINESS_TEMPLATE) | business_llm | email_parser
    )
    state["final_email"] = await chain.ainvoke({"main_points": a.main_points})
    return state


async def _node_academic(state: EmailState) -> EmailState:
    a = state["analysis"]
    if not a:
        return state
    chain = (
        _build_email_prompt("Academic", ACADEMIC_TEMPLATE) | academic_llm | email_parser
    )
    state["final_email"] = await chain.ainvoke({"main_points": a.main_points})
    return state


async def _node_corporate(state: EmailState) -> EmailState:
    a = state["analysis"]
    if not a:
        return state
    chain = (
        _build_email_prompt("Corporate", CORPORATE_TEMPLATE)
        | corporate_llm
        | email_parser
    )
    state["final_email"] = await chain.ainvoke({"main_points": a.main_points})
    return state


async def _node_translate(state: EmailState) -> EmailState:
    fe = state["final_email"]
    if not fe:
        return state
    target = (state.get("language") or "english").strip().lower()
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

@router.post("/formalize_email")
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


@router.post("/generate_reply")
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
