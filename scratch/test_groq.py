import urllib.request
import json

API_KEY = "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"

data = json.dumps({
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 20
}).encode()

req = urllib.request.Request(
    "https://api.groq.com/openai/v1/chat/completions",
    data=data,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
        print("SUCCESS:", result["choices"][0]["message"]["content"])
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"ERROR {e.code}: {body[:500]}")
except Exception as e:
    print(f"ERROR: {e}")
