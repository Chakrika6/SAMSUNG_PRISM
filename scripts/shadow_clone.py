import os
from github import Github, GithubException
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env in project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG") # Your Demo Org

def mirror_org(g, target_org_name, limit=5):
    """Fetch top repos from a real org and mirror them to the demo org."""
    try:
        target_org = g.get_organization(target_org_name)
        demo_org = g.get_organization(GITHUB_ORG)
        
        print(f"[INFO] Mirroring top {limit} repos from '{target_org_name}' to '{GITHUB_ORG}'...")
        
        repos = list(target_org.get_repos(sort="stars", direction="desc"))[:limit]
        
        for real_repo in repos:
            print(f"\n[PROCESS] Mirroring {real_repo.name}...")
            
            # 1. Create mirror repo in Demo Org
            try:
                mirror_repo = demo_org.create_repo(
                    real_repo.name,
                    description=f"SHADOW CLONE of {real_repo.full_name} - For RADAR Analysis Demo",
                    auto_init=True
                )
                print(f"[OK] Created mirror: {mirror_repo.full_name}")
            except GithubException as e:
                if e.status == 422:
                    print(f"[INFO] Mirror {real_repo.name} already exists.")
                    mirror_repo = demo_org.get_repo(real_repo.name)
                else:
                    print(f"[ERROR] Could not create mirror: {e}")
                    continue

            # 2. Copy README and Context
            try:
                real_readme = real_repo.get_readme()
                content = real_readme.decoded_content.decode("utf-8")
                
                # Append a "Shadow Clone" banner
                banner = f"\n\n---\n> [!CAUTION]\n> This is a **Shadow Clone** of `{real_repo.full_name}` created for the SAMSUNG PRISM RADAR Demo.\n\n"
                
                try:
                    demo_readme = mirror_repo.get_contents("README.md")
                    mirror_repo.update_file(
                        demo_readme.path,
                        "Apply Shadow Clone Mirror",
                        banner + content,
                        demo_readme.sha
                    )
                except GithubException:
                    mirror_repo.create_file("README.md", "Apply Shadow Clone Mirror", banner + content)
                
                print(f"[OK] Mirrored README for {real_repo.name}")
            except Exception as e:
                print(f"[WARN] Could not mirror content for {real_repo.name}: {e}")

    except GithubException as e:
        print(f"[ERROR] Organization access failed: {e}")

def main():
    import sys
    if not GITHUB_TOKEN or not GITHUB_ORG:
        print("[ERROR] GITHUB_TOKEN and GITHUB_ORG must be set.")
        return

    g = Github(GITHUB_TOKEN)
    
    # Check for command line argument
    if len(sys.argv) > 2 and sys.argv[1] == "--target":
        target = sys.argv[2]
    else:
        target = input("Enter the name of the GitHub Organization to Shadow Clone (e.g. 'langchain-ai'): ")
    
    if target:
        mirror_org(g, target)

if __name__ == "__main__":
    main()
