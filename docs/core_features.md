# Detailed Documentation: core_features.py (Developer 1 Domain)

This file manages the **Core Communication Logic**: Email Formalization, Translation, and Smart Replies.

---

## 1. Environment & API Key Guard (Best Practice)
In Python, any code at the top level (outside functions) is executed the moment the file is imported. Since we initialize LLM objects immediately, we MUST ensure the API key is present, or the app will crash with a confusing error.

```python
import os
from dotenv import load_dotenv

# 0. Load the .env file immediately
load_dotenv()

# Guard: Check if the key exists BEFORE initializing models
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY is missing. Check your .env file.")
```
- **Viva Point:** Mention that this is a "Guard Clause" for **Import-Time Initialization**. It provides a clear, human-readable error message if the environment is misconfigured.

---

## 2. LLM Configuration & Temperatures
We use the `ChatGroq` wrapper for the `openai/gpt-oss-120b` model.

```python
analyser_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.0)
business_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.4)
```
- **Temperature 0.0:** Used for the `analyser`. It must be deterministic (always gives the same output for the same input) to correctly detect categories.
- **Temperature 0.4:** Used for writing. It allows the model to vary its phrasing slightly for a more "human" feel while staying professional.

---

## 3. Pydantic Models (Type Safety)
Pydantic ensures that the LLM's output matches exactly what we expect.

```python
class AnalysisOutput(BaseModel):
    already_formal: bool = Field(description="True if the email is already formal")
    detected_category: Literal["business", "academic", "corporate", "unknown"]
    main_points: str = Field(description="Extracted or original main content")
```
- **Field Descriptions:** These strings are actually passed to the LLM by the `PydanticOutputParser` so the AI knows exactly what each field means.

---

## 4. LangGraph Workflow Routing
The logic behind how the email "moves" through the system.

```python
def _route_after_analysis(state: EmailState) -> str:
    a = state["analysis"]
    if a and a.already_formal and a.detected_category == state["category"]:
        return "return_direct"
    return state["category"]
```
- **Logic:** If the `already_formal` flag is True, we skip the writing nodes and jump straight to the output. This **saves tokens** and **reduces latency** for the user.

---

## 5. API Endpoint Implementation
The bridge to the frontend.

```python
@router.post("/formalize_email")
async def formalize_email(request: EmailRequest):
    result = await main_graph.ainvoke({
        "raw_email": request.raw_email,
        "category": request.category,
        "language": request.language or "english",
        # ... state ...
    })
    return {
        "category": request.category,
        "email": result["final_email"].model_dump(),
    }
```
- **`ainvoke`:** Stands for "Asynchronous Invoke." It allows the server to handle multiple users simultaneously without waiting (blocking) for the LLM to finish.
- **`model_dump()`:** Converts the Pydantic object into a JSON-friendly Python dictionary.
