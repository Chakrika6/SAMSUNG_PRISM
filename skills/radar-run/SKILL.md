---
name: radar-run
description: Run the complete RADAR Enterprise Fusion pipeline — scan org, fetch papers, analyze across all repos, create PRs/Issues, and broadcast to Telegram.
metadata:
  {
    "openclaw": {
      "emoji": "🔬",
      "requires": {
        "env": ["GOOGLE_API_KEY", "GITHUB_TOKEN", "GITHUB_ORG", "TELEGRAM_BOT_TOKEN"]
      }
    }
  }
---

# RADAR Enterprise Fusion Pipeline

Run the full autonomous heartbeat. This single command executes all 5 steps:

**Full Pipeline (Recommended)**
```bash
cd {{workspace}}
python main.py
```

This will automatically:
1. **Step 0 — Org Scan**: Deep-scan all repos in the GitHub Organization (READMEs + code files + issues)
2. **Step 1 — Harvest**: Fetch papers from ArXiv, competitor threats, and historical trends
3. **Step 2 — Brain**: Analyze papers against ALL repos using Gemini (with Groq fallback)
4. **Step 3 — Execute**: Create PRs for code fixes and Issues for research alerts in the correct repos
5. **Step 4 — Broadcast**: Send a consolidated Enterprise Report to Telegram

After the pipeline completes, report:
- How many repos were scanned
- How many papers were fetched
- Which papers were matched to which repos
- The PR/Issue URLs that were created
- Confirmation that the Telegram report was dispatched

If Gemini fails due to API rate limits, the system automatically falls back to Groq Llama-3.3.
