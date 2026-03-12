# Detailed Documentation: main.py (The Entry Point)

This file is the **central hub** of the application. It manages the server lifecycle, global security, and integrates the modular feature sets.

---

## 1. Environment and Security Initialization
At the very top of the file, we handle environment variables. This is critical because the subsequent imports of `core_features` and `agent_features` immediately initialize LLM objects that require an API key.

```python
import os
from dotenv import load_dotenv

# Load environment variables BEFORE importing local modules
load_dotenv()
```
- **Line 5:** `load_dotenv()` reads the `.env` file. We do this *before* importing our routers (Lines 13-14) so that those modules find the `GROQ_API_KEY` in the environment the moment they are loaded.

---

## 2. FastAPI Application Instance
We define the app and its metadata, which powers the auto-generated documentation.

```python
app = FastAPI(
    title="ToneForgeAI",
    description=(
        "AI-powered email assistant: formalize, translate, reply, "
        "negotiate, and parse legal emails."
    ),
)
```
- **`app`:** The global instance that registers all routes and middleware.
- **Swagger UI:** By visiting `http://localhost:8000/docs`, you can see this description and test every endpoint interactively.

---

## 3. Global Middleware (CORS)
Security logic to allow frontend-backend communication.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
- **CORS:** Cross-Origin Resource Sharing. 
- **Line 26:** `allow_origins=["*"]` allows any frontend (regardless of port or domain) to send requests. Without this, browsers block API calls for security.

---

## 4. Static Files and Main UI
The backend also serves as the web server for the frontend.

```python
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
```
- **Line 33:** `app.mount` maps the local `static/` folder to the `/static` URL path. This is how the browser loads `app.js` and `styles.css`.
- **Line 36:** The root route (`/`) simply reads and returns your `index.html` file as the homepage.

---

## 5. Module Integration (The Routers)
This is the core of the modular architecture designed to prevent merge conflicts.

```python
# Include the routers from our split files
app.include_router(core_router)
app.include_router(agent_router)
```
- **Lines 43-44:** Instead of writing logic here, we "mount" the routers from the other two files. This allows Developer 1 and Developer 2 to build independently in their own files without touching `main.py`.
