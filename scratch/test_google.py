import urllib.request
import json

API_KEY = "AIzaSyCrlX2nREKHzFs9wHxB4g_7_X9wclzHiYQ"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

data = json.dumps({
    "contents": [{"parts": [{"text": "Say hello in one sentence"}]}]
}).encode()

req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
        print("SUCCESS:", result["candidates"][0]["content"]["parts"][0]["text"])
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"ERROR {e.code}: {body[:300]}")
except Exception as e:
    print(f"ERROR: {e}")
