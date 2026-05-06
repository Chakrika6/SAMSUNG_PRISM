"""
RADAR — Fetchers Configuration
Member 2: The Data Harvester

All tunable settings for the paper fetcher live here.
Edit this file to change what RADAR monitors.
No code changes needed — just edit the values below.
"""

import os

# ---------------------------------------------------------------------------
# ArXiv topic keywords — papers are fetched for EACH of these queries
# Add or remove keywords here to tune what RADAR watches.
# ---------------------------------------------------------------------------
TOPIC_KEYWORDS = [
    # 1. Core Inference & NPU
    "on-device AI inference optimization",
    "mobile NPU hardware acceleration",
    "quantization for edge devices",

    # 2. Galaxy Vision Pipeline
    "mobile computational photography AI",
    "real-time vision language models",
    "low light image enhancement deep learning",

    # 3. Samsung Knox Security & Privacy
    "on-device federated learning",
    "differential privacy mobile neural network",
    "adversarial robustness lightweight models",

    # 4. SmartThings & AIoT
    "edge computing IoT optimization",
    "low power wireless sensor networks AI",
    "home automation machine learning",
]

# Maximum papers to fetch per keyword from ArXiv
MAX_RESULTS_PER_KEYWORD = 10

# ---------------------------------------------------------------------------
# Competitor institutions — used to flag papers via Semantic Scholar
# ---------------------------------------------------------------------------
COMPETITOR_INSTITUTIONS = [
    "Google Brain",
    "Google DeepMind",
    "Qualcomm AI Research",
    "Meta AI",
    "Microsoft Research",
    "Apple Machine Learning Research",
    "Huawei Noah's Ark Lab",
    "MediaTek Research",
    "ARM Research",
]

# Maximum papers to fetch per competitor institution from Semantic Scholar
MAX_RESULTS_PER_INSTITUTION = 3

# ---------------------------------------------------------------------------
# Semantic Scholar API settings
# ---------------------------------------------------------------------------
SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SEMANTIC_SCHOLAR_FIELDS = "title,abstract,url,authors,externalIds,paperId"
SEMANTIC_SCHOLAR_TIMEOUT = 10  # seconds — hard cut-off, no hanging

# ---------------------------------------------------------------------------
# Output contract path (relative to the fetchers/ folder at runtime)
# ---------------------------------------------------------------------------
OUTPUT_CONTRACT_PATH = "../contracts/incoming_papers.json"

# ---------------------------------------------------------------------------
# Embedding model for semantic relevance scoring
# ---------------------------------------------------------------------------
# all-MiniLM-L6-v2: ~80MB, fast on CPU, high quality sentence embeddings.
# Change this to any sentence-transformers model name if needed.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# Samsung Research Profile (static fallback)
# ---------------------------------------------------------------------------
# Used as the baseline profile for relevance scoring.
# The dynamic profile builder enriches this with Samsung's live ArXiv papers
# and newsroom headlines. If the dynamic build fails, this is used alone.
# ---------------------------------------------------------------------------
SAMSUNG_RESEARCH_PROFILE = """
Samsung is a global technology leader working across several cutting-edge domains.

Galaxy AI and On-Device Intelligence:
Samsung is heavily investing in running large language models, generative AI,
image generation, and multimodal AI directly on mobile devices (Galaxy S and
A series phones) using the Exynos NPU and third-party chips. Key challenges
include model quantization, inference speed under 150ms, memory footprint
reduction, and energy efficiency during continuous AI tasks.

Camera and Computational Photography:
Samsung leads in mobile camera AI — including night photography, super-resolution,
zoom enhancement via neural upscaling, semantic segmentation for portrait mode,
video stabilization, and real-time image signal processing on-device.

Display Technology and Vision AI:
Samsung manufactures OLED and AMOLED displays and researches adaptive refresh,
eye-tracking, gaze estimation, and display-aware content rendering. Research on
video super-resolution and frame interpolation for mobile displays is relevant.

Foldable Devices and Adaptive UX:
Samsung Galaxy Z Fold and Flip are pioneering foldable form factors. Research
on adaptive UI layouts, flexible display durability, multi-window task management,
and context-aware computing for foldables is directly relevant.

Wearables and Health AI:
Galaxy Watch and Galaxy Ring perform continuous health monitoring. Research on
efficient biosignal processing (PPG, ECG, SpO2), on-device health inference,
anomaly detection, and federated learning for privacy-preserving health AI matters.

5G, 6G and Network Intelligence:
Samsung builds 5G base stations and researches 6G. Papers on intelligent
network slicing, beamforming, channel estimation with deep learning, and
AI-driven radio resource management are highly relevant.

Semiconductor and Memory Innovation:
Samsung produces DRAM, NAND flash, and the Exynos SoC. Research on
processing-in-memory (PIM), near-memory computing, memory bandwidth optimization
for AI workloads, and hardware-software co-design for neural networks matters.

Security and Privacy (Samsung Knox):
Samsung Knox is their enterprise security platform. Research on on-device
differential privacy, secure enclaves, federated learning, adversarial robustness,
and confidential computing on mobile hardware is relevant.

SmartThings and AIoT:
Samsung connects billions of IoT devices via SmartThings. Research on
distributed edge inference, tiny machine learning (TinyML), sensor fusion,
and energy-aware scheduling for IoT networks is relevant.

Robotics and Embodied AI:
Samsung is expanding into home robotics and embodied AI agents. Research on
real-time robot perception, navigation, manipulation, and vision-language-action
models is increasingly relevant.
"""

# ---------------------------------------------------------------------------
# Relevance filter settings
# ---------------------------------------------------------------------------
# Minimum cosine similarity score for a paper to be considered relevant.
# Range: 0.0 (keep everything) to 1.0 (exact match only).
# Typical scores for on-topic papers: 0.18-0.35 with all-MiniLM-L6-v2.
RELEVANCE_THRESHOLD = 0.18

# Set to True to print each paper's similarity score during a run (for calibration).
SHOW_RELEVANCE_SCORES = True

# ---------------------------------------------------------------------------
# Dynamic Profile Builder settings
# ---------------------------------------------------------------------------
# ArXiv queries to find Samsung's own published research
SAMSUNG_PROFILE_ARXIV_QUERIES = [
    'au:"Samsung"',
    'all:"Samsung Research"',
    'all:"Samsung Electronics" AND cat:cs.*',
    'all:"Samsung AI" AND cat:cs.*',
]

# Max papers to fetch per profile query
SAMSUNG_PROFILE_MAX_PAPERS_PER_QUERY = 10

# Samsung Newsroom RSS URL for tech announcements
SAMSUNG_NEWSROOM_RSS_URL = "https://news.samsung.com/global/feed"

# Maximum newsroom headlines to include in the profile
SAMSUNG_NEWSROOM_MAX_HEADLINES = 20

# Cache the dynamic profile locally for this many hours before refreshing
PROFILE_CACHE_MAX_AGE_HOURS = 24

# Cache file location (inside fetchers/ folder)
PROFILE_CACHE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".profile_cache.json"
)

# ---------------------------------------------------------------------------
# Trend Fetcher Settings
# ---------------------------------------------------------------------------
ARXIV_TREND_CATEGORIES = ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.NE"]
ARXIV_TREND_MAX_RESULTS = 2000
ARXIV_BASE_URL = "http://export.arxiv.org/api/query"

