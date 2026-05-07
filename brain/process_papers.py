import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in path (needed when run as subprocess)
sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from brain.llm_client import LLMClient
from pydantic import BaseModel, Field
from typing import List, Optional

class PendingAction(BaseModel):
    paper_title: str
    url: str
    type: str = Field(description="'Opportunity' or 'Threat'")
    reason: str
    action_type: str = Field(description="'PR' if code can be written, 'ISSUE' if high-level research/threat")
    proposed_implementation: str = Field(description="Code snippet or architectural steps")
    target_entity: str = Field(description="The repo name this applies to")

class AnalysisOutput(BaseModel):
    actions: List[PendingAction]

def main():
    base_dir = Path(__file__).parent.parent
    INCOMING_PAPERS_PATH = base_dir / "contracts" / "incoming_papers.json"
    THREAT_PAPERS_PATH = base_dir / "contracts" / "threat_papers.json"
    ORG_PROFILE_PATH = base_dir / "contracts" / "org_profile.json"
    PENDING_ACTIONS_PATH = base_dir / "contracts" / "pending_actions.json"

    # 1. Load Org Context
    if not ORG_PROFILE_PATH.exists():
        print("[ERROR] Org profile not found. Run org_scanner first.")
        return
    with open(ORG_PROFILE_PATH, "r", encoding="utf-8") as f:
        org_context = f.read()

    # 2. Load Papers
    papers = []
    if INCOMING_PAPERS_PATH.exists():
        with open(INCOMING_PAPERS_PATH, "r", encoding="utf-8") as f:
            papers.extend(json.load(f))
    if THREAT_PAPERS_PATH.exists():
        with open(THREAT_PAPERS_PATH, "r", encoding="utf-8") as f:
            threats = json.load(f)
            for t in threats: t["type"] = "Threat"
            papers.extend(threats)

    if not papers:
        print("No papers to analyze.")
        return

    # 3. Analyze across ALL repos
    prompt = f"""
    You are a Research Architect. Match these papers to the organization's repositories.
    
    Organization Context (Profile):
    {org_context}
    
    Research Papers:
    {json.dumps(papers, indent=2)}
    
    Tasks:
    1. For EVERY repo, check if any papers are highly relevant.
    2. If a paper has a clear code implementation -> action_type = 'PR'.
    3. If it is a threat or high-level research -> action_type = 'ISSUE'.
    4. Prioritize 'Threat' papers.
    """

    print(f"[BRAIN] Analyzing {len(papers)} papers across the Organization...")
    llm = LLMClient()
    analysis = llm.generate_json(prompt, AnalysisOutput, "You are an R&D Lead at Samsung.")

    if analysis:
        with open(PENDING_ACTIONS_PATH, "w", encoding="utf-8") as f:
            f.write(analysis.model_dump_json(indent=2))
        print(f"[OK] Generated {len(analysis.actions)} actions.")
    else:
        print("[FAIL] Analysis failed.")

if __name__ == "__main__":
    main()
