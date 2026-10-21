import os
from pathlib import Path
from typing import Literal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Project root (one level up from backend/), so the server works from any working directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the .env file in the project root
load_dotenv(ROOT_DIR / ".env")

app = FastAPI(title="iGEM CareBot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class HistoryTurn(BaseModel):
    role: Literal["user", "bot"]
    text: str

class ChatMessage(BaseModel):
    message: str
    history: list[HistoryTurn] = []

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
client = genai.Client(api_key=api_key) if api_key else None

# Only the most recent turns are sent back to Gemini, to keep requests small
MAX_HISTORY_TURNS = 20

# Strict System Instruction for the AI Persona and Safety Router
system_instruction = """
You are CareBot, an empathetic and supportive informational guide created by an iGEM team to help burn patients with scarring recovery.
You provide general information about scar types, healing timelines, and coping strategies based on standard guidelines.

CRITICAL SAFETY & BEHAVIOR RULES:
1. You are NOT a doctor or a therapist.
2. MEDICAL/CRISIS HANDOFF: If the user asks for a specific medical diagnosis, expresses severe physical pain/infection, or asks about self-harm, suicide, severe depression, or overwhelming shame/feeling ugly, you MUST immediately hand off the conversation by replying with EXACTLY and ONLY this phrase: HANDOFF_REQUIRED
3. DANGEROUS/ILLEGAL QUERIES: If the user asks a dangerous or illegal question (e.g., "how do I make a bomb", violence, etc.), respond with: "I cannot fulfill this request. My purpose is to provide support and information regarding scar recovery and burn care."
4. OFF-TOPIC/SHORT INPUTS: If the input is extremely short (e.g., "mushrooms", "hello") or unrelated to scars/burns, politely ask for clarification and gently remind them that your purpose is to support scar recovery, but they can find other information elsewhere online.
5. CONCISENESS & FORMATTING: Keep your responses short and concise (1-2 paragraphs max). Use markdown bolding VERY sparingly. ONLY bold important **Dates**, **Names of Organizations/Societies**, and **Specific Locations**. Do NOT bold general medical terms, conversational words, or scar-related words.
6. INTERACTIVE MAP: If the user explicitly asks to find a burn center, hospital, or support group in a specific region, you MUST append the exact tag `[SHOW_MAP: Region Name | FILTER]` at the very end of your response.
   - If they specifically ask for community support, survivor programs, or Phoenix SOAR, use the filter `SOAR`. (e.g., `[SHOW_MAP: Texas | SOAR]`)
   - If they ask for medical care, doctors, or general burn centers, use the filter `ALL`. (e.g., `[SHOW_MAP: Chicago | ALL]`)
"""

# Serve the index.html at the root URL
@app.get("/")
async def root():
    return FileResponse(ROOT_DIR / "index.html")

@app.post("/api/chat")
async def chat_endpoint(request: ChatMessage):
    if not client:
        return {
            "status": "success",
            "reply": "The backend is running, but the GEMINI_API_KEY is not set in the .env file. Please add it to test the AI!"
        }

    # Rebuild the conversation so follow-up questions have context
    contents = [
        types.Content(
            role="model" if turn.role == "bot" else "user",
            parts=[types.Part(text=turn.text)]
        )
        for turn in request.history[-MAX_HISTORY_TURNS:]
    ]
    contents.append(types.Content(role="user", parts=[types.Part(text=request.message)]))

    try:
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )
        reply_text = (response.text or "").strip()

        # Check if the AI decided to trigger the safety handoff
        if "HANDOFF_REQUIRED" in reply_text:
            return {
                "status": "handoff",
                "reply": "HANDOFF_REQUIRED"
            }

        return {
            "status": "success",
            "reply": reply_text
        }

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {
            "status": "success",
            "reply": "I'm sorry, I'm having trouble connecting to my AI brain right now."
        }

# Serve only the files the page needs (not .env or the scripts)
def file_route(path: Path):
    async def serve():
        return FileResponse(path)
    return serve

for public_file in ["style.css", "script.js", "hospitals.json"]:
    app.add_api_route(
        f"/{public_file}",
        file_route(ROOT_DIR / public_file),
        methods=["GET"],
        include_in_schema=False
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", "8000")))
