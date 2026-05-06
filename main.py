"""
RADAR - The Heartbeat (Integrator)
This script acts as the central coordinator.
It wires together the fetchers, brain, and outputs pipeline.

OpenClaw Integration
--------------------
This project is integrated with OpenClaw for autonomous, always-on operation.
The OpenClaw agent (RADAR) can run this pipeline on demand or on a schedule
via the skills in openclaw/skills/.

  /radar-run     -> full pipeline
  /radar-fetch   -> only fetch papers
  /radar-analyze -> only Gemini brain analysis
  /radar-pr      -> only auto-coder + GitHub PR
  /radar-alert   -> only Telegram alert
  /radar-status  -> show pipeline status

See openclaw/SOUL.md for agent personality and openclaw/HEARTBEAT.md for schedule.
"""

import sys
import os

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


def heartbeat():
    print("=" * 60)
    print("  RADAR Heartbeat - Autonomous Research Pipeline")
    print("=" * 60)

    # Step 1: Fetch papers (Member 2 - Data Harvester)
    print("\n[Step 1] Fetching papers via Semantic Scholar / ArXiv...")
    try:
        from fetchers.paper_fetcher import run_fetcher
        run_fetcher()
        print("[Step 1] [OK] Papers fetched -> contracts/incoming_papers.json")
    except Exception as e:
        print(f"[Step 1] [FAIL] Fetcher failed: {e}")
        print("         Continuing with cached incoming_papers.json if available.")

    # Step 2: Analyze via Gemini Brain Engine (Member 3)
    print("\n[Step 2] Analyzing papers with Gemini Brain Engine...")
    try:
        from brain.engine import main as analyze_papers
        analyze_papers()
        print("[Step 2] [OK] Analysis complete -> contracts/pending_actions.json")
    except Exception as e:
        print(f"[Step 2] [FAIL] Brain engine failed: {e}")
        print("         Continuing with existing pending_actions.json if available.")

    # Step 3: Auto-Coder - generate code and submit PR (Member 4)
    print("\n[Step 3] Running Auto-Coder and submitting GitHub PR...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "outputs/auto_pr.py"],
            capture_output=False,
            cwd=os.path.dirname(__file__),
        )
        if result.returncode != 0:
            print("[Step 3] Auto-Coder exited with errors. "
                  "Try running: python outputs/auto_pr.py --mock")
        else:
            print("[Step 3] [OK] Auto-Coder complete.")
    except Exception as e:
        print(f"[Step 3] [FAIL] Auto-Coder failed: {e}")

    # Step 4: Send Telegram alert (Member 4)
    print("\n[Step 4] Dispatching Telegram alert...")
    try:
        from outputs.send_alert import main as send_alert
        send_alert()
        print("[Step 4] [OK] Alert sent.")
    except Exception as e:
        print(f"[Step 4] [FAIL] Alert failed: {e}")

    # Step 5: Send Telegram Trend Broadcaster (Member 4)
    print("\n[Step 5] Dispatching Telegram Trend Analysis Alert...")
    try:
        from outputs.trend_broadcaster import main as broadcast_trends
        broadcast_trends()
        print("[Step 5] [OK] Trend Broadcaster sent.")
    except Exception as e:
        print(f"[Step 5] [FAIL] Trend Broadcaster failed: {e}")

    print("\n" + "=" * 60)
    print("  Heartbeat completed.")
    print("=" * 60)


if __name__ == "__main__":
    heartbeat()
