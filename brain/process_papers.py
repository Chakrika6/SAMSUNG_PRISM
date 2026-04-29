import os
import json
from google import genai
from pydantic import BaseModel, Field

# Ensure we have the API key
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    # Try loading from .env
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        api_key = os.environ.get("GOOGLE_API_KEY")
    except ImportError:
        pass

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it or add it to a .env file in the root directory.")

client = genai.Client(api_key=api_key)

# Define the expected structured output schema using Pydantic
class PendingAction(BaseModel):
    paper_title: str = Field(description="Title of the selected paper")
    url: str = Field(description="URL of the selected paper")
    type: str = Field(description="Type of the alert, e.g., 'Opportunity'")
    reason: str = Field(description="Reason why this paper matches the repository context goals")
    action: str = Field(description="Proposed action to take based on the paper")

def main():
    # File paths based on the contract
    INCOMING_PAPERS_PATH = os.path.join(os.path.dirname(__file__), "..", "contracts", "incoming_papers.json")
    REPO_CONTEXT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "repo_context.md")
    PENDING_ACTIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "contracts", "pending_actions.json")

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
    
    Output exactly one JSON object representing the action to take. 
    Do NOT wrap it in a list, just return the JSON object matching the requested schema.
    """

    # We use gemini-2.5-flash, as it is fully supported on the free tier
    print("Analyzing papers with Gemini 2.5 Flash...")
    try:
        # Require JSON output matching our schema
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": PendingAction
            }
        )
        
        # Parse the JSON string from Gemini
        action_data = json.loads(response.text)
        
        # The contract requires a list of actions
        output_data = [action_data]

        with open(PENDING_ACTIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
            
        print(f"Successfully wrote the selected action to {PENDING_ACTIONS_PATH}")

    except Exception as e:
        print(f"Error communicating with Gemini or writing output: {e}")

if __name__ == "__main__":
    main()
