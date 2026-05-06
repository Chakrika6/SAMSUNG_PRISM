import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import config

def fetch_historical_trends():
    categories = getattr(config, "ARXIV_TREND_CATEGORIES", ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.NE"])
    search_query = " OR ".join([f"cat:{c}" for c in categories])
    
    # To get a meaningful 30 days, we need a larger max_results. 
    # 200 was too low and would only pull a few hours of papers.
    max_results = getattr(config, "ARXIV_TREND_MAX_RESULTS", 2000)
    
    # ArXiv doesn't have a direct API endpoint in config, so we use the standard one.
    base_url = getattr(config, "ARXIV_BASE_URL", "http://export.arxiv.org/api/query")
    url = f"{base_url}?search_query={urllib.parse.quote(search_query)}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    print(f"Fetching historical trends from ArXiv (up to {max_results} recent papers)...")
    
    trend_data = []
    try:
        response = urllib.request.urlopen(url)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        for entry in root.findall('atom:entry', ns):
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
                
    except Exception as e:
        print(f"Error fetching from ArXiv: {e}")
        
    contract_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'contracts', 'trend_data_raw.json')
    os.makedirs(os.path.dirname(contract_path), exist_ok=True)
    
    with open(contract_path, 'w', encoding='utf-8') as f:
        json.dump(trend_data, f, indent=4)
        
    print(f"Saved {len(trend_data)} trending papers from the last 30 days to {contract_path}")

if __name__ == "__main__":
    fetch_historical_trends()
