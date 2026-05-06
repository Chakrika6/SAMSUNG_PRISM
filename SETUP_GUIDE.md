# 🛠️ RADAR: Global Setup & Deployment Guide
**Autonomous Research-to-PR Pipeline for Samsung PRISM**

This guide provides a step-by-step walkthrough to set up the RADAR autonomous pipeline on any Windows machine (teammate or judge).

---

## 1. Prerequisites
Ensure the following are installed:
*   **Python 3.9+**: [Download here](https://www.python.org/downloads/)
*   **Git**: [Download here](https://git-scm.com/)
*   **Node.js** (Required for the OpenClaw CLI): [Download here](https://nodejs.org/)

---

## 2. Repository Setup
Clone the repository and enter the project folder:
```bash
git clone <your-repo-url>
cd SAMSUNG_PRISM
```

---

## 3. Environment & Credentials
The pipeline requires four API keys to function. Create a `.env` file in the root directory by duplicating `.env.example`.

### A. Google Gemini API Key
1.  Go to [Google AI Studio](https://aistudio.google.com/).
2.  Click on **"Get API key"** in the left sidebar.
3.  Click **"Create API key in new project"**.
4.  Copy the key and paste it into `GOOGLE_API_KEY` in your `.env`.

### B. Semantic Scholar API Key
1.  Go to the [Semantic Scholar API Dashboard](https://www.semanticscholar.org/product/api).
2.  Sign up for a free developer account.
3.  Generate an API key from your profile settings.
4.  Copy the key and paste it into `SEMANTIC_SCHOLAR_API_KEY`.

### C. GitHub Personal Access Token
1.  Login to GitHub and go to **Settings** > **Developer settings**.
2.  Select **Personal access tokens** > **Tokens (classic)**.
3.  Click **Generate new token (classic)**.
4.  Give it a name and select the **`repo`** checkbox (required for creating PRs).
5.  Click **Generate token**, copy it, and paste it into `GITHUB_TOKEN`.

### D. Telegram Bot & Chat ID
1.  **Get the Bot Token**: Search for `@BotFather` on Telegram and send `/newbot`. Follow instructions to get your `HTTP API Token`.
2.  **Get the Chat ID**:
    *   Create a Telegram Group and add your new bot to it.
    *   Add `@userinfobot` to the group or send a message and then visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` to find the `chat: { id: -100... }`.
    *   Paste the token into `TELEGRAM_BOT_TOKEN` and the ID into `TELEGRAM_CHAT_ID`.

---

## 4. Install Dependencies
Run the following command to install all necessary Python libraries from the requirements file:
```bash
pip install -r requirements.txt
```

---

## 5. OpenClaw Agent Setup
To run the system autonomously (the "Always-On" mode), install the OpenClaw framework:

1.  **Install the CLI**:
    ```bash
    npm install -g openclaw-cli
    ```
2.  **Initialize the Gateway**:
    ```bash
    openclaw setup
    ```
    *Follow the prompts to create your account.*
3.  **Register the Workspace**:
    Point OpenClaw to your current project folder:
    ```bash
    openclaw agents add --id radar --name "RADAR Agent" --path "C:\path\to\SAMSUNG_PRISM"
    ```
4.  **Connect the Config**:
    Ensure the global config (`~/.openclaw/openclaw.json`) points to our skills:
    ```bash
    openclaw skills add --path "C:\path\to\SAMSUNG_PRISM\skills"
    ```

---

## 6. Activate Autonomous Heartbeat
To ensure RADAR wakes up every day without human intervention:

1.  **Enable Cron**: Open `C:\Users\<User>\.openclaw\openclaw.json` and ensure `"cron": { "enabled": true }` is present.
2.  **Add the Job**: Create a folder `~/.openclaw/cron/` if it doesn't exist, and create a `jobs.json` file:
    ```json
    [
      {
        "id": "radar-heartbeat",
        "name": "RADAR Daily Pipeline",
        "enabled": true,
        "schedule": { "kind": "cron", "expr": "0 6 * * *", "tz": "Asia/Kolkata" },
        "sessionTarget": "openclaw",
        "payload": { "text": "/radar-run" }
      }
    ]
    ```
3.  **Restart the Service**:
    ```bash
    openclaw gateway restart
    ```

---

## 7. Testing the Flow
To verify everything is working immediately (without waiting for 6:00 AM):

**Method A: CLI (Quickest)**
```bash
python main.py
```

**Method B: OpenClaw Dashboard (Visual)**
1.  Run `openclaw dashboard`.
2.  In the chat window, type: `/radar-run`.
3.  Watch the agent fetch papers, analyze threats, generate code, and send the Telegram alert in real-time.

---

## ✅ Success Criteria
1.  **New File**: A new `.py` file appears in the `generated/` folder.
2.  **New PR**: A Pull Request is opened on your GitHub repo.
3.  **New Alert**: A "Macro Trend Detected" card appears in your Telegram chat.
