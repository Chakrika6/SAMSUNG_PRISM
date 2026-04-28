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
        print(json.dumps(parsed_output, indent=2))
        
    except Exception as e:
        print(f"Error calling Gemini API or processing response: {e}")

if __name__ == "__main__":
    main()
