---
name: radar-pr
description: Run the RADAR Auto-Coder — generate a Python implementation from pending_actions.json and submit it as a GitHub Pull Request.
metadata:
  {
    "openclaw": {
      "emoji": "⚡",
      "requires": {
        "env": ["GITHUB_TOKEN", "GOOGLE_API_KEY"]
      }
    }
  }
---

# RADAR — Auto-Coder & PR Submitter

Generate code with Gemini and submit a GitHub Pull Request automatically.

**Normal mode (uses Gemini to write real code):**
```bash
cd c:\Users\sahit\Desktop\Samsung-Prism\SAMSUNG_PRISM
python outputs/auto_pr.py
```

**Mock mode (template code, no Gemini quota needed):**
```bash
cd c:\Users\sahit\Desktop\Samsung-Prism\SAMSUNG_PRISM
python outputs/auto_pr.py --mock
```

If the first command fails with a quota or 429 error, automatically fall back to mock mode.

After running, extract and report:
- The GitHub PR URL (look for lines starting with `[OK]    PR opened:`)
- The branch name created
- The file path committed

Format response as:
> ⚡ **Auto-Coder Complete!**
> PR: [link](url)
> Branch: `branch-name`
> File: `generated/entity.py`
