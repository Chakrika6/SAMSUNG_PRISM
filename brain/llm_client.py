import os
import json
import time
from google import genai
from groq import Groq
from pydantic import BaseModel
from typing import Type, TypeVar, Optional, List

T = TypeVar("T", bound=BaseModel)

class LLMClient:
    def __init__(self):
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
    def generate_json(self, prompt: str, schema: Type[T], system_instruction: str = "") -> Optional[T]:
        """
        Attempts to generate structured JSON using Gemini 2.0 Flash, 
        falling back to Groq Llama 3.3 if needed.
        """
        
        # 1. Try Gemini
        if self.google_key:
            try:
                print("   [LLM] Attempting Gemini 2.0 Flash...")
                client = genai.Client(api_key=self.google_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": schema,
                        "system_instruction": system_instruction
                    }
                )
                return schema.model_validate_json(response.text)
            except Exception as e:
                print(f"   [WARN] Gemini failed: {e}")

        # 2. Try Groq Fallback
        if self.groq_key:
            try:
                print("   [LLM] Switching to Groq Llama-3.3 Fallback...")
                client = Groq(api_key=self.groq_key)
                
                # Groq doesn't support response_schema directly, so we append it to the prompt
                full_prompt = f"{system_instruction}\n\n{prompt}\n\nReturn a JSON object matching this schema: {json.dumps(schema.model_json_schema())}"
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": full_prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                return schema.model_validate_json(chat_completion.choices[0].message.content)
            except Exception as e:
                print(f"   [WARN] Groq failed: {e}")

        print("   [ERROR] All LLM providers failed.")
        return None
