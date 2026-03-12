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
We use specialized **Groq models** optimized for different stages of the pipeline.

```python
# Using specialized models for speed and quality
analyser_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
business_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.4)
```
- **Llama 3.1 8B (Instant):** Used for the `analyser`. It is incredibly fast and efficient for classification and extraction tasks.
- **Llama 3.3 70B (Versatile):** Used for the generative writing and translation tasks. It has higher reasoning capabilities and handles multilingual nuance far better than smaller models.
- **Temperature 0.0:** Used for the `analyser` to ensure deterministic classification.
- **Temperature 0.4:** Used for writing to balance professional consistency with human-like phrasing.

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

---

## 6. Available Tasks & Functional Logic

### **A. Email Formalizer (Rewrite Task)**
**Purpose:** Transforms informal, messy, or "brain-dump" notes into structured, professional emails.
- **Analysis Node:** The system first identifies the "Main Points" (who is involved, what is requested, what is the deadline).
- **Style Injection:** Depending on the category (Business/Academic/Corporate), the AI applies a rigid structural template.
- **Edge Case Handling:** If the email is already formal, the AI recognizes this and preserves the original content to avoid over-processing.

### **B. Smart Reply Generator**
**Purpose:** Context-aware reply generation based on the thread's history.
- **Context Awareness:** Instead of a generic "Thanks," the AI reads the incoming message and crafts a specific response addressing the points raised.
- **Tone Matching:** Ensures the reply matches the professional category chosen by the user.

### **C. Professional Translator**
**Purpose:** High-fidelity translation that preserves professional nuance.
- **Tone Preservation:** Unlike standard translators that might lose formality, this task specifically instructs the AI to maintain "Business Formal" or "Academic Respectful" tones in the target language.
- **Entity Protection:** Proper nouns, company names, and technical terms are preserved as-is.
