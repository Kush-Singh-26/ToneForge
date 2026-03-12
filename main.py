import os
from dotenv import load_dotenv

# Load environment variables BEFORE importing local modules
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from core_features import router as core_router
from agent_features import router as agent_router

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


# Include the routers from our split files
app.include_router(core_router)
app.include_router(agent_router)
