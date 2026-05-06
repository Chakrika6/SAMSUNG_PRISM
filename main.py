import subprocess
import time
import sys
from dotenv import load_dotenv

load_dotenv()

def run_script(script_cmd):
    print(f"\n[{script_cmd}] Running...")
    try:
        # Split cmd in case there are arguments like --mock
        cmd = [sys.executable] + script_cmd.split()
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_cmd}: {e.stderr}")
        sys.exit(1)

def heartbeat():
    print("=========================================")
    print("Executing RADAR Heartbeat...")
    print("=========================================\n")
    
    # Step 1: Call fetchers module
    print("Step 1: Multi-Dimensional Harvesting (Opportunities, Threats, Trends)...")
    run_script("fetchers/paper_fetcher.py")
    run_script("fetchers/fetch_threats.py")
    run_script("fetchers/fetch_historical_trends.py")
    
    # Step 2: Call brain module
    print("Step 2: Processing Intelligence via Gemini & ML...")
    run_script("brain/process_papers.py")    # Opportunity mapping
    run_script("brain/trend_analyzer.py")    # Trend clustering & velocity
    
    # Step 3: Call outputs module
    print("Step 3: Dispatching Multi-Repo Actions & Intel...")
    run_script("outputs/github_dispatcher.py")
    run_script("outputs/auto_pr.py --mock")
    
    print("\nStep 4: Broadcasting to Telegram (Threats & Trends)...")
    run_script("outputs/send_alert.py")
    run_script("outputs/trend_broadcaster.py")
    
    print("\n=========================================")
    print("Heartbeat completed successfully.")
    print("=========================================")

if __name__ == "__main__":
    heartbeat()
