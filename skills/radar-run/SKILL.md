---
name: radar-run
description: Run the complete RADAR pipeline — fetch papers, analyze with Gemini, generate code, and submit a GitHub Pull Request automatically.
metadata:
  {
    "openclaw": {
      "emoji": "🔬",
      "requires": {
        "env": ["GOOGLE_API_KEY", "GITHUB_TOKEN"]
      }
    }
  }
---

# RADAR Full Pipeline

Run the complete RADAR autonomous research pipeline:

**Step 1 — Fetch Papers**
```bash
cd c:\Users\sahit\Desktop\Samsung-Prism\SAMSUNG_PRISM
python -m fetchers.paper_fetcher
```

**Step 2 — Analyze with Gemini Brain Engine**
```bash
cd c:\Users\sahit\Desktop\Samsung-Prism\SAMSUNG_PRISM
python -m brain.engine
```

**Step 3 — Auto-Coder: Generate Code & Submit PR**
```bash
cd c:\Users\sahit\Desktop\Samsung-Prism\SAMSUNG_PRISM
python outputs/auto_pr.py
```

After each step, read the output and report:
- How many papers were fetched
- Which paper was selected by the Gemini Brain
- The PR URL that was created

If any step fails due to API rate limits, automatically add `--mock` to step 3 and proceed.
