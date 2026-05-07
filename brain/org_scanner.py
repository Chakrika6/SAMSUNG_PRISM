import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in path (needed when run as subprocess)
sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from github import Github, GithubException
from brain.llm_client import LLMClient
from pydantic import BaseModel, Field
from typing import List, Dict

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG")


class RepoStrategy(BaseModel):
    repo_name: str
    tech_stack: List[str]
    engineering_goals: List[str]
    research_targets: List[str]

class OrgProfile(BaseModel):
    org_name: str
    global_goals: List[str]
    research_keywords: List[str]
    repo_strategies: List[RepoStrategy]

def get_code_vibe(repo):
    """Peek at code files to understand tech stack and patterns."""
    vibe = []
    try:
        contents = repo.get_contents("")
        for file in contents:
            if file.type == "file" and file.name.endswith((".py", ".cpp", ".h", ".js", ".ts", ".go")):
                vibe.append(f"File: {file.name}")
                if len(vibe) >= 3: break # Don't over-scan
        
        # Try to read one main file
        for file in contents:
            if file.name in ["main.py", "app.py", "index.js", "inference.py"]:
                code = file.decoded_content.decode("utf-8")
                vibe.append(f"Sample Code from {file.name}:\n{code[:1000]}")
                break
    except:
        pass
    return "\n".join(vibe)

def scan_organization():
    if not GITHUB_TOKEN or not GITHUB_ORG:
        print("[ERROR] GITHUB_TOKEN and GITHUB_ORG must be set.")
        return None

    g = Github(GITHUB_TOKEN)
    try:
        org = g.get_organization(GITHUB_ORG)
        repos = org.get_repos()
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return None

    org_summary = {}
    print(f"\n[RADAR] Deep Scanning Organization: {GITHUB_ORG}...")

    for repo in repos:
        if repo.archived or repo.fork: continue
        
        print(f"   -> Analyzing Repo: {repo.name} (Code + README)")
        
        readme = ""
        try: readme = repo.get_readme().decoded_content.decode("utf-8")[:1500]
        except: readme = "No README."

        issues = []
        try:
            for issue in repo.get_issues(state='open'):
                if not issue.pull_request:
                    issues.append(f"- {issue.title}")
                    if len(issues) >= 3: break
        except: pass

        code_vibe = get_code_vibe(repo)

        org_summary[repo.name] = {
            "description": repo.description or "",
            "readme": readme,
            "issues": issues,
            "code_vibe": code_vibe
        }

    prompt = f"""
    Analyze these repositories in the '{GITHUB_ORG}' organization.
    Determine the tech stack, engineering goals, and research targets for each.
    Also provide a global research strategy for the whole org.
    
    Data:
    {json.dumps(org_summary, indent=2)}
    """

    print("[STRATEGY] Synthesizing Org Strategy via Resilient LLM...")
    llm = LLMClient()
    return llm.generate_json(prompt, OrgProfile, "You are a CTO building a research roadmap.")

def main():
    base_dir = Path(__file__).parent.parent
    org_profile_path = base_dir / "contracts" / "org_profile.json"
    
    profile = scan_organization()
    if profile:
        with open(org_profile_path, "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json(indent=2))
        print(f"[OK] Deep Org Profile saved to {org_profile_path}")
    else:
        print("[FAIL] Could not generate profile.")

if __name__ == "__main__":
    main()
