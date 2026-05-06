"""
RADAR Multi-Provider LLM Client 🤖⚡
===================================
A resilient wrapper that manages multiple LLM providers (Gemini, Groq).
It uses environment variables for keys and fallbacks automatically.
"""

import os
from typing import Optional
try:
    from dotenv import load_dotenv
    # Load .env from the root of the project (one level up from brain/)
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    load_dotenv(env_path)
except ImportError:
    pass

# --- Provider SDKs ---
try:
    from google import genai
    from google.genai import types as genai_types
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

import requests  # Used for Groq (OpenAI-compatible REST API)

class LLMClient:
    def __init__(self):
        # Load keys from environment (configured in .env)
        self.gemini_key = os.getenv("GOOGLE_API_KEY")
        self.groq_key   = os.getenv("GROQ_API_KEY")
        
        self.groq_model = "llama-3.3-70b-versatile"

    def generate_content(self, prompt: str, system_instruction: str = "") -> str:
        """
        Attempt to generate content.
        Strategy: 
        1. Try the configured Gemini key.
        2. If Gemini fails (429/Exhausted), fallback to Groq.
        """
        
        # --- Stage 1: Try Gemini ---
        if HAS_GEMINI and self.gemini_key:
            try:
                client = genai.Client(api_key=self.gemini_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash-lite",
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    )
                )
                return response.text.strip()
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    print(f"[LLM] Gemini Key exhausted. Falling back to GROQ...")
                else:
                    print(f"[LLM] Gemini unexpected error: {e}. Falling back to GROQ...")

        # --- Stage 2: Fallback to Groq ---
        if self.groq_key:
            print(f"[LLM] Switching to GROQ Fallback ({self.groq_model})...")
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json"
                }
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                
                payload = {
                    "model": self.groq_model,
                    "messages": messages,
                    "temperature": 0.2
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
                
            except Exception as e:
                print(f"[LLM] Groq failed: {e}")

        # --- Stage 3: Fallback to Ollama (Local) ---
        print("[LLM] Switching to Local OLLAMA Fallback...")
        try:
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "llama3", # Defaulting to llama3, can be changed in .env
                "prompt": f"{system_instruction}\n\n{prompt}" if system_instruction else prompt,
                "stream": False
            }
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            return f"[ERROR] All LLM providers (Gemini, Groq, Ollama) failed. Last error: {e}"
        
        return "[ERROR] No LLM providers configured (missing keys)."

# Simple test runner
if __name__ == "__main__":
    # Note: In a real run, the environment variables would be loaded via dotenv
    # but for this test we assume they are already in the environment.
    client = LLMClient()
    test_prompt = "Say 'RADAR Resilience Layer: ONLINE'"
    print(f"Testing LLM Resilience Layer...")
    result = client.generate_content(test_prompt)
    print(f"\nFinal Result:\n{result}")
