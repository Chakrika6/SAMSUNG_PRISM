import urllib.request
import json

API_KEY = "89ca3afd7d2596befd85ef6fa539f307"
BASE_URL = "https://api.bytez.com/models/v2/openai/chat/completions"

data = json.dumps({
    "model": "openai/gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say hello in one sentence"}],
    "max_tokens": 50
}).encode()

req = urllib.request.Request(
    BASE_URL,
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
