# RADAR: Complete Technical Architecture & Implementation Guide

This document is written to give you a deep, under-the-hood understanding of exactly how RADAR will be built. We will avoid abstract "team" terms and focus strictly on **the code, the files, the libraries, and the logic**. 

Even if you aren't a Python expert, reading this will make you understand exactly what your code is going to do at every single step.

---

## 1. The Core Idea (What are we building?)
RADAR is an AI agent that acts like a highly intelligent Chief Technology Officer for a codebase. It continuously reads new research papers from the internet and tells your developers:
1. *"This paper helps fix a bug we are working on."* (Opportunity)
2. *"A competitor just published a paper on the secret project we are building."* (Threat)
3. *"The entire industry is suddenly publishing papers about 'On-Device AI'."* (Trend)

---

## 2. The Tech Stack (What Libraries Are We Using & Why?)

To build this, the Python code will rely on these specific libraries. Here is what they actually do:

* **`requests` & `urllib`:** Basic Python libraries used to talk to the internet (downloading papers).
* **`arxiv` & `semanticscholar`:** Pre-built Python packages that make talking to research databases 10x easier than writing it from scratch.
* **`ast` (Abstract Syntax Tree):** A built-in Python library. Instead of reading code like a text file, `ast` reads code like a tree, allowing the script to instantly extract just the `def function_names()` without getting distracted by the rest of the code.
* **`google-generativeai`:** The official Gemini 1.5 Flash API. We use this because Gemini is brilliant at logic and has a massive 1-million token free tier.
* **`sentence-transformers`:** This library converts text (like a paper's abstract) into a list of numbers (called an **Embedding**). This allows the computer to do math to see how "similar" two papers are to each other.
* **`scikit-learn` (`sklearn`):** A data science library. We use its **K-Means Clustering** algorithm. If you give it 500 papers, K-Means will automatically group them into clumps of similar topics, proving what the industry is focusing on.
* **`python-telegram-bot` & `PyGithub`:** Libraries that let Python automatically send texts to your phone and create Issues on GitHub.

---

## 3. The Folder Structure (Where is the code going and why?)

Before writing any Python, we created 5 specific folders. We did this to enforce **Separation of Concerns**. Instead of having one massive, confusing `app.py` file, the pipeline is broken into clean stages where each folder only talks to the next folder via JSON files.

* **`/fetchers`**: Handles reading the outside world. Only scripts that hit internet APIs (ArXiv, Semantic Scholar) live here.
* **`/brain`**: Handles the logic and AI. Scripts here don't touch the internet—they just read the downloaded text and use Gemini and AST to find matches.
* **`/outputs`**: Handles dispatching alerts. Scripts here take the final matched alerts and send them to Telegram/GitHub.
* **`/contracts`**: The most important folder. Code never jumps between folders. Instead, `/fetchers` saves a JSON here, and `/brain` reads that JSON. It is the "bridge" between the stages.
* **`/data`**: Stores your codebase goals, `repo_context.md`, and private dummy data for testing. 

---

## 4. Step-by-Step Implementation (How & Where Are We Coding It?)

Here is the exact breakdown of the files we are going to write, the libraries they will use, and what the code inside them will actually do.

### Module 1: The Fetcher Layer (Gathering Data)
**Files to be written:** 
* `fetchers/arxiv_fetcher.py`
* `fetchers/scholar_threats.py`

**The Logic (What the code does):**
1. The code imports the `arxiv` library.
2. It sends a search query: `keywords="mobile NPU optimization"`.
3. The API returns a list of papers. 
4. The code loops through the list, rips out the `title`, `abstract`, and `authors`, and saves it locally to a file named `contracts/incoming_papers.json`.
5. For the `scholar_threats.py` script, it does the same thing, but it adds a filter: `if author_institution == "Google Brain": save to threat_papers.json`.

### Module 2: The AST Parser (Understanding Our Own Code)
**Files to be written:** 
* `brain/ast_graph_builder.py`

**The Logic (What the code does):**
1. The code opens the actual Python files in our repository.
2. It uses the `ast.parse()` function. This magically finds every `def` (function) and `class` inside the code, ignoring basic formatting.
3. It takes those function names and docstrings and saves them into a clean little dictionary. Now, RADAR knows exactly what the codebase looks like.

### Module 3: The LLM Matcher (The AI Brain)
**Files to be written:** 
* `brain/gemini_matcher.py`

**The Logic (What the code does):**
1. The code imports `google-generativeai`.
2. It opens `contracts/incoming_papers.json` (from Module 1) and loads the AST dictionary (from Module 2).
3. It builds a massive text prompt: *"Hey Gemini, here are 5 new papers. Here is a list of functions and open Issues from our codebase. Compare them. Tell me if any paper fixes any function or issue."*
4. Gemini's API returns the answer. 
5. The Python code takes Gemini's answer and saves it to `contracts/pending_actions.json` (which will contain the `target_entity` like Issue #42 or a `def`).

### Module 4: Trend Momentum (Data Science)
**Files to be written:**
* `brain/trend_analyzer.py`

**The Logic (What the code does):**
1. It imports `sentence-transformers` and `sklearn`.
2. It takes 1,000 recent papers collected by Module 1.
3. The sentence-transformer turns the 1,000 text abstracts into 1,000 lists of numbers representing their meaning.
4. `sklearn.cluster.KMeans(n_clusters=10)` groups the numbers into 10 distinct "topics".
5. The code calculates which cluster had the most papers added in the last 7 days compared to the last 30 days. The winning cluster is saved as the "Live Trend".

### Module 5: Output Dispatchers (Talking to Humans)
**Files to be written:**
* `outputs/github_agent.py`
* `outputs/telegram_agent.py`

**The Logic (What the code does):**
1. The code imports `PyGithub`.
2. It opens `contracts/pending_actions.json`.
3. For every "Opportunity" generated by Gemini, it authenticates with a GitHub Token, formats a clean Markdown string, and runs `repo.create_issue(title, body)`.
4. It does the exact same thing with `python-telegram-bot` to send a message to your phone.

---

## 5. Execution & Orchestration (How everything connects)

If you have 5 isolated Python scripts, how do they run automatically? This is where **OpenClaw** comes in.

**File to be written:** `main.py`
**The Logic:**
Instead of typing `python fetchers/arxiv.py` manually, we use `main.py` to wrap everything in a schedule.
```python
# Pseudo-code representation of what main.py will do using OpenClaw's Heartbeat
import schedule

def run_radar_pipeline():
    fetchers.fetch_all_papers()     # Module 1 runs
    brain.analyze_threats_and_opportunities() # Modules 2 & 3 run
    outputs.dispatch_alerts()       # Module 5 runs

# Schedule this to run autonomously every morning at 6:00 AM
schedule.every().day.at("06:00").do(run_radar_pipeline)
```

---

## 6. Timeline of Implementation (When are we building what?)

* **Phase 1: API Connections (Days 1-3):** We just want to write the Fetcher and Output scripts. Can we successfully download an ArXiv JSON? Can we successfully send a Telegram message?
* **Phase 2: The Core AI Processing (Days 4-6):** We build the hard stuff. Getting AST to parse our code, getting Gemini to return perfectly formatted matches, and getting K-Means to cluster the trends.
* **Phase 3: Integration & OpenClaw (Days 7-9):** We tie them all into `main.py`. We let it run autonomously in the background. We record the demo video.
