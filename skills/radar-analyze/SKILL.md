---
name: radar-analyze
description: Run the RADAR Gemini Brain Engine — reads incoming_papers.json and outputs a priority action to pending_actions.json.
metadata:
  {
    "openclaw": {
      "emoji": "🧠",
      "requires": {
        "env": ["GOOGLE_API_KEY"]
      }
    }
  }
---

# RADAR — Gemini Brain Engine

Run the Gemini-powered threat and opportunity analysis engine.

```bash
cd c:\Users\sahit\Desktop\Samsung-Prism\SAMSUNG_PRISM
python -m brain.engine
```

After running, read `contracts/pending_actions.json` and report back:
- The paper title selected as highest priority
- The reason it was chosen
- The recommended action
- The `target_entity` (the function/class to implement)

Format the output as:
> 🔬 **Selected Paper:** [title](url)
> **Why it matters:** [reason]
> **Action:** [action]
> **Target entity:** `target_entity`

Then ask: "Would you like me to generate the code and submit a Pull Request?"
