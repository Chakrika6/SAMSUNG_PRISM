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

# Ensure project root is in path (needed when run as subprocess)
sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# ---------------------------------------------------------------------------
# Configuration – override via environment variables or edit directly here
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

# Path to the contract file (relative to this script's location)
SCRIPT_DIR = Path(__file__).parent          # outputs/
CONTRACTS_DIR = SCRIPT_DIR.parent / "contracts"
PENDING_ACTIONS_PATH = CONTRACTS_DIR / "pending_actions.json"

# Path to the memory file
SENT_ALERTS_PATH = CONTRACTS_DIR / "sent_alerts.json"
ORG_PROFILE_PATH = CONTRACTS_DIR / "org_profile.json"

def load_sent_history() -> set:
    """Load the set of URLs already sent to Telegram."""
    if not SENT_ALERTS_PATH.exists():
        return set()
    with open(SENT_ALERTS_PATH, "r", encoding="utf-8") as f:
        try:
            return set(json.load(f))
        except:
            return set()

def load_contract(path: Path) -> dict:
    """Load and return data from a JSON contract file."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

def _escape(text: str) -> str:
    """Escape all MarkdownV2 special characters in plain text."""
    special = r"\_*[]()~`>#+-=|{}.!"
    for ch in special:
        text = text.replace(ch, f"\\{ch}")
    return text

def save_sent_history(history: set):
    """Save the updated history of sent URLs."""
    with open(SENT_ALERTS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(history), f, indent=2)

def format_deep_focus_report(org_data: dict) -> str:
    """Build a report for days when no new research is detected."""
    lines = [
        "🛡️ *RADAR STRATEGIC STATUS: STEADY*",
        "╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾",
        "No new competitor moves or high\\-priority opportunities detected in the last scan\\.",
        "",
        "🎯 *Current Engineering Focus:*",
    ]

    repos = org_data.get("repo_strategies", [])[:3] 
    if repos:
        for r in repos:
            repo_name = _escape(r.get("repo_name", "Unknown"))
            lines.append(f"• *{repo_name}*")
            issues = r.get("engineering_goals", [])[:2]
            for issue in issues:
                lines.append(f"  ▫️ {_escape(issue)}")
    else:
        lines.append("Review existing open issues on GitHub to maintain momentum\\.")

    lines.append("")
    lines.append("💡 _Next scan scheduled in 24h\\. Stay focused on current implementation targets\\._")
    lines.append("╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾╾")
    lines.append("🤖 _RADAR Autonomous Heartbeat_")
    
    return "\n".join(lines)

def format_threat_report(actions: list, history: set) -> str:
    """Build a high-priority report focused exclusively on NEW competitor threats."""
    threats = [a for a in actions if a.get("type", "").lower() == "threat" and a.get("url") not in history]
    if not threats:
        return ""

    lines = [
        "🚨 *RADAR CRITICAL THREAT ALERT*",
        "⚠️ *Competitor Move Detected*",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    for t in threats:
        repo = _escape(str(t.get('target_entity', 'Unknown')))
        paper = _escape(str(t.get('paper_title', 'Research Paper')))
        url = t.get('url', '')
        reason = _escape(str(t.get('reason', 'Critical overlap detected.')))
        impl = _escape(str(t.get('proposed_implementation', 'N/A')))

        lines.append(f"🔴 *Target Project:* `{repo}`")
        if url:
            lines.append(f"📄 *Competitor Paper:* [{paper}]({url})")
            history.add(url) # Mark as sent
        else:
            lines.append(f"📄 *Competitor Paper:* {paper}")
        lines.append(f"🛑 *Risk:* {reason}")
        lines.append(f"🛡️ *Mitigation:* {impl}")
        lines.append("┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄")

    lines.append("")
    lines.append("❗ *Immediate attention required from R&D Lead\\.*")
    return "\n".join(lines)

def format_opportunity_report(actions: list, history: set) -> str:
    """Build a report for NEW standard research opportunities."""
    opps = [a for a in actions if a.get("type", "").lower() == "opportunity" and a.get("url") not in history]
    if not opps:
        return ""

    lines = [
        "🟢 *RADAR OPPORTUNITY DIGEST*",
        "🛠️ *Engineering Optimizations*",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    for o in opps:
        repo = _escape(str(o.get('target_entity', 'Unknown')))
        paper = _escape(str(o.get('paper_title', 'Research Paper')))
        url = o.get('url', '')
        reason = _escape(str(o.get('reason', 'Performance gain possible.')))
        
        if url:
            history.add(url) # Mark as sent

        lines.append(f"✅ *Repo:* `{repo}`")
        if url:
            lines.append(f"📄 *Source:* [{paper}]({url})")
        else:
            lines.append(f"📄 *Source:* {paper}")
        lines.append(f"🧠 *Why:* _{reason}_")
        lines.append("┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄")

    lines.append("")
    lines.append("🤖 _RADAR Autonomous Heartbeat_")
    return "\n".join(lines)

async def send_message(token: str, chat_id: str, text: str, name: str) -> None:
    """Helper to send a single message."""
    if not text:
        return
    bot = Bot(token=token)
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True,
        )
        print(f"[OK] {name} dispatched.")
    except Exception as exc:
        print(f"[ERROR] Failed to send {name}: {exc}")

def main() -> None:
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("[ERROR] Telegram credentials not configured.")
        sys.exit(1)

    data = load_contract(PENDING_ACTIONS_PATH)
    actions = data.get("actions", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    org_data = load_contract(ORG_PROFILE_PATH)
    
    history = load_sent_history()

    threat_text = format_threat_report(actions, history)
    opp_text = format_opportunity_report(actions, history)
    
    # NEW: If nothing was sent, send the Deep Focus report
    final_text = ""
    if not threat_text and not opp_text:
        final_text = format_deep_focus_report(org_data)
        name = "Deep Focus Report"
    else:
        # Save history only if we actually found something new
        save_sent_history(history)
        # Reports will be sent via loop.run_until_complete below

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if final_text:
        loop.run_until_complete(send_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, final_text, name))
    else:
        if threat_text:
            loop.run_until_complete(send_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, threat_text, "Threat Report"))
        if opp_text:
            loop.run_until_complete(send_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, opp_text, "Opportunity Report"))

if __name__ == "__main__":
    main()
