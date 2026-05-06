import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Testing key: {api_key[:10]}...")

client = genai.Client(api_key=api_key)
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello, are you alive?"
    )
    print("Gemini Response:", response.text)
except Exception as e:
    print("Gemini Error:", e)
