"""
RADAR — Dynamic Samsung Research Profile Builder (Member 2)
============================================================
Automatically discovers what Samsung is currently working on by
fetching their recent ArXiv publications and Samsung Newsroom headlines.

Instead of a static, hand-written profile in config.py, this module
builds a LIVE profile from Samsung's own published research.

How it works:
  1. Query ArXiv for papers authored by Samsung Research / Samsung Electronics
  2. Scrape Samsung Newsroom RSS for recent tech announcements
  3. Combine all abstracts + headlines into a dynamic profile string
  4. Fall back to the static SAMSUNG_RESEARCH_PROFILE in config.py if all sources fail

The dynamic profile is refreshed automatically based on PROFILE_CACHE_MAX_AGE_HOURS.
All settings are in config.py — no hardcoded values here.
"""

import logging
import os
import sys
import json
from datetime import datetime

log = logging.getLogger("radar.profile_builder")

# ---------------------------------------------------------------------------
# Load all settings from config.py — nothing hardcoded
# ---------------------------------------------------------------------------
try:
    from fetchers.config import (
        SAMSUNG_RESEARCH_PROFILE,
        SAMSUNG_PROFILE_ARXIV_QUERIES,
        SAMSUNG_PROFILE_MAX_PAPERS_PER_QUERY,
        SAMSUNG_NEWSROOM_RSS_URL,
        SAMSUNG_NEWSROOM_MAX_HEADLINES,
        PROFILE_CACHE_MAX_AGE_HOURS,
        PROFILE_CACHE_FILE,
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import (
        SAMSUNG_RESEARCH_PROFILE,
        SAMSUNG_PROFILE_ARXIV_QUERIES,
        SAMSUNG_PROFILE_MAX_PAPERS_PER_QUERY,
        SAMSUNG_NEWSROOM_RSS_URL,
        SAMSUNG_NEWSROOM_MAX_HEADLINES,
        PROFILE_CACHE_MAX_AGE_HOURS,
        PROFILE_CACHE_FILE,
    )


# ===========================================================================
# 1. Fetch Samsung's own ArXiv papers
# ===========================================================================

def _fetch_samsung_arxiv_papers() -> list[dict]:
    """
    Fetch Samsung's recent ArXiv publications.
    Returns a list of {title, abstract} dicts.
    """
    try:
        import arxiv
    except ImportError:
        log.warning("'arxiv' package not installed — cannot build dynamic profile from ArXiv.")
        return []

    papers = []
    seen_ids = set()

    client = arxiv.Client(
        page_size=SAMSUNG_PROFILE_MAX_PAPERS_PER_QUERY,
        delay_seconds=1.0,
        num_retries=2,
    )

    for query in SAMSUNG_PROFILE_ARXIV_QUERIES:
        log.info(f"  Profile: ArXiv search -> '{query}'")
        search = arxiv.Search(
            query=query,
            max_results=SAMSUNG_PROFILE_MAX_PAPERS_PER_QUERY,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        try:
            for result in client.results(search):
                if result.entry_id in seen_ids:
                    continue
                seen_ids.add(result.entry_id)
                papers.append({
                    "title": result.title.strip(),
                    "abstract": result.summary.strip().replace("\n", " "),
                })
        except Exception as exc:
            log.warning(f"  Profile: ArXiv error for '{query}': {exc}")

    log.info(f"  Profile: Found {len(papers)} Samsung-authored ArXiv papers")
    return papers


# ===========================================================================
# 2. Fetch Samsung Newsroom (RSS)
# ===========================================================================

def _fetch_samsung_newsroom() -> list[str]:
    """
    Fetch recent headlines from Samsung Newsroom RSS.
    Returns a list of headline strings.
    """
    try:
        import requests
    except ImportError:
        return []

    headlines = []

    try:
        resp = requests.get(SAMSUNG_NEWSROOM_RSS_URL, timeout=10)
        if resp.status_code == 200:
            # Simple XML parsing without requiring lxml
            import re
            # Try CDATA-wrapped titles first, then plain titles
            titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", resp.text)
            if not titles:
                titles = re.findall(r"<title>(.*?)</title>", resp.text)
            # Keep all non-empty headlines — they're all Samsung content
            headlines = [t.strip() for t in titles if t.strip()]
            log.info(f"  Profile: Found {len(headlines)} Samsung Newsroom headlines")
        else:
            log.warning(f"  Profile: Samsung Newsroom HTTP {resp.status_code}")
    except Exception as exc:
        log.warning(f"  Profile: Samsung Newsroom error: {exc}")

    return headlines[:SAMSUNG_NEWSROOM_MAX_HEADLINES]


# ===========================================================================
# 3. Cache management
# ===========================================================================

def _load_cache() -> dict | None:
    """Load cached profile if it exists and is fresh enough."""
    if not os.path.exists(PROFILE_CACHE_FILE):
        return None

    try:
        with open(PROFILE_CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        cached_at = datetime.fromisoformat(cache.get("cached_at", "2000-01-01"))
        age_hours = (datetime.now() - cached_at).total_seconds() / 3600
        if age_hours < PROFILE_CACHE_MAX_AGE_HOURS:
            log.info(f"  Profile: Using cached profile ({age_hours:.1f}h old)")
            return cache
        else:
            log.info(f"  Profile: Cache is {age_hours:.1f}h old — refreshing")
    except Exception:
        pass

    return None


def _save_cache(profile_text: str, paper_count: int, headline_count: int) -> None:
    """Save the built profile to a local cache file."""
    try:
        cache = {
            "cached_at": datetime.now().isoformat(),
            "paper_count": paper_count,
            "headline_count": headline_count,
            "profile_text": profile_text,
        }
        with open(PROFILE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        log.info(f"  Profile: Cached to {PROFILE_CACHE_FILE}")
    except Exception as exc:
        log.warning(f"  Profile: Failed to save cache: {exc}")


# ===========================================================================
# 4. Public API: build_dynamic_profile()
# ===========================================================================

def build_dynamic_profile() -> str:
    """
    Build a live Samsung research profile from their ArXiv papers and newsroom.

    Returns:
        A multi-paragraph string describing Samsung's current research focus.
        Falls back to SAMSUNG_RESEARCH_PROFILE from config.py if all sources fail.
    """
    log.info("Building dynamic Samsung research profile...")

    # Check cache first
    cached = _load_cache()
    if cached and cached.get("profile_text"):
        return cached["profile_text"]

    # Fetch from live sources
    arxiv_papers = _fetch_samsung_arxiv_papers()
    newsroom_headlines = _fetch_samsung_newsroom()

    # If we got nothing, fall back to static profile
    if not arxiv_papers and not newsroom_headlines:
        log.warning("  Profile: No live data available — using static profile from config.py")
        return SAMSUNG_RESEARCH_PROFILE

    # Build the profile text
    sections = []

    sections.append(
        "Samsung's current research focus, automatically extracted from their "
        "recent publications and announcements:\n"
    )

    if arxiv_papers:
        sections.append("=== Samsung's Recent Research Papers ===\n")
        for i, paper in enumerate(arxiv_papers, 1):
            sections.append(
                f"Paper {i}: {paper['title']}\n"
                f"Focus: {paper['abstract'][:500]}\n"
            )

    if newsroom_headlines:
        sections.append("\n=== Samsung's Recent Announcements ===\n")
        for headline in newsroom_headlines:
            sections.append(f"- {headline}")

    # Also append the static profile as a baseline
    sections.append(
        "\n\n=== Samsung's Core Research Domains (baseline) ===\n"
        + SAMSUNG_RESEARCH_PROFILE
    )

    profile_text = "\n".join(sections)

    # Cache it
    _save_cache(profile_text, len(arxiv_papers), len(newsroom_headlines))

    log.info(
        f"  Profile: Built from {len(arxiv_papers)} papers + "
        f"{len(newsroom_headlines)} headlines"
    )

    return profile_text
