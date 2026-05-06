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

from github import Github
client = genai.Client(api_key=api_key)
g = Github(os.getenv("GITHUB_TOKEN"))

# Define the expected structured output schema using Pydantic
class PendingAction(BaseModel):
    paper_title: str = Field(description="Title of the selected paper")
    url: str = Field(description="URL of the selected paper")
    type: str = Field(description="Type of the alert, e.g., 'Opportunity'")
    reason: str = Field(description="Reason why this paper matches the repository context goals")
    action: str = Field(description="Proposed action to take based on the paper")
    target_entity: str = Field(description="The name of the specific repository in the organization this applies to (e.g. 'galaxy-vision-pipeline')")

def harvest_org_context(org_name):
    """Fetch README/Context from all repos in the organization."""
    if not org_name:
        return "No organization configured. Fallback to local context."
    
    try:
        org = g.get_organization(org_name)
        repos = org.get_repos()
        combined_context = f"ORGANIZATION CONTEXT: {org_name}\n"
        combined_context += "=========================================\n\n"
        
        for repo in repos:
            try:
                readme = repo.get_readme().decoded_content.decode("utf-8")
                combined_context += f"REPOSITORY: {repo.name}\n"
                combined_context += f"DESCRIPTION: {repo.description}\n"
                combined_context += "--- CONTEXT START ---\n"
                combined_context += readme[:2000] # Limit to avoid token overflow
                combined_context += "\n--- CONTEXT END ---\n\n"
            except:
                continue
        return combined_context
    except Exception as e:
        return f"Error harvesting org context: {e}"

def main():
    # File paths based on the contract
    INCOMING_PAPERS_PATH = os.path.join(os.path.dirname(__file__), "..", "contracts", "incoming_papers.json")
    THREAT_PAPERS_PATH = os.path.join(os.path.dirname(__file__), "..", "contracts", "threat_papers.json")
    PENDING_ACTIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "contracts", "pending_actions.json")
    ORG_NAME = os.getenv("GITHUB_ORG")

    # Read the incoming papers
    papers_to_analyze = []
    try:
        with open(INCOMING_PAPERS_PATH, "r", encoding="utf-8") as f:
            papers_to_analyze.extend(json.load(f))
    except Exception as e:
        print(f"Error reading {INCOMING_PAPERS_PATH}: {e}")

    # Read threat papers from competitors
    try:
        if os.path.exists(THREAT_PAPERS_PATH):
            with open(THREAT_PAPERS_PATH, "r", encoding="utf-8") as f:
                threats = json.load(f)
                for t in threats:
                    t["type"] = "Threat" # Force threat type for these
                papers_to_analyze.extend(threats)
    except Exception as e:
        print(f"Error reading {THREAT_PAPERS_PATH}: {e}")

    if not papers_to_analyze:
        print("No papers or threats to analyze.")
        return

    # Live Harvest from GitHub Organization
    print(f"Harvesting live context from Organization: {ORG_NAME}...")
    repo_context = harvest_org_context(ORG_NAME)

    prompt = f"""
    You are an intelligent Samsung R&D research architect. 
    
    Here is the combined context of all repositories in our Organization:
    {repo_context}
    
    Here is a list of recently fetched research papers and competitor threats in JSON format:
    {json.dumps(papers_to_analyze, indent=2)}
    
    Your task:
    1. Analyze the abstracts of these papers against the goals of EVERY repository in the list above.
    2. Identify exactly one highly relevant paper that provides a breakthrough for ONE of the repositories.
    3. Specify which repository (target_entity) this paper belongs to.
    
    Output exactly one JSON object representing the action to take. 
    Do NOT wrap it in a list, just return the JSON object matching the requested schema.
    """

    print("Analyzing intelligence with Gemini 2.0 Flash...")
    try:
        # Require JSON output matching our schema
        # Use gemini-2.0-flash for state-of-the-art performance
        response = client.models.generate_content(
            model="gemini-2.0-flash",
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
