import os
import json
import ast
from google import genai
from pydantic import BaseModel, Field

# Ensure we have the API key
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        api_key = os.environ.get("GOOGLE_API_KEY")
    except ImportError:
        pass

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

client = genai.Client(api_key=api_key)

class PendingAction(BaseModel):
    paper_title: str = Field(description="Title of the selected paper")
    url: str = Field(description="URL of the selected paper")
    type: str = Field(description="Type of the alert, e.g., 'Opportunity'")
    reason: str = Field(description="Reason why this paper matches the repository context goals")
    action: str = Field(description="Proposed action to take based on the paper")
    target_entity: str = Field(description="The specific codebase entity affected by this paper (e.g., function name)")
    entity_type: str = Field(description="The type of the target entity (e.g., 'function', 'class')")

def parse_ast_directory(directory):
    functions = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            functions.append({
                                "name": node.name,
                                "file": os.path.relpath(filepath, directory),
                                "docstring": ast.get_docstring(node) or "No docstring provided."
                            })
                except Exception as e:
                    print(f"Failed to parse {filepath}: {e}")
    return functions

def main():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    TARGET_REPO_DIR = os.path.join(BASE_DIR, "data", "core-inference-engine")
    INCOMING_PAPERS_PATH = os.path.join(BASE_DIR, "contracts", "incoming_papers.json")
    REPO_CONTEXT_PATH = os.path.join(BASE_DIR, "data", "repo_context.md")
    PENDING_ACTIONS_PATH = os.path.join(BASE_DIR, "contracts", "pending_actions.json")

    # 1. Parse AST Graph
    print(f"Parsing AST graph for repository at {TARGET_REPO_DIR}...")
    code_entities = parse_ast_directory(TARGET_REPO_DIR)
    
    # 2. Read context and incoming papers
    with open(INCOMING_PAPERS_PATH, "r", encoding="utf-8") as f:
        incoming_papers = json.load(f)
        
    with open(REPO_CONTEXT_PATH, "r", encoding="utf-8") as f:
        repo_context = f.read()

    # 3. Build Prompt
    prompt = f"""
You are an intelligent research assistant and senior software engineer.

Here is the context and goals of our repository:
{repo_context}

Here are the extracted code entities (functions) from our local codebase:
{json.dumps(code_entities, indent=2)}

Here is a list of recently fetched research papers in JSON format:
{json.dumps(incoming_papers, indent=2)}

Your task:
Analyze the abstracts of these papers against our repository goals and the existing codebase.
Find exactly one highly relevant paper that matches the goals.
Crucially, you must identify WHAT specific code entity this paper affects from the provided codebase entities.

Output exactly one JSON object representing the action to take. 
The "type" field MUST ALWAYS BE exactly the string "Opportunity".
Do NOT wrap it in a list, just return the JSON object matching the requested schema.
"""

    print("Analyzing papers and mapping to codebase using Gemini...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": PendingAction
                }
            )
            
            action_data = json.loads(response.text)
            output_data = [action_data]

            with open(PENDING_ACTIONS_PATH, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2)
                
            print(f"Successfully mapped paper to {action_data.get('target_entity')} and wrote to {PENDING_ACTIONS_PATH}")
            break # Success, exit retry loop

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("Retrying in 5 seconds...")
                import time
                time.sleep(5)
            else:
                print("Error communicating with Gemini after all retries.")
                print("Falling back to Groq API...")
                
                groq_api_key = os.environ.get("GROQ_API_KEY")
                if not groq_api_key:
                    print("GROQ_API_KEY not set. Cannot use fallback.")
                    return
                    
                try:
                    from groq import Groq
                    groq_client = Groq(api_key=groq_api_key)
                    
                    groq_prompt = prompt + "\nEnsure the JSON object has exactly these keys: paper_title, url, type, reason, action, target_entity, entity_type"
                    
                    completion = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "user",
                                "content": groq_prompt
                            }
                        ],
                        response_format={"type": "json_object"}
                    )
                    
                    action_data = json.loads(completion.choices[0].message.content)
                    output_data = [action_data]

                    with open(PENDING_ACTIONS_PATH, "w", encoding="utf-8") as f:
                        json.dump(output_data, f, indent=2)
                        
                    print(f"Successfully mapped paper to {action_data.get('target_entity')} using Groq and wrote to {PENDING_ACTIONS_PATH}")
                    
                except Exception as groq_e:
                    print(f"Groq fallback also failed: {groq_e}")

if __name__ == "__main__":
    main()
