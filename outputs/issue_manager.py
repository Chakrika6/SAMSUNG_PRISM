import os
import json
from pathlib import Path
from dotenv import load_dotenv
from github import Github

# Load env vars (needed when run as subprocess)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

def main():
    base_dir = Path(__file__).parent.parent
    PENDING_ACTIONS_PATH = base_dir / "contracts" / "pending_actions.json"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_ORG = os.getenv("GITHUB_ORG")

    if not PENDING_ACTIONS_PATH.exists():
        print("No pending actions.")
        return

    with open(PENDING_ACTIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        actions = data.get("actions", [])

    g = Github(GITHUB_TOKEN)
    
    for action in actions:
        if action["action_type"] == "ISSUE":
            repo_name = action["target_entity"]
            print(f"[ISSUE] Creating issue in {repo_name}...")
            
            try:
                repo = g.get_repo(f"{GITHUB_ORG}/{repo_name}")
                title = f"[RADAR] {action['paper_title']}"
                body = f"### Research Alert: {action['type']}\n\n"
                body += f"**Reason:** {action['reason']}\n\n"
                body += f"**Paper URL:** {action['url']}\n\n"
                body += f"**Proposed Steps:**\n{action['proposed_implementation']}\n"
                
                repo.create_issue(title=title, body=body, labels=["radar-intelligence"])
                print(f"   [OK] Issue created: {title}")
            except Exception as e:
                print(f"   [FAIL] Could not create issue in {repo_name}: {e}")

if __name__ == "__main__":
    main()
