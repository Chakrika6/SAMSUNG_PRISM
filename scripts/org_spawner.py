import os
import json
from pathlib import Path
from github import Github, GithubException
from dotenv import load_dotenv

# Load environment variables from .env in project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG")
DATA_DIR = Path(__file__).parent.parent / "data"

def create_repo_in_org(g, org_name, repo_name, description):
    """Create a repository in the specified organization."""
    try:
        org = g.get_organization(org_name)
        repo = org.create_repo(
            repo_name,
            description=description,
            auto_init=True  # Creates a README so we can commit to it immediately
        )
        print(f"[OK] Created repository: {repo.full_name}")
        return repo
    except GithubException as e:
        if e.status == 422: # Already exists
            print(f"[INFO] Repository {repo_name} already exists in {org_name}.")
            return org.get_repo(repo_name)
        else:
            print(f"[ERROR] Failed to create repo {repo_name}: {e}")
            return None

def upload_context_readme(repo, context_file):
    """Upload the repo_context.md content as the README.md."""
    if not context_file.exists():
        print(f"[WARN] No context file found at {context_file}")
        return

    with open(context_file, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        readme = repo.get_contents("README.md")
        repo.update_file(
            readme.path,
            "Initialize with RADAR Repository Context",
            content,
            readme.sha
        )
        print(f"[OK] Updated README for {repo.name} with context data.")
    except GithubException:
        # If README doesn't exist for some reason
        repo.create_file("README.md", "Initialize with RADAR Repository Context", content)
        print(f"[OK] Created README for {repo.name} with context data.")

def main():
    if not GITHUB_TOKEN or not GITHUB_ORG:
        print("[ERROR] GITHUB_TOKEN and GITHUB_ORG must be set in environment.")
        return

    g = Github(GITHUB_TOKEN)
    
    # Iterate through each folder in data/
    # Each folder represents a repository to be spawned
    for folder in DATA_DIR.iterdir():
        if folder.is_dir() and not folder.name.startswith("."):
            repo_name = folder.name
            context_file = folder / "repo_context.md"
            
            print(f"\n[PROCESS] Spawning repo for: {repo_name}...")
            
            # 1. Create Repo
            description = f"Demo repository for {repo_name.replace('-', ' ').title()} - Managed by RADAR Agent"
            repo = create_repo_in_org(g, GITHUB_ORG, repo_name, description)
            
            if repo:
                # 2. Upload Context
                upload_context_readme(repo, context_file)

    print("\n[DONE] Organization spawning complete.")

if __name__ == "__main__":
    main()
