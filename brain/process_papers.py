import os
import sys
import json
import time
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

    # 3. Analyze in BATCHES to stay under token limits
    batch_size = 15
    all_actions = []
    llm = LLMClient()
    
    print(f"[BRAIN] Analyzing {len(papers)} papers in batches of {batch_size}...")
    
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i + batch_size]
        print(f"   Processing batch {i//batch_size + 1}/{(len(papers)-1)//batch_size + 1} ({len(batch)} papers)...")
        
        prompt = f"""
        You are a Research Architect. Match these papers to the organization's repositories.
        
        Organization Context (Profile):
        {org_context}
        
        Research Papers (Batch):
        {json.dumps(batch, indent=2)}
        
        Tasks:
        1. For EVERY repo, check if any papers are highly relevant.
        2. If a paper has a clear code implementation -> action_type = 'PR'.
        3. If it is a threat or high-level research -> action_type = 'ISSUE'.
        4. Prioritize 'Threat' papers.
        """

        analysis = llm.generate_json(prompt, AnalysisOutput, "You are an R&D Lead at Samsung.")
        if analysis and analysis.actions:
            all_actions.extend(analysis.actions)
            print(f"      [+] Found {len(analysis.actions)} actions in this batch.")
        
        # Be polite to APIs
        if i + batch_size < len(papers):
            time.sleep(2)

    # 4. Save consolidated actions
    final_output = AnalysisOutput(actions=all_actions)
    with open(PENDING_ACTIONS_PATH, "w", encoding="utf-8") as f:
        f.write(final_output.model_dump_json(indent=2))
    
    print(f"[OK] Intelligence analysis complete. Total actions generated: {len(all_actions)}")

if __name__ == "__main__":
    main()
