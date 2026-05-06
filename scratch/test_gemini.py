import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
try:
    response = model.generate_content("Say hello")
    print(f"RESPONSE: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")
