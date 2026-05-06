---
name: radar-fetch
description: Fetch the latest ArXiv research papers relevant to Samsung on-device AI (quantization, KV-cache, model compression).
metadata:
  {
    "openclaw": {
      "emoji": "📡",
      "requires": {
        "env": ["SEMANTIC_SCHOLAR_API_KEY"]
      }
    }
  }
---

# RADAR — Paper Fetcher

Fetch the latest ArXiv papers from the RADAR harvester module.

```bash
cd c:\Users\sahit\Desktop\Samsung-Prism\SAMSUNG_PRISM
python -m fetchers.paper_fetcher
```

After running, check and report:
1. How many papers were saved to `contracts/incoming_papers.json`
2. The top 3 paper titles fetched
3. Whether any paper looks immediately relevant to Samsung on-device AI

Then ask: "Would you like me to run the Gemini Brain analysis on these papers?"
