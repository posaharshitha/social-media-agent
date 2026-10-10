# 🤖 SocialMind AI — Social Media Agentic AI

> **Powered by IBM Granite LLM via IBM watsonx.ai**

A web-based Agentic AI application that generates personalized social media posts, captions, hashtags, content ideas, and posting strategies — tailored to your platform, audience, and communication style. Built with AI ethics, privacy protection, and human-centered (HAM) design at its core.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Post Generator** | Full platform-optimized posts (Instagram, LinkedIn, Twitter/X, Facebook, YouTube, TikTok) |
| **Caption Writer** | Short, engaging captions for images and videos |
| **Hashtag Generator** | Primary, niche, and trending hashtag sets |
| **Content Ideas** | Weekly content calendar suggestions with format recommendations |
| **Posting Tips** | Platform-specific best-time and frequency recommendations |
| **Social Media Q&A** | Strategy, growth, engagement, and algorithm questions |
| **AI Guardrails** | Multi-layer safety filters block harmful or misleading content |
| **Privacy Safe** | No PII stored on disk; session expires on browser close |

---

## 🛠️ Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10 or newer | [python.org/downloads](https://www.python.org/downloads/) |
| pip | Bundled with Python | Upgrade: `python -m pip install --upgrade pip` |
| IBM Cloud Account | — | Free tier available at [cloud.ibm.com](https://cloud.ibm.com) |
| IBM watsonx.ai Project | — | Create at [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com) |

> **Note:** The application also works in **Demo Mode** without IBM credentials. Demo mode returns simulated responses so you can test the full UI flow.

---

## 🚀 Quick Start (Windows — Recommended)

### 1. Download / Clone the project

```
social_media_agent/
├── app.py
├── agent.py
├── requirements.txt
├── .env.example
├── run.bat          ← double-click this
├── PROJECT_PLAN.md
├── README.md
├── templates/
│   ├── index.html
│   └── chat.html
└── static/
    ├── css/style.css
    └── js/app.js
```

### 2. Configure IBM credentials (optional — skip for Demo Mode)

```bat
REM In the social_media_agent folder:
copy .env.example .env
notepad .env
```

Edit `.env`:

```env
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-chat-v2
FLASK_SECRET_KEY=any_long_random_string
```

### 3. Run the application

```bat
run.bat
```

`run.bat` automatically:
1. Checks Python is installed
2. Creates a virtual environment (`venv/`)
3. Installs all dependencies from `requirements.txt`
4. Copies `.env.example` → `.env` if no `.env` exists
5. Launches the Flask server

### 4. Open your browser

```
http://127.0.0.1:5000
```

---

## 🐧 Manual Setup (any OS)

```bash
# 1. Navigate to project directory
cd social_media_agent

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with your IBM credentials

# 6. Run the app
python app.py
```

---

## 🔑 Getting IBM watsonx.ai Credentials

1. Sign up at [cloud.ibm.com](https://cloud.ibm.com) (free tier available)
2. Go to **Manage → Access (IAM) → API Keys** → create a new API key
3. Go to [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
4. Create or open a **watsonx.ai project**
5. Copy the **Project ID** from project settings
6. Choose your regional URL:

| Region | URL |
|--------|-----|
| US South (Dallas) | `https://us-south.ml.cloud.ibm.com` |
| EU Frankfurt | `https://eu-de.ml.cloud.ibm.com` |
| EU London | `https://eu-gb.ml.cloud.ibm.com` |
| Tokyo | `https://jp-tok.ml.cloud.ibm.com` |
| Sydney | `https://au-syd.ml.cloud.ibm.com` |

7. Set these values in your `.env` file

---

## 🎮 How to Use the Application

### Step 1 — Onboarding
Fill in your profile:
- **Name** — personalizes the AI responses
- **Platform** — Instagram / LinkedIn / Twitter/X / Facebook / YouTube / TikTok
- **Content Type** — Educational / Promotional / Motivational / Entertainment / News
- **Target Audience** — describe your audience (e.g., "Young professionals aged 22–35 interested in tech")
- **Language** — English, Hindi, Spanish, French, German, Portuguese, Arabic, Japanese
- **Communication Style** — Professional / Casual / Humorous / Inspirational / Bold & Direct

### Step 2 — Chat with SocialMind AI

| What you want | What to type |
|---------------|-------------|
| A full post | `Write a LinkedIn post about productivity tips` |
| A caption | `Caption for a photo of my team celebrating a milestone` |
| Hashtags | `Hashtags for a fitness motivation Instagram reel` |
| Content ideas | `Give me 5 content ideas for this week on TikTok` |
| Posting advice | `When is the best time to post on Instagram?` |
| Growth strategy | `How do I grow my LinkedIn following organically?` |

### Step 3 — Review and Publish
⚠️ **Always review AI-generated content before publishing.** The app displays a disclaimer on every content output.

### Quick Actions
Use the **Quick Actions** sidebar buttons for one-click prompt starters.

---

## 🛡️ AI Ethics & Safety

| Principle | Implementation |
|-----------|---------------|
| **No harmful content** | Blocked topic patterns + regex safety filter |
| **Input sanitization** | Prompt injection attempts stripped before LLM call |
| **Output filtering** | Response scanned before display |
| **Transparency** | Every AI response is labelled as AI-generated |
| **Human oversight** | Disclaimer on every content output |
| **Privacy** | No PII stored to disk; session-only storage |
| **Fairness** | System prompt instructs model to avoid bias |

---

## 📁 Project Structure

```
social_media_agent/
├── app.py              Flask web application & REST API routes
├── agent.py            AI agent: IBM Granite integration, prompt engineering, guardrails
├── requirements.txt    Python package dependencies
├── .env.example        Environment variable template
├── run.bat             One-click Windows launcher
├── PROJECT_PLAN.md     Full Agentic AI SDLC project plan
├── README.md           This file
├── templates/
│   ├── index.html      Onboarding / profile form page
│   └── chat.html       Chat and content generation interface
└── static/
    ├── css/
    │   └── style.css   Application stylesheet
    └── js/
        └── app.js      Chat UI JavaScript
```

---

## 🔌 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/` | Onboarding form |
| `POST` | `/onboard` | Submit profile, redirect to chat |
| `GET` | `/chat` | Chat interface |
| `POST` | `/chat` | JSON chat API: `{message}` → `{reply, intent, safe}` |
| `GET` | `/reset` | Clear session, return to onboarding |
| `GET` | `/health` | Health check: `{status, llm_ready, mode}` |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web framework |
| `ibm-watsonx-ai` | IBM Granite LLM client SDK |
| `python-dotenv` | Load `.env` configuration |
| `requests` | HTTP utility (transitive dependency) |

---

## ⚙️ Configuration Reference (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WATSONX_API_KEY` | For live mode | — | IBM Cloud API key |
| `WATSONX_PROJECT_ID` | For live mode | — | watsonx.ai project ID |
| `WATSONX_URL` | For live mode | `https://us-south.ml.cloud.ibm.com` | Regional endpoint |
| `GRANITE_MODEL_ID` | No | `ibm/granite-13b-chat-v2` | Granite model to use |
| `FLASK_SECRET_KEY` | Yes | dev default | Session encryption key |
| `FLASK_ENV` | No | `development` | `development` or `production` |
| `PORT` | No | `5000` | Port to run on |

---

## 🧪 Testing

```bash
# Check the health endpoint
curl http://127.0.0.1:5000/health

# Expected response (demo mode):
# {"llm_ready": false, "mode": "demo", "status": "ok"}

# Expected response (live mode):
# {"llm_ready": true, "mode": "live", "status": "ok"}
```

---

## 🔒 Security Notes

- **Never commit `.env`** to version control — it contains your API keys
- The `.env` file is git-ignored by design
- Flask sessions are server-side with `HTTPONLY` and `SameSite=Lax` cookies
- All user input is sanitized before reaching the LLM
- All LLM output is filtered before display

---

## 📋 SDLC Phases Covered

See [`PROJECT_PLAN.md`](PROJECT_PLAN.md) for the complete Agentic AI SDLC documentation:

1. ✅ **Planning** — Use case, stakeholders, ethical boundaries
2. ✅ **Design** — Agent flow, API design, UI wireframes, data schema
3. ✅ **Development** — Flask backend, IBM Granite integration, frontend
4. ✅ **Testing** — Unit, integration, adversarial, manual QA checklist
5. ✅ **Deployment** — `run.bat` launcher, Docker option, cloud deployment
6. ✅ **Maintenance** — Monitoring schedule, update cadence, security audit

---

## 🤝 Responsible AI Statement

SocialMind AI is built with IBM's principles of trustworthy AI:

> *"AI should be transparent, explainable, fair, robust, privacy-preserving, and safe."*

This application:
- Clearly identifies itself as an AI assistant
- Refuses to generate harmful, misleading, or deceptive content
- Reminds users to review all content before publishing
- Does not store personal data beyond the active session
- Applies guardrails at both input and output stages

---

*SocialMind AI · IBM Granite LLM · Always review AI content before publishing.*
