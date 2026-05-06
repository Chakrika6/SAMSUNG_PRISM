import os
import json
from brain.llm_client import LLMClient

# Initialize the resilient client
client = LLMClient()

def main():
    # File paths based on the contract
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INCOMING_PAPERS_PATH = os.path.join(BASE_DIR, "contracts", "incoming_papers.json")
    REPO_CONTEXT_PATH = os.path.join(BASE_DIR, "data", "repo_context.md")
    PENDING_ACTIONS_PATH = os.path.join(BASE_DIR, "contracts", "pending_actions.json")

    # Read the incoming papers
    try:
        with open(INCOMING_PAPERS_PATH, "r", encoding="utf-8") as f:
            incoming_papers = json.load(f)
    except Exception as e:
        print(f"Error reading {INCOMING_PAPERS_PATH}: {e}")
        return

    # Read the repo context
    try:
        with open(REPO_CONTEXT_PATH, "r", encoding="utf-8") as f:
            repo_context = f.read()
    except Exception as e:
        print(f"Error reading {REPO_CONTEXT_PATH}: {e}")
        return

    prompt = f"""
    You are an intelligent research assistant. 
    
    Here is the context and goals of our repository:
    {repo_context}
    
    Here is a list of recently fetched research papers in JSON format:
    {json.dumps(incoming_papers, indent=2)}
    
    Your task:
    Analyze the abstracts of these papers against our repository goals.
    Find exactly one highly relevant paper that matches the goals.
    
    Output exactly one JSON object with this schema:
    {{
        "paper_title": "Title",
        "url": "URL",
        "type": "Opportunity",
        "reason": "Detailed reason",
        "action": "Proposed action",
        "target_entity": "Name of algorithm/function to implement",
        "entity_type": "function or class"
    }}
    Return ONLY the raw JSON. No markdown fences.
    """

    print("Analyzing papers with Resilient LLM (Gemini -> Groq -> Ollama)...")
    try:
        output_text = client.generate_content(prompt)
        
        # Strip potential markdown fences
        if output_text.startswith("```"):
            lines = output_text.splitlines()
            output_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        
        # Parse the JSON string
        action_data = json.loads(output_text)
        
        # The contract requires a list of actions
        output_data = [action_data]

        with open(PENDING_ACTIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
            
        print(f"Successfully wrote the selected action to {PENDING_ACTIONS_PATH}")
        print(json.dumps(output_data, indent=2))

    except Exception as e:
        print(f"Error communicating with LLM or writing output: {e}")

if __name__ == "__main__":
    main()
