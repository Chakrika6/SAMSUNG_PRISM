"""
RADAR — fetchers package
Member 2: The Data Harvester

Public API:
    from fetchers import run_fetcher
    papers = run_fetcher()
"""

from fetchers.paper_fetcher import run_fetcher

__all__ = ["run_fetcher"]
