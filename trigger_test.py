import time
import subprocess
import os
import sys

TARGET_TIME = "19:52"
print(f"RADAR Automation Test: Waiting until {TARGET_TIME} to trigger the pipeline...")

while True:
    current_time = time.strftime("%H:%M")
    if current_time == TARGET_TIME:
        print("\n[MATCH] Triggering RADAR Pipeline...")
        # Set environment variables
        env = os.environ.copy()
        env["GOOGLE_API_KEY"] = "AIzaSyBXvvaWWE2Ah-v83deyb9gXHwUF1Nrz-rw"
        env["GITHUB_TOKEN"] = "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"
        env["TELEGRAM_BOT_TOKEN"] = "8638650035:AAEE-Pdmfzlw83L9-3oquH6WOuXreMzRXbs"
        env["TELEGRAM_CHAT_ID"] = "-4838787469"
        
        subprocess.run([sys.executable, "main.py"], env=env, cwd=os.getcwd())
        print("\n[DONE] Pipeline execution finished.")
        break
    
    # Simple countdown
    sys.stdout.write(f"\rCurrent time: {current_time} | Waiting for {TARGET_TIME}...")
    sys.stdout.flush()
    time.sleep(10)
