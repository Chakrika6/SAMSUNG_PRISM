"""
Member 4 – The Communicator | outputs/auto_pr.py
=================================================
THE AUTO-CODER  🤖⚡
---------------------
God-Tier upgrade: instead of telling engineers *what* to change, RADAR actually
writes the code itself and submits a ready-to-merge Pull Request.
"""

import json
import os
import re
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path
from github import Github, GithubException

# Import our resilient LLM client
from brain.llm_client import LLMClient

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "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")
GITHUB_REPO:  str = os.getenv("GITHUB_REPO",  "Chakrika6/SAMSUNG_PRISM")

# Initialize the resilient client
llm_client = LLMClient()

# Branch prefix for every auto-generated PR
BRANCH_PREFIX = "radar/auto-coder"
PR_LABEL_NAME  = "RADAR: Auto-Coder"
PR_LABEL_COLOR = "6f42c1"

# Paths
SCRIPT_DIR           = Path(__file__).parent
PENDING_ACTIONS_PATH = SCRIPT_DIR.parent / "contracts" / "pending_actions.json"
GENERATED_CODE_DIR   = "generated"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_print(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()

def load_pending_actions() -> list[dict]:
    if not PENDING_ACTIONS_PATH.exists():
        safe_print(f"[ERROR] Contract file not found: {PENDING_ACTIONS_PATH}")
        sys.exit(1)
    with open(PENDING_ACTIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# ---------------------------------------------------------------------------
# Code Generator
# ---------------------------------------------------------------------------

def generate_code(alert: dict) -> str:
    """Uses the resilient LLMClient to write the Python implementation."""
    paper_title   = alert.get("paper_title", "Unknown Paper")
    url           = alert.get("url", "")
    reason        = alert.get("reason", "")
    action        = alert.get("action", "")
    target_entity = alert.get("target_entity", "improved_algorithm")
    entity_type   = alert.get("entity_type", "function")

    system_instr = "You are an expert AI research engineer working at Samsung R&D."
    prompt = textwrap.dedent(f"""
    Write a complete, production-quality Python implementation of the algorithm from:
    PAPER: {paper_title} ({url})
    
    TASK: Implement `{target_entity}` ({entity_type}).
    WHY: {reason}
    ACTION: {action}

    The code must be self-contained, include docstrings, and an example run block.
    Return ONLY raw Python code. No markdown fences.
    """).strip()

    safe_print(f"[RADAR] Generating code for: {target_entity}...")
    code = llm_client.generate_content(prompt, system_instruction=system_instr)

    # Strip accidental markdown fences
    if code.startswith("```"):
        lines = code.splitlines()
        code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    
    return code

# ---------------------------------------------------------------------------
# GitHub Integration
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:48]

def build_pr_body(alert: dict, branch: str, file_path: str, generated_at: str) -> str:
    return textwrap.dedent(f"""
    ## 🤖 RADAR Auto-Coder — Autonomous Pull Request
    > *Generated via Resilient LLM Layer (Gemini -> Groq -> Ollama)*
    
    ### 📄 Source: {alert.get('paper_title')}
    URL: {alert.get('url')}

    ### 🧠 Context
    {alert.get('reason')}

    ### ✅ Review Checklist
    - [ ] Run `python {file_path}` to verify logic.
    - [ ] Approve & Merge.
    """).strip()

def create_pull_request(alert: dict, code: str) -> str:
    g    = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)

    target_entity = alert.get("target_entity", "algorithm")
    slug          = slugify(target_entity)
    timestamp     = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    branch_name   = f"{BRANCH_PREFIX}/{slug}-{timestamp}"
    file_path     = f"{GENERATED_CODE_DIR}/{slug}.py"
    generated_at  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Branch & Commit
    base_sha = repo.get_branch(repo.default_branch).commit.sha
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_sha)
    
    commit_msg = f"feat(auto-coder): implement {target_entity} from ArXiv"
    repo.create_file(path=file_path, message=commit_msg, content=code, branch=branch_name)

    # PR
    pr = repo.create_pull(
        title=f"[RADAR Auto-Coder] {target_entity}",
        body=build_pr_body(alert, branch_name, file_path, generated_at),
        head=branch_name,
        base=repo.default_branch
    )
    return pr.html_url

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    alerts = load_pending_actions()
    candidates = [a for a in alerts if a.get("type", "").lower() == "opportunity" and a.get("target_entity")]

    if not candidates:
        safe_print("[INFO] Nothing to process.")
        return

    for alert in candidates:
        try:
            code = generate_code(alert)
            url = create_pull_request(alert, code)
            safe_print(f"[OK] PR Created: {url}")
        except Exception as e:
            safe_print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
