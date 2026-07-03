import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Gemini API key is not configured.")
    raise SystemExit(0)

client = genai.Client(api_key=api_key)

for model in client.models.list():
    name = getattr(model, "name", "")
    supported_actions = getattr(model, "supported_actions", [])

    if "generateContent" in supported_actions or not supported_actions:
        print(name)