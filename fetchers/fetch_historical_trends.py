import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import config

def fetch_batch(url, retries=3):
    """Fetch a single ArXiv API batch with retry + exponential backoff."""
    for attempt in range(retries):
        try:
            response = urllib.request.urlopen(url)
            return response.read()
        except Exception as e:
            wait = (attempt + 1) * 5  # 5s, 10s, 15s
            print(f"   [WARN] ArXiv request failed (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                print(f"   Retrying in {wait}s...")
                time.sleep(wait)
    return None

def fetch_historical_trends():
    categories = getattr(config, "ARXIV_TREND_CATEGORIES", ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.NE"])
    search_query = " OR ".join([f"cat:{c}" for c in categories])
    
    max_results = getattr(config, "ARXIV_TREND_MAX_RESULTS", 2000)
    batch_size = 200  # ArXiv-friendly batch size
    base_url = getattr(config, "ARXIV_BASE_URL", "http://export.arxiv.org/api/query")
    
    print(f"Fetching historical trends from ArXiv (up to {max_results} papers in batches of {batch_size})...")
    
    trend_data = []
    thirty_days_ago = datetime.now() - timedelta(days=30)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    for start in range(0, max_results, batch_size):
        url = (
            f"{base_url}?search_query={urllib.parse.quote(search_query)}"
            f"&sortBy=submittedDate&sortOrder=descending"
            f"&start={start}&max_results={batch_size}"
        )
        print(f"   Fetching batch {start // batch_size + 1} (papers {start}-{start + batch_size})...")
        
        xml_data = fetch_batch(url)
        if xml_data is None:
            print(f"   [ERROR] Batch {start // batch_size + 1} failed after all retries. Stopping.")
            break
        
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            print(f"   [ERROR] XML parse error: {e}")
            break
            
        entries = root.findall('atom:entry', ns)
        if not entries:
            print(f"   No more entries. Done.")
            break
        
        batch_count = 0
        for entry in entries:
            published_elem = entry.find('atom:published', ns)
            if published_elem is None:
                continue
                
            published_str = published_elem.text
            published_date = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
            
            if published_date >= thirty_days_ago:
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                summary_elem = entry.find('atom:summary', ns)
                abstract = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else ""
                
                cat_elem = entry.find('atom:category', ns)
                category = cat_elem.attrib.get('term', 'unknown') if cat_elem is not None else 'unknown'
                
                trend_data.append({
                    "title": title,
                    "abstract": abstract,
                    "date": published_date.strftime("%Y-%m-%d"),
                    "category": category,
                    "source": "ArXiv"
                })
                batch_count += 1
        
        print(f"   Got {batch_count} papers from this batch (total: {len(trend_data)})")
        
        # Be polite to ArXiv — 3 second delay between batches
        if start + batch_size < max_results and entries:
            time.sleep(3)
                
    contract_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'contracts', 'trend_data_raw.json')
    os.makedirs(os.path.dirname(contract_path), exist_ok=True)
    
    with open(contract_path, 'w', encoding='utf-8') as f:
        json.dump(trend_data, f, indent=4)
        
    print(f"Saved {len(trend_data)} trending papers from the last 30 days to {contract_path}")

if __name__ == "__main__":
    fetch_historical_trends()

