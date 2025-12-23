import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise SystemExit("❌ Missing GOOGLE_API_KEY in .env")

client = genai.Client(api_key=api_key)

# Use a common model name; if it errors, list models (next step).
model = "gemini-2.0-flash"

resp = client.models.generate_content(
    model=model,
    contents="Hello! Are you ready to help me cook?"
)

print(resp.text)
