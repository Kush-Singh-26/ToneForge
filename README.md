---
title: ToneForge AI
emoji: ⚡
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
---

# ToneForge AI 🚀

ToneForge AI is a sophisticated, minimalist AI-powered email assistant designed to elevate professional communication. It leverages high-performance LLMs via Groq and LangChain to provide formalization, translation, strategic negotiation, and legal analysis in a single, streamlined interface.

## 🌟 Core Features

### 1. ✍️ Formalize & Translate
Transform casual thoughts into polished, professional drafts. 
- **Context-Aware**: Choose between Business, Corporate, or Academic styles.
- **Multilingual**: Formalize and translate into any target language (Spanish, French, Hindi, etc.) in one step.

### 2. 🤖 Smart Reply
Generate intelligent, contextually relevant responses to incoming messages.
- Maintains the original conversation's thread and tone.
- Built-in tone profiles (Business, Corporate, Academic).

### 3. 🤝 Strategic Negotiation (Multi-Agent)
A complex simulation tool using **LangGraph** to model a back-and-forth negotiation between two AI agents:
- **Proposer**: Drafts emails representing your strategic position.
- **Responder**: Simulates the counterpart's realistic reactions and counter-proposals.
- **Evaluator**: A neutral agent that determines if an agreement is reached or suggests next steps.

### 4. ⚖️ Legal Parser
Deconstruct complex legal text or contract emails into structured intelligence.
- Extracts **Obligations** and **Deadlines**.
- Identifies **Risk Flags** (e.g., "indemnify", "irrevocable").
- Rates clauses by risk level (Low/Medium/High).
- Provides an **Executive Summary** in plain English.

---

## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Orchestration**: [LangChain](https://www.langchain.com/) & [LangGraph](https://python.langchain.com/docs/langgraph)
 - **LLM Infrastructure**: [Groq](https://groq.com/) (GPT 120B OSS)
- **Frontend**: HTML5, [Tailwind CSS](https://tailwindcss.com/), [Lucide Icons](https://lucide.dev/)
- **State Management**: Pydantic & TypedDict

---

## 🚀 Deployment

### 🐳 Hugging Face Spaces (Backend/Full-Stack)
This repository is configured to run as a Docker container on Hugging Face Spaces.
1. Create a new Space with the **Docker SDK**.
2. Add your `GROQ_API_KEY` to **Settings > Variables and secrets**.
3. Push this repo to the Space's remote.
4. Access the API documentation at `https://your-space-name.hf.space/docs`.

### ⚡ Vercel (Frontend Only)
You can host the frontend separately on Vercel for maximum performance.
1. Connect this GitHub repository to Vercel.
2. Vercel will automatically serve the root `index.html`.
3. The frontend is pre-configured to automatically route requests to the Hugging Face API when running on a non-HF domain.

---

## 💻 Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Variables**:
   Create a `.env` file and add:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```
3. **Run the Server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
4. **Open in Browser**:
   `http://localhost:8000`

---

## 📜 License
MIT License. Built with ❤️ for professional efficiency.
