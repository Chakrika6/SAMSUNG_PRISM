import os
import json
import numpy as np
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

def calculate_velocity(papers_in_cluster):
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    
    last_7_count = 0
    last_30_count = 0
    
    for paper in papers_in_cluster:
        # Assuming date is 'YYYY-MM-DD'
        try:
            paper_date = datetime.strptime(paper.get('date', now.strftime('%Y-%m-%d')), '%Y-%m-%d')
        except ValueError:
            paper_date = now
            
        if paper_date >= thirty_days_ago:
            last_30_count += 1
        if paper_date >= seven_days_ago:
            last_7_count += 1
            
    # Simple count for velocity
    return last_7_count

def main():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    TREND_DATA_PATH = os.path.join(BASE_DIR, "contracts", "trend_data_raw.json")
    LIVE_TRENDS_PATH = os.path.join(BASE_DIR, "contracts", "live_trends.json")
    
    if not os.path.exists(TREND_DATA_PATH):
        print(f"Error: {TREND_DATA_PATH} not found.")
        return

    with open(TREND_DATA_PATH, "r", encoding="utf-8") as f:
        papers = json.load(f)

    if not papers:
        print("No papers found in trend data.")
        return

    abstracts = [p.get("abstract", "") for p in papers]
    
    print("Loading SentenceTransformer model...")
    # Use a small, fast model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating embeddings...")
    embeddings = model.encode(abstracts)
    
    print("Clustering papers...")
    # Number of clusters: roughly sqrt of number of papers, max 10
    num_clusters = min(max(2, len(papers) // 2), 10) 
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    kmeans.fit(embeddings)
    
    # Group papers by cluster
    clusters = {i: [] for i in range(num_clusters)}
    for idx, label in enumerate(kmeans.labels_):
        clusters[label].append(papers[idx])
        
    print("Calculating cluster velocities...")
    best_cluster_id = -1
    best_velocity = -1
    
    for cluster_id, cluster_papers in clusters.items():
        velocity = calculate_velocity(cluster_papers)
        if velocity > best_velocity:
            best_velocity = velocity
            best_cluster_id = cluster_id
            
    winning_cluster = clusters[best_cluster_id]
    
    # Summarize the winning cluster
    cluster_categories = [p.get("category", "Unknown") for p in winning_cluster]
    dominant_category = max(set(cluster_categories), key=cluster_categories.count) if cluster_categories else "Unknown"
    
    now = datetime.now()
    fourteen_days_ago = now - timedelta(days=14)
    papers_last_14 = 0
    for p in winning_cluster:
        try:
            pd = datetime.strptime(p.get('date', now.strftime('%Y-%m-%d')), '%Y-%m-%d')
        except ValueError:
            pd = now
        if pd >= fourteen_days_ago:
            papers_last_14 += 1
    
    # Creating an aggressive Telegram card format logic output
    # The Communicator (Member 4) will read this and format it, so we just need to provide the raw info
    trend_output = {
        "cluster_id": int(best_cluster_id),
        "cluster_name": f"Surge in {dominant_category} Research",
        "papers_last_14_days": papers_last_14,
        "key_competitors": ["Google Brain", "Meta AI"], # Mocking this as Member 2 extracts it
        "implication": "Rapid movement detected in this research area. Immediate attention required to maintain competitive edge.",
        "papers": winning_cluster
    }

    with open(LIVE_TRENDS_PATH, "w", encoding="utf-8") as f:
        json.dump([trend_output], f, indent=2) # Output as a list for the Broadcaster
        
    print(f"Successfully analyzed trends and wrote winning cluster to {LIVE_TRENDS_PATH}")

if __name__ == "__main__":
    main()
