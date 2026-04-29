"""
Quick validation script — checks contracts/incoming_papers.json matches the required schema.
Run from project root: python fetchers/validate_contract.py
"""
import json
import os
import sys

try:
    from fetchers.config import OUTPUT_CONTRACT_PATH
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import OUTPUT_CONTRACT_PATH

# Resolve the contract path relative to this file's directory (same as paper_fetcher.py)
CONTRACT_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_CONTRACT_PATH)
)
REQUIRED_FIELDS = {"title", "abstract", "url", "authors", "source"}

def main():
    with open(CONTRACT_PATH, encoding="utf-8") as f:
        papers = json.load(f)

    errors = []
    for i, paper in enumerate(papers):
        missing = REQUIRED_FIELDS - set(paper.keys())
        if missing:
            errors.append(f"  Paper [{i}] missing fields: {missing}")
        if not isinstance(paper.get("authors"), list):
            errors.append(f"  Paper [{i}] 'authors' is not a list — got {type(paper.get('authors'))}")
        if not paper.get("url", "").startswith("http"):
            errors.append(f"  Paper [{i}] 'url' looks invalid: {paper.get('url')}")

    print(f"\nContract: {os.path.abspath(CONTRACT_PATH)}")
    print(f"Total papers : {len(papers)}")

    sources = {}
    for p in papers:
        s = p.get("source", "Unknown")
        sources[s] = sources.get(s, 0) + 1
    for src, count in sources.items():
        print(f"  {src:20s}: {count} papers")

    if errors:
        print(f"\n[FAIL] {len(errors)} schema error(s) found:")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print(f"\n[PASS] All {len(papers)} papers pass schema validation. Contract fulfilled. [OK]")

if __name__ == "__main__":
    main()
