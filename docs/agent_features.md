# Detailed Documentation: agent_features.py (Developer 2 Domain)

This file manages the **Specialized AI Agents**: Multi-Agent Negotiation and the Legal Parser.

---

## 1. Environment & API Key Guard (Best Practice)
At the top of the file, we handle environment loading and an API key guard.

```python
import os
from dotenv import load_dotenv

# 0. Load the .env file immediately
load_dotenv()

# Guard: Check if the key exists BEFORE initializing models
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY is missing. Check your .env file.")
```
- **Viva Point:** This check ensures the LLM's constructor (which will look for the key) doesn't fail with a confusing error message later in the code.

---

## 2. Multi-Agent System Roles & Temperatures
We use the state-of-the-art **Llama 3.3 70B** model for these tasks due to the high reasoning requirements of negotiation and legal analysis.

```python
# Negotiation and Legal require high reasoning - using the 70B versatile model
proposer_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)
responder_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.6)
evaluator_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
legal_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
```
- **Llama 3.3 70B (Versatile):** This model is the best-in-class for Groq's current stack, providing GPT-4 level reasoning which is essential for multi-agent logic.
- **Proposer & Responder:** Higher temperatures (`0.5-0.6`) allow for dynamic negotiation and creative counter-offers.
- **Evaluator & Legal:** Set to `0.0` for maximum precision. These agents MUST be objective and never "hallucinate" or vary their logic.

---

## 3. The Cyclic Multi-Agent Graph
This is the **Cyclic Logic** that makes the agents talk to each other.

```python
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
```
- **Step 1:** The `proposer` makes an offer on our behalf.
- **Step 2:** The `responder` simulates the other party, countering or accepting.
- **Step 3:** The `evaluator` (the "referee") looks at the thread and decides if terms are agreed upon.
- **Step 4:** `_route_negotiation` (the loop brain) repeats the process unless agreement is reached or the `max_rounds` limit is hit.

---

## 4. Legal Document Parser
This feature uses a highly detailed Pydantic model to extract structured data from complex legal text.

```python
class LegalParseOutput(BaseModel):
    obligations: list[str] = Field(description="Explicit duties/commitments found")
    deadlines: list[str] = Field(description="Dates, deadlines, or time constraints")
    clauses: list[LegalClause] = Field(
        description="Identified legal clauses with risk levels"
    )
    risk_flags: list[str] = Field(description="High-risk words or phrases")
    overall_risk: Literal["low", "medium", "high"] = Field(
        description="Overall legal risk rating"
    )
    plain_summary: str = Field(description="Plain-English explanation of commitments")
```
- **Viva Point:** This model forces the LLM to output structured risk data. Notice how `overall_risk` is constrained to a `Literal` of only three values, ensuring consistent data for our frontend UI.

---

## 5. API Endpoint Implementation
The bridge between HTTP and the AI graphs.

```python
@router.post("/negotiate_email")
async def negotiate_email(request: NegotiationRequest):
    result = await neg_graph.ainvoke({
        "topic": request.topic,
        "our_position": request.our_position,
        "their_position": request.their_position,
        "category": request.category,
        "rounds": 0,
        "max_rounds": request.max_rounds,
        "history": [],
        "evaluator_decision": None,
        "agreement_reached": False,
    })
    return {
        "topic": request.topic,
        "rounds_completed": result["rounds"],
        "agreement_reached": result["agreement_reached"],
        "summary": result["evaluator_decision"].summary,
        "email_thread": [
            {"role": e.role, "subject": e.subject, "body": e.body}
            for e in result["history"]
        ],
    }
```
- **Asynchronous Execution:** Like the formalizer, this uses `ainvoke` so that long negotiation loops don't block the entire server.
- **Summary Retrieval:** Notice the check: `result["evaluator_decision"].summary` extracts the final verdict from the referee agent.

---

## 6. Available Tasks & Functional Logic

### **A. Multi-Agent Negotiation Simulation**
**Purpose:** Helps users practice or simulate a difficult email negotiation before sending actual mail.
- **Proposer Agent:** Acts as the user's advocate. It tries to achieve the user's "Our Position" using persuasive but professional language.
- **Responder Agent:** Simulates the other party. It acts realistically—rejecting unfair offers and suggesting compromises.
- **Evaluator Agent:** Acts as the "Referee." It reads the back-and-forth history and identifies when an agreement has been reached, providing a final summary of the agreed terms.

### **B. Legal & Contract Parser**
**Purpose:** Simplifies "legalese" and identifies hidden risks in contracts.
- **Risk Scorecard:** Identifies "Risk Flags" like *indemnification*, *irrevocability*, or *sole discretion* that might be dangerous for a user.
- **Commitment Extraction:** Clearly lists all **Obligations** (what you MUST do) and **Deadlines** (WHEN you must do it).
- **Plain Summary:** Translates complex legal clauses into 2-3 simple English sentences so anyone can understand what they are signing.
