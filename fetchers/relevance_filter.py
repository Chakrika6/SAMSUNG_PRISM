"""
RADAR — Semantic Relevance Filter (Member 2: The Data Harvester)
================================================================
Scores each paper against Samsung's LIVE research profile using
sentence-transformer embeddings + cosine similarity.

The profile is built DYNAMICALLY from Samsung's own ArXiv publications
and Newsroom headlines — no manual updates needed.

How it works:
  1. Build a live Samsung profile via profile_builder.py
  2. Encode the profile into an embedding vector
  3. For each paper, encode (title + abstract) into a paper embedding
  4. Compute cosine similarity between paper and profile
  5. Keep papers whose similarity >= RELEVANCE_THRESHOLD

Model used: all-MiniLM-L6-v2 (~80MB, runs fully offline, no API key needed)
"""

import logging
import os
import sys

log = logging.getLogger("radar.relevance_filter")

# ---------------------------------------------------------------------------
# Load config values
# ---------------------------------------------------------------------------
try:
    from fetchers.config import SAMSUNG_RESEARCH_PROFILE, RELEVANCE_THRESHOLD, EMBEDDING_MODEL_NAME
    from fetchers.profile_builder import build_dynamic_profile
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import SAMSUNG_RESEARCH_PROFILE, RELEVANCE_THRESHOLD, EMBEDDING_MODEL_NAME
    from profile_builder import build_dynamic_profile


# ---------------------------------------------------------------------------
# Embedding model (loaded lazily — only when filter is first called)
# ---------------------------------------------------------------------------
_model = None
_profile_embedding = None


def _get_model():
    """
    Load sentence-transformer model once and cache it.
    Falls back gracefully if sentence-transformers is not installed.
    """
    global _model
    if _model is not None:
        return _model

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        log.error(
            "'sentence-transformers' not installed. "
            "Run: pip install sentence-transformers\n"
            "Falling back to no filtering (all papers kept)."
        )
        return None

    log.info(f"Loading embedding model '{EMBEDDING_MODEL_NAME}' (first run may take ~30s)...")
    _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    log.info("Embedding model loaded.")
    return _model


def _get_profile_embedding(model):
    """
    Build a DYNAMIC Samsung research profile from live sources,
    encode it into an embedding vector, and cache the result.
    Falls back to the static SAMSUNG_RESEARCH_PROFILE if live fetch fails.
    """
    global _profile_embedding
    if _profile_embedding is not None:
        return _profile_embedding

    # Try dynamic profile first
    try:
        profile_text = build_dynamic_profile()
        if not profile_text or len(profile_text.strip()) < 10:
            log.warning("Dynamic profile too short or empty — using static fallback.")
            profile_text = SAMSUNG_RESEARCH_PROFILE
        else:
            log.info("Using DYNAMIC Samsung research profile for scoring.")
    except Exception as exc:
        log.warning(f"Dynamic profile build failed ({exc}) — using static fallback.")
        profile_text = SAMSUNG_RESEARCH_PROFILE

    _profile_embedding = model.encode(
        profile_text,
        convert_to_tensor=True,
        show_progress_bar=False,
    )
    return _profile_embedding


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_papers(papers: list[dict]) -> list[dict]:
    """
    Score each paper against the Samsung Research Profile.
    Returns the same list of papers, each enriched with a
    '_relevance_score' field (float 0.0-1.0).

    If sentence-transformers is unavailable, returns papers unchanged
    (with _relevance_score = 1.0 so nothing is dropped).
    """
    model = _get_model()
    if model is None or not papers:
        # Graceful fallback — no filtering or no papers to score
        for p in papers:
            p["_relevance_score"] = 1.0
        return papers

    profile_emb = _get_profile_embedding(model)

    # Build a batch of paper texts for efficient encoding
    texts = [
        (p.get("title", "") + ". " + p.get("abstract", "")).strip()
        for p in papers
    ]

    log.info(f"Scoring {len(texts)} papers against Samsung Research Profile...")
    paper_embeddings = model.encode(
        texts,
        convert_to_tensor=True,
        show_progress_bar=False,
        batch_size=32,
    )

    # Cosine similarity: dot product of unit vectors
    from sentence_transformers.util import cos_sim
    scores = cos_sim(paper_embeddings, profile_emb)  # shape: (N, 1)

    for i, paper in enumerate(papers):
        paper["_relevance_score"] = float(scores[i][0])

    return papers


def filter_relevant(papers: list[dict], threshold: float = None) -> tuple[list[dict], list[dict]]:
    """
    Filter papers by semantic relevance to Samsung's research profile.

    Args:
        papers:    List of paper dicts (contract schema + optional _relevance_score)
        threshold: Cosine similarity cutoff. Uses RELEVANCE_THRESHOLD from config if None.

    Returns:
        (relevant_papers, dropped_papers)
        Note: '_relevance_score' is removed before returning to keep the contract clean.
    """
    try:
        from fetchers.config import RELEVANCE_THRESHOLD, SHOW_RELEVANCE_SCORES
    except ModuleNotFoundError:
        from config import RELEVANCE_THRESHOLD, SHOW_RELEVANCE_SCORES

    if threshold is None:
        threshold = RELEVANCE_THRESHOLD

    scored = score_papers(papers)

    relevant = []
    dropped = []

    if SHOW_RELEVANCE_SCORES:
        log.info("--- Relevance Scores (threshold=%.2f) ---" % threshold)

    for paper in scored:
        score = paper.pop("_relevance_score", 1.0)  # remove internal field
        title  = paper.get("title", "")[:65]
        decision = "KEEP" if score >= threshold else "DROP"

        if SHOW_RELEVANCE_SCORES:
            log.info(f"  {decision}  [{score:.3f}]  {title}")

        if score >= threshold:
            relevant.append(paper)
        else:
            dropped.append(paper)

    if SHOW_RELEVANCE_SCORES:
        log.info("--- End of scores ---")

    return relevant, dropped

