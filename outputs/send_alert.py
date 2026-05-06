"""
Member 4 – The Communicator (outputs/send_alert.py)
====================================================
Reads `contracts/pending_actions.json` produced by Member 3's Brain Engine
and dispatches a clean, Markdown-formatted alert to a Telegram chat using
the `python-telegram-bot` library (v20+, async).

Usage
-----
1. Install dependency:
       pip install python-telegram-bot

2. Set your credentials either as environment variables (recommended) or
   edit the constants below:
       TELEGRAM_BOT_TOKEN  – Token from @BotFather
       TELEGRAM_CHAT_ID    – Target chat / channel ID (use a negative
                             number for groups/channels, e.g. -100xxxxxxxxxx)

3. Run from the SAMSUNG_PRISM root directory:
       python outputs/send_alert.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv

# Load environment variables from .env in project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# ---------------------------------------------------------------------------
# Configuration – override via environment variables or edit directly here
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

# Path to the contract file (relative to this script's location)
SCRIPT_DIR = Path(__file__).parent          # outputs/
CONTRACTS_DIR = SCRIPT_DIR.parent / "contracts"
PENDING_ACTIONS_PATH = CONTRACTS_DIR / "pending_actions.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_pending_actions() -> list[dict]:
    """Load and return the list of alerts from pending_actions.json."""
    if not PENDING_ACTIONS_PATH.exists():
        print(f"[ERROR] Contract file not found: {PENDING_ACTIONS_PATH}")
        sys.exit(1)

    with open(PENDING_ACTIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("[ERROR] pending_actions.json must contain a JSON array.")
        sys.exit(1)

    return data


def _escape(text: str) -> str:
    """Escape all MarkdownV2 special characters in plain text."""
    # Characters that must be escaped in MarkdownV2 outside code/pre blocks
    special = r"\_*[]()~`>#+-=|{}.!"
    for ch in special:
        text = text.replace(ch, f"\\{ch}")
    return text


def format_alert(alert: dict, index: int, total: int) -> str:
    """
    Build a Markdown-formatted Telegram message for a single alert.

    Expected fields (from Member 3's contract):
        paper_title, url, type, reason, action
    """
    paper_title = alert.get("paper_title", "Unknown Paper")
    url         = alert.get("url", "")
    alert_type  = alert.get("type", "Info")
    reason      = alert.get("reason", "No reason provided.")
    action      = alert.get("action", "No action specified.")

    # Emoji badge based on alert type
    type_emoji = {
        "opportunity": "🟢",
        "threat":      "🔴",
        "info":        "🔵",
    }.get(alert_type.lower(), "⚪")

    # Escape free-text fields; leave url and action unescaped (used in link / code span)
    safe_title      = _escape(paper_title)
    safe_alert_type = _escape(alert_type)
    safe_reason     = _escape(reason)

    lines = [
        f"🤖 *RADAR Alert \\[{index}/{total}\\]*",
        "",
        f"📄 *Paper:* [{safe_title}]({url})" if url else f"📄 *Paper:* {safe_title}",
        f"{type_emoji} *Type:* {safe_alert_type}",
        "",
        "🧠 *Why it matters:*",
        f"_{safe_reason}_",
        "",
        "⚡ *Recommended Action:*",
        f"`{action}`",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core async sender
# ---------------------------------------------------------------------------

async def send_alerts(token: str, chat_id: str, alerts: list[dict]) -> None:
    """Iterate over alerts and send each one as a Telegram message."""
    bot = Bot(token=token)

    # Verify the bot token is valid before sending anything
    try:
        me = await bot.get_me()
        print(f"[INFO] Connected as @{me.username}. Sending {len(alerts)} alert(s)…")
    except Exception as exc:
        print(f"[ERROR] Could not authenticate with Telegram: {exc}")
        sys.exit(1)

    total = len(alerts)
    for idx, alert in enumerate(alerts, start=1):
        message = format_alert(alert, idx, total)
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=False,
            )
            print(f"[OK]   Alert {idx}/{total} sent: {alert.get('paper_title', '?')}")
        except Exception as exc:
            print(f"[WARN] Failed to send alert {idx}/{total}: {exc}")

    print("[DONE] All alerts dispatched.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Guard against unconfigured credentials
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(
            "[ERROR] TELEGRAM_BOT_TOKEN is not set.\n"
            "        Export it as an environment variable:\n"
            "            set TELEGRAM_BOT_TOKEN=<your-token>   (Windows)\n"
            "            export TELEGRAM_BOT_TOKEN=<your-token> (Linux/Mac)"
        )
        sys.exit(1)

    if TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        print(
            "[ERROR] TELEGRAM_CHAT_ID is not set.\n"
            "        Export it as an environment variable:\n"
            "            set TELEGRAM_CHAT_ID=<your-chat-id>   (Windows)\n"
            "            export TELEGRAM_CHAT_ID=<your-chat-id> (Linux/Mac)"
        )
        sys.exit(1)

    alerts = load_pending_actions()

    if not alerts:
        print("[INFO] No alerts found in pending_actions.json. Nothing to send.")
        return

    asyncio.run(send_alerts(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, alerts))


if __name__ == "__main__":
    main()
