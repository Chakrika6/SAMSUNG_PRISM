import os
import json
from pathlib import Path
from github import Github, GithubException
from google import genai
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def scan_organization():
    """
    Connects to the GitHub Organization, iterates through all repos,
    and extracts their goals/issues to build a global context.
    """
    if not GITHUB_TOKEN or not GITHUB_ORG:
        print("[ERROR] GITHUB_TOKEN and GITHUB_ORG must be set for Org Scanning.")
        return None

    g = Github(GITHUB_TOKEN)
    try:
        org = g.get_organization(GITHUB_ORG)
    except Exception as e:
        print(f"[ERROR] Could not connect to organization {GITHUB_ORG}: {e}")
        return None

    org_summary = {}
    print(f"\n[RADAR] Scanning Organization: {GITHUB_ORG}...")

    # Iterate through all repositories in the organization
    try:
        repos = org.get_repos()
        for repo in repos:
            if repo.archived or repo.fork:
                continue
            
            print(f"   -> Analyzing Repo: {repo.name}")
            
            # 1. Get README content
            readme_content = ""
            try:
                readme = repo.get_contents("README.md")
                readme_content = readme.decoded_content.decode("utf-8")
            except:
                readme_content = "No README found."

            # 2. Get active issues
            issues = []
            try:
                for issue in repo.get_issues(state='open'):
                    if not issue.pull_request: 
                        issues.append(f"- {issue.title}: {issue.body[:200] if issue.body else ''}")
            except:
                pass

            org_summary[repo.name] = {
                "description": repo.description or "No description",
                "readme_snippet": readme_content[:1000], 
                "active_issues": issues[:5] 
            }
    except Exception as e:
        print(f"[ERROR] Failed to list repos: {e}")
        return None

    # 3. Strategy Synthesis
    prompt = f"""
You are the Chief Technology Officer (CTO) for the {GITHUB_ORG} organization.
I have scanned the following repositories and their current status (READMEs and active issues):
{json.dumps(org_summary, indent=2)}

Based on this live data, identify the top 3 core engineering goals for the ENTIRE organization.
Also, generate a list of 5 high-impact research keywords that our research agent should use to find papers on ArXiv/Semantic Scholar to solve these specific problems.

Return your analysis as a PURE JSON object (no markdown formatting):
{{
  "org_name": "{GITHUB_ORG}",
  "global_goals": ["Goal 1", "Goal 2", "Goal 3"],
  "research_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "repo_mapping": {{
    "repo_name": "What this specific repo needs from research"
  }}
}}
"""

    # --- FALLBACK LOGIC: Gemini -> Groq ---
    print("[STRATEGY] Synthesizing Organization-Wide Strategy...")
    
    # Try Gemini first
    try:
        print("   -> Trying Gemini 2.5 Flash...")
        gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as gemini_err:
        print(f"   [WARN] Gemini failed (503/Quota): {gemini_err}")
        
        # Try Groq Fallback
        if GROQ_API_KEY:
            print("   -> Switching to GROQ Fallback (Llama-3)...")
            try:
                groq_client = Groq(api_key=GROQ_API_KEY)
                chat_completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                return json.loads(chat_completion.choices[0].message.content)
            except Exception as groq_err:
                print(f"   [ERROR] Groq fallback also failed: {groq_err}")
        else:
            print("   [ERROR] No GROQ_API_KEY available for fallback.")
            
    return None

def main():
    base_dir = Path(__file__).parent.parent
    org_profile_path = base_dir / "contracts" / "org_profile.json"
    
    profile = scan_organization()
    if profile:
        with open(org_profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)
        print(f"[OK] Organization Profile saved to {org_profile_path}")
    else:
        print("[FAIL] Could not generate Org Profile.")

if __name__ == "__main__":
    main()
