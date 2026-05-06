---
name: radar-alert
description: Send a Telegram alert with the latest RADAR findings from pending_actions.json.
metadata:
  {
    "openclaw": {
      "emoji": "📢",
      "requires": {
        "env": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
      }
    }
  }
---

# RADAR — Telegram Alert

Send a Telegram notification with the latest high-priority research findings.

```bash
cd c:\Users\sahit\Desktop\Samsung-Prism\SAMSUNG_PRISM
python outputs/send_alert.py
```

After running, confirm:
- Whether the message was sent successfully
- A preview of what was sent

If TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set, explain how to configure them and point to the `.env.example` file.
