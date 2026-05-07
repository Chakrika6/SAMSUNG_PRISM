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

def load_contract(path: Path) -> dict:
    """Load and return data from a JSON contract file."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _escape(text: str) -> str:
    """Escape all MarkdownV2 special characters in plain text."""
    # Characters that must be escaped in MarkdownV2 outside code/pre blocks
    special = r"\_*[]()~`>#+-=|{}.!"
    for ch in special:
        text = text.replace(ch, f"\\{ch}")
    return text


def format_enterprise_report(actions_data: dict, trends_data: dict) -> str:
    """Build a comprehensive Markdown-formatted report for the entire organization."""
    actions = actions_data.get("actions", [])
    
    lines = [
        "🏢 *RADAR Enterprise Fusion Report*",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    # 1. Trends Section
    if trends_data:
        lines.append("📈 *Global Research Trends*")
        top_trends = trends_data.get("top_clusters", [])[:3]
        for t in top_trends:
            lines.append(f"• _{_escape(t['name'])}_ \\(Velocity: {t.get('velocity', 'N/A')}\\)")
        lines.append("")

    # 2. Actions Section
    if actions:
        lines.append("⚡ *Active Repositories & Intel*")
        for act in actions:
            emoji = "🔴" if act.get("type", "").lower() == "threat" else "🟢"
            action_icon = "🔨" if act.get("action_type") == "PR" else "📋"
            
            lines.append(f"{emoji} *Repo:* `{_escape(act['target_entity'])}`")
            lines.append(f"📄 *Paper:* [{_escape(act['paper_title'])}]({act['url']})")
            lines.append(f"{action_icon} *Status:* {_escape(act['action_type'])} created")
            lines.append(f"🧠 *Reason:* _{_escape(act['reason'])}_")
            lines.append("---")
    else:
        lines.append("✅ No critical threats or code opportunities detected today.")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🤖 _RADAR Autonomous Heartbeat_")
    
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core async sender
# ---------------------------------------------------------------------------

async def send_report(token: str, chat_id: str, report_text: str) -> None:
    """Send the consolidated report to Telegram."""
    bot = Bot(token=token)
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=report_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True,
        )
        print("[OK] Enterprise Report dispatched.")
    except Exception as exc:
        print(f"[ERROR] Failed to send report: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Guard against unconfigured credentials
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[ERROR] TELEGRAM_BOT_TOKEN is not set.")
        sys.exit(1)

    if TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("[ERROR] TELEGRAM_CHAT_ID is not set.")
        sys.exit(1)

    TRENDS_PATH = CONTRACTS_DIR / "trend_report.json"
    
    actions_data = load_contract(PENDING_ACTIONS_PATH)
    trends_data = load_contract(TRENDS_PATH)

    report_text = format_enterprise_report(actions_data, trends_data)
    asyncio.run(send_report(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, report_text))


if __name__ == "__main__":
    main()
