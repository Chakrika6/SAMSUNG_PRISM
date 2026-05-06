"""
RADAR — PaperFetcher (Member 2: The Data Harvester)
====================================================
Fetches the latest research papers from:
  1. ArXiv API       — topic-keyword based search
  2. Semantic Scholar — competitor institution monitoring (optional / graceful fallback)

Output contract: overwrites ../contracts/incoming_papers.json
Schema per paper:
  {
    "title":    str,
    "abstract": str,
    "url":      str,
    "authors":  list[str],
    "source":   str   ("ArXiv" | "SemanticScholar")
  }

Run standalone:
    cd <project_root>
    python fetchers/paper_fetcher.py
"""

import json
import os
import sys
import logging
from datetime import datetime

# Semantic relevance filter (fetchers/relevance_filter.py)
try:
    from fetchers.relevance_filter import filter_relevant
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from relevance_filter import filter_relevant

# ---------------------------------------------------------------------------
# Local config (fetchers/config.py)
# ---------------------------------------------------------------------------
try:
    from fetchers.config import (
        TOPIC_KEYWORDS,
        MAX_RESULTS_PER_KEYWORD,
        COMPETITOR_INSTITUTIONS,
        MAX_RESULTS_PER_INSTITUTION,
        OUTPUT_CONTRACT_PATH,
        SEMANTIC_SCHOLAR_BASE_URL,
        SEMANTIC_SCHOLAR_FIELDS,
        SEMANTIC_SCHOLAR_TIMEOUT,
    )
except ModuleNotFoundError:
    # Allow running directly as a script: python fetchers/paper_fetcher.py
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import (
        TOPIC_KEYWORDS,
        MAX_RESULTS_PER_KEYWORD,
        COMPETITOR_INSTITUTIONS,
        MAX_RESULTS_PER_INSTITUTION,
        OUTPUT_CONTRACT_PATH,
        SEMANTIC_SCHOLAR_BASE_URL,
        SEMANTIC_SCHOLAR_FIELDS,
        SEMANTIC_SCHOLAR_TIMEOUT,
    )

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("radar.fetcher")


# ===========================================================================
# 1. ArXiv Fetcher
# ===========================================================================

def fetch_from_arxiv(keywords: list[str], max_per_keyword: int) -> list[dict]:
    """
    Query ArXiv for recent papers matching each keyword.
    Returns a deduplicated list of papers in contract schema format.
    """
    try:
        import arxiv
    except ImportError:
        log.error("'arxiv' package not installed. Run: pip install arxiv")
        return []

    papers: list[dict] = []
    seen_ids: set[str] = set()

    client = arxiv.Client(
        page_size=max_per_keyword,
        delay_seconds=1.0,   # be polite to the ArXiv API
        num_retries=3,
    )

    for keyword in keywords:
        log.info(f"ArXiv search → '{keyword}'")
        search = arxiv.Search(
            query=keyword,
            max_results=max_per_keyword,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        fetched_count = 0
        try:
            for result in client.results(search):
                paper_id = result.entry_id  # e.g. "http://arxiv.org/abs/2401.00001v1"

                if paper_id in seen_ids:
                    log.debug(f"  Duplicate skipped: {result.title[:60]}")
                    continue

                seen_ids.add(paper_id)
                papers.append({
                    "title":    result.title.strip(),
                    "abstract": result.summary.strip().replace("\n", " "),
                    "url":      result.entry_id,
                    "authors":  [a.name for a in result.authors],
                    "source":   "ArXiv",
                })
                fetched_count += 1

        except Exception as exc:
            log.warning(f"  ArXiv error for '{keyword}': {exc}")

        log.info(f"  → {fetched_count} new papers added (total so far: {len(papers)})")

    return papers


# ===========================================================================
# 2. Semantic Scholar Fetcher (competitor institution monitoring)
# ===========================================================================

def fetch_from_semantic_scholar(
    institutions: list[str],
    max_per_institution: int,
    existing_urls: set[str],
) -> list[dict]:
    """
    Query Semantic Scholar for papers from competitor institutions.
    Uses raw HTTP requests with a hard timeout — no auto-retry on 429.
    Returns [] gracefully if rate-limited or on any error.
    """
    try:
        import requests
    except ImportError:
        log.warning("'requests' not available — skipping Semantic Scholar.")
        return []

    papers: list[dict] = []

    for institution in institutions:
        log.info(f"Semantic Scholar → competitor: '{institution}'")
        # Read the API key from environment
        import os
        from dotenv import load_dotenv
        import time
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
        api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

        try:
            headers = {}
            if api_key and api_key != "your_semantic_scholar_api_key_here":
                headers["x-api-key"] = api_key

            resp = requests.get(
                SEMANTIC_SCHOLAR_BASE_URL,
                params={
                    "query":  institution,
                    "fields": SEMANTIC_SCHOLAR_FIELDS,
                    "limit":  max_per_institution,
                },
                headers=headers,
                timeout=SEMANTIC_SCHOLAR_TIMEOUT,
            )
            time.sleep(1.1)  # Respect 1 req/sec limit

            if resp.status_code == 429:
                log.warning(f"  Rate-limited (429) for '{institution}' — skipping.")
                continue
            if resp.status_code != 200:
                log.warning(f"  HTTP {resp.status_code} for '{institution}' — skipping.")
                continue

            data = resp.json().get("data", [])
            added = 0
            for paper in data:
                paper_id = paper.get("paperId")
                url = (
                    f"https://www.semanticscholar.org/paper/{paper_id}"
                    if paper_id else None
                )
                if not url or url in existing_urls:
                    continue

                existing_urls.add(url)
                abstract = paper.get("abstract") or ""
                authors  = [a.get("name", "") for a in paper.get("authors", [])]

                papers.append({
                    "title":    (paper.get("title") or "").strip(),
                    "abstract": abstract.strip().replace("\n", " "),
                    "url":      url,
                    "authors":  authors,
                    "source":   "SemanticScholar",
                })
                added += 1

            log.info(f"  → {added} competitor papers added from '{institution}'")

        except Exception as exc:
            log.warning(f"  Semantic Scholar error for '{institution}': {exc}")

    return papers


# ===========================================================================
# 3. Write contract
# ===========================================================================

def write_contract(papers: list[dict], output_path: str) -> None:
    """
    Overwrite the incoming_papers.json contract file with clean JSON.
    """
    abs_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    with open(abs_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)

    log.info(f"Contract written → {abs_path}  ({len(papers)} papers)")


# ===========================================================================
# 4. Main entry point
# ===========================================================================

def run_fetcher() -> list[dict]:
    """
    Public entry point called by main.py heartbeat.
    Returns the list of papers written to the contract.
    """
    log.info("=" * 60)
    log.info(f"RADAR PaperFetcher started  [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    log.info("=" * 60)

    # 0. Dynamic Context Injection (New)
    # Check for org_profile.json generated by Step 0 (Org Scanner)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile_path = os.path.join(base_dir, "contracts", "org_profile.json")
    
    current_keywords = TOPIC_KEYWORDS
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
                new_keywords = profile.get("research_keywords", [])
                if new_keywords:
                    log.info(f"Using dynamic keywords from Org Profile: {new_keywords}")
                    current_keywords = new_keywords
        except Exception as e:
            log.warning(f"Failed to read org_profile.json: {e}")

    # Step 1: ArXiv — topic keyword search
    arxiv_papers = fetch_from_arxiv(current_keywords, MAX_RESULTS_PER_KEYWORD)

    # Build a set of URLs already seen for deduplication across sources
    existing_urls: set[str] = {p["url"] for p in arxiv_papers}

    # Step 2: Semantic Scholar — competitor institution monitoring
    ss_papers = fetch_from_semantic_scholar(
        COMPETITOR_INSTITUTIONS,
        MAX_RESULTS_PER_INSTITUTION,
        existing_urls,
    )

    # Step 3: Merge all fetched papers
    all_papers = arxiv_papers + ss_papers
    raw_count = len(all_papers)

    # Step 4: Semantic relevance filter
    # Scores every paper against the Samsung Research Profile using
    # sentence-transformer embeddings. No hardcoded keyword lists.
    log.info(f"Running semantic relevance filter on {raw_count} papers...")
    relevant_papers, dropped_papers = filter_relevant(all_papers)
    dropped = len(dropped_papers)
    log.info(
        f"Relevance filter: {len(relevant_papers)} kept, "
        f"{dropped} dropped as not relevant to Samsung."
    )

    # Step 5: Resolve output path relative to *this file's* location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.normpath(os.path.join(script_dir, OUTPUT_CONTRACT_PATH))

    # Step 6: Write contract
    write_contract(relevant_papers, output_path)

    # Summary
    log.info("-" * 60)
    log.info(f"  ArXiv fetched      : {len(arxiv_papers)}")
    log.info(f"  SemanticScholar    : {len(ss_papers)}")
    log.info(f"  Not Samsung-relevant (dropped) : {dropped}")
    log.info(f"  Samsung-relevant (written)     : {len(relevant_papers)}")
    log.info("  Contract fulfilled [OK]")
    log.info("=" * 60)

    return relevant_papers


# ---------------------------------------------------------------------------
# Allow running as a standalone script for testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_fetcher()
