"""
Member 4 – The Communicator | outputs/trend_broadcaster.py
===========================================================
Reads `contracts/live_trends.json` produced by Member 3's Trend Engine
and fires a beautifully formatted Markdown card to the Telegram channel.

Card design:
    🔴 LIVE TREND DETECTED: [Cluster Name]
    📊 17 New Papers in last 14 days
    🔬 Key Competitors acting: [Institutions]
    ⚠️  Implication: [Summary]

Usage
-----
1. Install dependency (if not already installed):
       pip install python-telegram-bot

2. Set credentials as environment variables (recommended) OR edit the
   constants block below:
       TELEGRAM_BOT_TOKEN  – Token from @BotFather
       TELEGRAM_CHAT_ID    – Target chat / channel ID

3. Run from the SAMSUNG_PRISM root directory:
       python outputs/trend_broadcaster.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from telegram import Bot
from telegram.constants import ParseMode

# ---------------------------------------------------------------------------
# Configuration – set via environment variables or edit directly here
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

# Path to contract (relative to this script)
SCRIPT_DIR        = Path(__file__).parent          # outputs/
CONTRACTS_DIR     = SCRIPT_DIR.parent / "contracts"
LIVE_TRENDS_PATH  = CONTRACTS_DIR / "live_trends.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_live_trends() -> list[dict]:
    """Load the trend list from contracts/live_trends.json."""
    if not LIVE_TRENDS_PATH.exists():
        print(f"[ERROR] Contract file not found: {LIVE_TRENDS_PATH}")
        sys.exit(1)
    with open(LIVE_TRENDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print("[ERROR] live_trends.json must contain a JSON array.")
        sys.exit(1)
    return data


def _escape(text: str) -> str:
    """Escape all MarkdownV2 special characters in plain text."""
    special = r"\_*[]()~`>#+-=|{}.!"
    for ch in special:
        text = text.replace(ch, f"\\{ch}")
    return text


def format_trend_card(trend: dict, index: int, total: int) -> str:
    """
    Build a beautiful Markdown card for a single live trend.

    Expected fields (from Member 3's live_trends.json contract):
        cluster_name, paper_count, timeframe_days,
        key_competitors, implication,
        top_paper { title, url },
        trend_score  (optional)
    """
    cluster_name    = trend.get("cluster_name",    "Unknown Cluster")
    paper_count     = trend.get("paper_count",     0)
    timeframe_days  = trend.get("timeframe_days",  14)
    competitors     = trend.get("key_competitors", [])
    implication     = trend.get("implication",     "No implication provided.")
    trend_score     = trend.get("trend_score",     None)
    top_paper       = trend.get("top_paper",       {})
    top_title       = top_paper.get("title", "")
    top_url         = top_paper.get("url", "")

    # Escaped safe versions for MarkdownV2
    safe_cluster     = _escape(cluster_name)
    safe_implication = _escape(implication)
    safe_competitors = _escape(", ".join(competitors) if competitors else "Unknown")
    safe_top_title   = _escape(top_title)

    # Trend score badge
    if trend_score is not None:
        score_int = int(trend_score)
        if score_int >= 80:
            score_badge = f"🔥 *Trend Score:* `{score_int}/100` \\(CRITICAL\\)"
        elif score_int >= 50:
            score_badge = f"⚠️ *Trend Score:* `{score_int}/100` \\(HIGH\\)"
        else:
            score_badge = f"📈 *Trend Score:* `{score_int}/100` \\(MODERATE\\)"
    else:
        score_badge = ""

    # Top paper line
    if top_title and top_url:
        top_paper_line = f"📎 *Top Paper:* [{safe_top_title}]({top_url})"
    elif top_title:
        top_paper_line = f"📎 *Top Paper:* {safe_top_title}"
    else:
        top_paper_line = ""

    lines = [
        f"🔴 *LIVE TREND DETECTED: {safe_cluster}*",
        "",
        f"📊 *{paper_count} New Papers* in last {timeframe_days} days",
        f"🔬 *Key Competitors acting:* {safe_competitors}",
        f"⚠️ *Implication:* {safe_implication}",
        "",
    ]

    if score_badge:
        lines.append(score_badge)
        lines.append("")

    if top_paper_line:
        lines.append(top_paper_line)
        lines.append("")

    lines += [
        f"━━━━━━━━━━━━━━━━━━━━━━━━",
        f"_RADAR Trend Digest · Alert {index}/{total}_",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core async broadcaster
# ---------------------------------------------------------------------------

async def broadcast_trends(token: str, chat_id: str, trends: list[dict]) -> None:
    """Send one Telegram card per trend."""
    bot = Bot(token=token)

    try:
        me = await bot.get_me()
        print(f"[INFO] Connected as @{me.username}. Broadcasting {len(trends)} trend(s)…")
    except Exception as exc:
        print(f"[ERROR] Could not authenticate with Telegram: {exc}")
        sys.exit(1)

    total = len(trends)
    for idx, trend in enumerate(trends, start=1):
        card = format_trend_card(trend, idx, total)
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=card,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=False,
            )
            print(f"[OK]   Trend {idx}/{total} sent: {trend.get('cluster_name', '?')}")
        except Exception as exc:
            print(f"[WARN] Failed to send trend {idx}/{total}: {exc}")

    print("[DONE] All trend cards dispatched.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(
            "[ERROR] TELEGRAM_BOT_TOKEN is not set.\n"
            "        Export it as an environment variable:\n"
            "            $env:TELEGRAM_BOT_TOKEN = '<token>'  (PowerShell)\n"
            "            export TELEGRAM_BOT_TOKEN=<token>    (Linux/Mac)"
        )
        sys.exit(1)

    if TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        print(
            "[ERROR] TELEGRAM_CHAT_ID is not set.\n"
            "        Export it as an environment variable:\n"
            "            $env:TELEGRAM_CHAT_ID = '<id>'  (PowerShell)\n"
            "            export TELEGRAM_CHAT_ID=<id>    (Linux/Mac)"
        )
        sys.exit(1)

    trends = load_live_trends()

    if not trends:
        print("[INFO] No trends found in live_trends.json. Nothing to broadcast.")
        return

    asyncio.run(broadcast_trends(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, trends))


if __name__ == "__main__":
    main()
