import urllib.request, json

KEY = "AIzaSyA2QgAdSUPvOxtScOAoGd1UJ4O5O-culrQ"

for model in ["gemini-2.5-flash", "gemini-2.5-pro", "gemma-4-26b-a4b-it"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}"
    data = json.dumps({"contents": [{"parts": [{"text": "Say hi"}]}]}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            print(f"{model}: SUCCESS - {result['candidates'][0]['content']['parts'][0]['text'][:80]}")
            break
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            msg = json.loads(body)['error']['message'][:120]
        except:
            msg = body[:120]
        print(f"{model}: ERROR {e.code} - {msg}")
    except Exception as e:
        print(f"{model}: ERROR - {e}")
