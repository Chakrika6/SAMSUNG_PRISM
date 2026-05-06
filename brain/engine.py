import json
import os
from google import genai

# Configure API key from environment variable
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Warning: GOOGLE_API_KEY not found in environment variables. Please set it before running.")

client = genai.Client(api_key=api_key)

def main():
    # Define file paths relative to this script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    incoming_papers_path = os.path.join(base_dir, "contracts", "incoming_papers.json")
    repo_context_path = os.path.join(base_dir, "data", "repo_context.md")
    pending_actions_path = os.path.join(base_dir, "contracts", "pending_actions.json")
    live_trends_path = os.path.join(base_dir, "contracts", "live_trends.json")

    # Read inputs
    try:
        with open(incoming_papers_path, "r", encoding="utf-8") as f:
            papers = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {incoming_papers_path}")
        return

    try:
        with open(repo_context_path, "r", encoding="utf-8") as f:
            context = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {repo_context_path}")
        return

    # Prepare prompt
    prompt = f"""
You are an expert AI researcher and architect.
Here are our current repository goals and context:
---
{context}
---

Here is a list of incoming research papers:
---
{json.dumps(papers, indent=2)}
---

Your task is to analyze these papers and find EXACTLY ONE paper that is highly relevant to our goals.
If multiple papers are relevant, pick the most relevant one.

Return your analysis as a JSON array with exactly one object matching this structure:
[
  {{
    "paper_title": "Paper Title",
    "url": "https://url-to-paper",
    "type": "Opportunity",
    "reason": "Detailed reason why this paper matches our goals.",
    "action": "Suggested action based on the paper"
  }}
]

Make sure the output is valid JSON.
"""

    # Call Gemini API
    print("Analyzing papers with Gemini...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        output_json = response.text
        
        # Validate that it parses as JSON
        parsed_output = json.loads(output_json)
        
        # Ensure it is a list
        if not isinstance(parsed_output, list):
            parsed_output = [parsed_output]
            
        # Save output
        with open(pending_actions_path, "w", encoding="utf-8") as f:
            json.dump(parsed_output, f, indent=2)
            
        print(f"Successfully generated pending actions and saved to {pending_actions_path}")
        
    except Exception as e:
        print(f"Error generating pending actions: {e}")

    # ==============================================================
    # 2. TREND & THREAT ANALYSIS
    # ==============================================================
    prompt_trends = f"""
You are an expert AI trend and threat analyst.
Here are our current repository goals:
---
{context}
---

Here is the list of incoming research papers from competitors and the broader community:
---
{json.dumps(papers, indent=2)}
---

Your task is to identify EXACTLY ONE major emerging trend or competitor threat from these papers that relates to our goals.

Return your analysis as a JSON array with exactly one object matching this structure:
[
  {{
    "cluster_name": "Name of the trend or threat",
    "paper_count": <approximate number of related papers from the list>,
    "timeframe_days": 14,
    "key_competitors": ["Competitor A", "Competitor B"],
    "implication": "What this means for our team's strategy and roadmap",
    "trend_score": <number between 1 and 100 representing severity/importance>,
    "top_paper": {{
      "title": "Most representative paper title",
      "url": "https://url-to-paper"
    }}
  }}
]

Make sure the output is valid JSON.
"""

    print("\nAnalyzing papers for Macro Trends & Threats...")
    try:
        response_trends = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_trends,
            config={"response_mime_type": "application/json"}
        )
        output_trends_json = response_trends.text
        
        parsed_trends = json.loads(output_trends_json)
        
        if not isinstance(parsed_trends, list):
            parsed_trends = [parsed_trends]
            
        with open(live_trends_path, "w", encoding="utf-8") as f:
            json.dump(parsed_trends, f, indent=2)
            
        print(f"Successfully generated trend analysis and saved to {live_trends_path}")
        
    except Exception as e:
        print(f"Error generating trend analysis: {e}")

if __name__ == "__main__":
    main()
