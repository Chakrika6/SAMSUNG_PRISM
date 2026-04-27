"""
RADAR - The Heartbeat (Integrator)
This script acts as the central coordinator.
Once Member 2, 3, and 4 finish their scripts, we import them here to run in sequence.
"""

def heartbeat():
    print("Executing RADAR Heartbeat...")
    # Step 1: Call fetchers module (Outputs to incoming_papers.json)
    print("Step 1: Fetching papers...")
    
    # Step 2: Call brain module (Reads incoming_papers.json -> Outputs pending_actions.json)
    print("Step 2: Processing via Gemini API...")
    
    # Step 3: Call outputs module (Reads pending_actions.json -> Sends to Telegram/GitHub)
    print("Step 3: Dispatching alerts...")
    
    print("Heartbeat completed successfully.")

if __name__ == "__main__":
    heartbeat()
