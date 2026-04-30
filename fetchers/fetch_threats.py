import os
import json
import yaml
import requests
import time
import config

def load_competitors(filepath):
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('competitors', [])

def fetch_threat_papers():
    yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'competitors.yaml')
    competitors = load_competitors(yaml_path)
    
    threat_papers = []
    base_url = getattr(config, "SEMANTIC_SCHOLAR_BASE_URL", "https://api.semanticscholar.org/graph/v1/paper/search")
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    max_saved = getattr(config, "MAX_RESULTS_PER_INSTITUTION", 5)
    timeout = getattr(config, "SEMANTIC_SCHOLAR_TIMEOUT", 10)
    base_fields = getattr(config, "SEMANTIC_SCHOLAR_FIELDS", "title,abstract,url,authors")
    
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    for comp in competitors:
        print(f"Fetching papers for competitor: {comp}")
        params = {
            "query": comp,
            "limit": 50, # Fetch a larger batch since strict filtering will discard many
            "fields": f"{base_fields},authors.affiliations,year"
        }
        
        saved_for_comp = 0
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            for paper in data.get("data", []):
                if saved_for_comp >= max_saved:
                    break
                    
                # Strict verification: Author affiliation OR author name MUST match the competitor string.
                # Avoids massive false positives (e.g. a paper just mentioning "Apple" in abstract)
                is_threat = False
                for author in paper.get("authors", []):
                    affiliations = author.get("affiliations", []) or []
                    if any(comp.lower() in str(aff).lower() for aff in affiliations):
                        is_threat = True
                        break
                    if comp.lower() in author.get("name", "").lower():
                        is_threat = True
                        break
                
                if is_threat:
                    threat_papers.append({
                        "title": paper.get("title", "Unknown Title"),
                        "abstract": paper.get("abstract", "No abstract available."),
                        "url": paper.get("url", ""),
                        "authors": [a.get("name") for a in paper.get("authors", [])],
                        "source": "Semantic Scholar",
                        "competitor": comp
                    })
                    saved_for_comp += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching for {comp}: {e}")
        
        # Rate limit compliance
        time.sleep(1.5)
    
    # Write to contract
    contract_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'contracts', 'threat_papers.json')
    os.makedirs(os.path.dirname(contract_path), exist_ok=True)
    
    with open(contract_path, 'w', encoding='utf-8') as f:
        json.dump(threat_papers, f, indent=4)
    print(f"Saved {len(threat_papers)} strictly verified threat papers to {contract_path}")

if __name__ == "__main__":
    fetch_threat_papers()
