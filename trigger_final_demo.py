import time
import subprocess
import os
import sys

TARGET_TIME = "20:49"
print(f"RADAR Final Org-Scale Test: Waiting until {TARGET_TIME} to trigger the pipeline...")

while True:
    current_time = time.strftime("%H:%M")
    if current_time == TARGET_TIME:
        print("\n[MATCH] Triggering Full Org-Scale Pipeline...")
        # main.py now includes Step 0 (Org Scanner)
        subprocess.run([sys.executable, "main.py"], cwd=os.getcwd())
        print("\n[DONE] Pipeline execution finished.")
        break
    
    # Simple countdown
    sys.stdout.write(f"\rCurrent time: {current_time} | Waiting for {TARGET_TIME}...")
    sys.stdout.flush()
    time.sleep(10)
