import os
from pathlib import Path
from google import genai
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found")
else:
    client = genai.Client(api_key=api_key)
    try:
        print("Available models for this API key:")
        for m in client.models.list():
            if 'generateContent' in (m.supported_actions or []):
                print(m.name)
    except Exception as e:
        print(f"Error fetching models: {e}")
