---
name: radar-status
description: Show the current status of the RADAR pipeline — pending actions, last run results, and system health.
metadata:
  {
    "openclaw": {
      "emoji": "📊"
    }
  }
---

# RADAR — Status Check

Check the current state of all RADAR pipeline contracts and files.

Run these commands to inspect the pipeline state:

```bash
cd c:\Users\sahit\Desktop\Samsung-Prism\SAMSUNG_PRISM

# Check pending actions
python -c "import json; data=json.load(open('contracts/pending_actions.json')); print(f'Pending actions: {len(data)}'); [print(f'  - {a[\"paper_title\"]} ({a[\"type\"]})') for a in data]"

# Check incoming papers count
python -c "import json; data=json.load(open('contracts/incoming_papers.json')); print(f'Incoming papers cached: {len(data)}')"

# Check generated files
python -c "import os; files=list(filter(lambda f: f.endswith('.py'), os.listdir('generated') if os.path.exists('generated') else [])); print(f'Generated files: {len(files)}'); [print(f'  - {f}') for f in files]"
```

Format the status report as:

> 📊 **RADAR System Status**
> 🔬 Incoming papers: [N]
> ⚡ Pending actions: [N]
> 📁 Generated implementations: [N]
> 
> **Next recommended step:** [suggest what to do next]
