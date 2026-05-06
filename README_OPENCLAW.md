# 🚀 RADAR: OpenClaw Agent Integration
**Team:** Samsung PRISM  
**Project:** RADAR (Research Alert & Development Autonomous Robot)

This repository is powered by **OpenClaw**, transforming standard scripts into a continuous, autonomous AI agent that seamlessly bridges the gap between academic research and production code.

## 🌟 What is RADAR?

RADAR is an always-on autonomous agent that proactively monitors global AI research, filters for relevance to Samsung's objectives (like on-device memory optimization and inference latency), and directly writes optimization Pull Requests into our codebase.

**The Pipeline:**
1. **Data Harvester (`fetchers/`):** Scrapes ArXiv and Semantic Scholar for new papers, dropping irrelevant ones using semantic embeddings (`sentence-transformers`).
2. **Brain Engine (`brain/`):** Uses Google Gemini to analyze incoming papers, identifying actionable architectural improvements (e.g., hybrid scaling, KV-cache compression).
3. **Auto-Coder (`outputs/auto_pr.py`):** Acts on Gemini's analysis by autonomously generating Python implementation code and submitting a Pull Request to our GitHub repository.
4. **Communicator (`outputs/send_alert.py`):** Dispatches real-time summary alerts to the team's Telegram group.

---

## ⏰ Autonomous Execution (No Human Intervention)

RADAR is designed for pure zero-touch operation. 

We have configured **OpenClaw's Native Cron Scheduler** (`c:\Users\sahit\.openclaw\cron\jobs.json`) to trigger the `/radar-run` skill **every day at exactly 06:00 AM**. 

Because OpenClaw is running continuously as a background service on your machine, at 6:00 AM the agent wakes up natively and executes the **entire five-step pipeline**:
1. **Scrape**: ArXiv & Semantic Scholar for new research.
2. **Filter**: Drop irrelevant papers using local semantic embeddings.
3. **Analyze**: Brain Engine uses Gemini to find both Code Opportunities and Macro Threats.
4. **Execute**: Auto-Coder generates code and opens a GitHub Pull Request.
5. **Broadcast**: Trend Engine fires beautiful visual threat alerts to the Telegram channel.

Once finished, the agent sends the alerts and goes back to sleep.
### To verify the daily schedule:
```bash
# In your terminal, run:
openclaw cron list
```
*You will see the `RADAR Daily Pipeline` job registered to execute `0 6 * * *`.*

---

## 🤖 OpenClaw Integration Details

This project doesn't just run scripts; it lives as an intelligent agent in the OpenClaw ecosystem.

- **`openclaw/SOUL.md`**: Defines the persona of the RADAR agent—efficient, direct, and focused on Samsung-specific optimizations.
- **`openclaw/HEARTBEAT.md`**: Instructs the agent on its autonomous duties and when to ping the engineers.
- **`openclaw/openclaw.json`**: Connects the workspace to the OpenClaw gateway, granting it permissions to read the codebase and execute the pipeline.

### Chatting with the Agent
Using the OpenClaw dashboard, engineers can bypass the 6:00 AM schedule and interact with the pipeline dynamically:
- Ask RADAR: *"Run the pipeline now"*
- Ask RADAR: *"Summarize the latest fetched papers in incoming_papers.json"*
- Ask RADAR: *"Trigger the auto-coder to create a PR for the latest action"*

---

## ⚙️ Setup & Credentials

All secrets are securely isolated in a `.env` file, meaning the agent can operate continuously in the background without prompting for authentication:
- `GOOGLE_API_KEY`: Powers the Gemini brain engine.
- `SEMANTIC_SCHOLAR_API_KEY`: Defeats rate-limits when scraping competitor institutions.
- `GITHUB_TOKEN`: Grants the auto-coder permission to branch and open PRs.
- `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID`: Connects the communicator to our mobile devices.

RADAR is fully initialized, scheduled, and monitoring. 🔬✨
