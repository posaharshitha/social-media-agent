# Social Media Agentic AI Application — Project Plan

**Project Title:** Social Media Agentic AI Application Using IBM Granite LLM  
**Version:** 1.0.0  
**Date:** 2025  
**Author:** Harshi  
**Stack:** Python · Flask · IBM Granite LLM (via IBM watsonx.ai) · HTML/CSS/JS

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Objectives](#2-objectives)
3. [Agentic AI SDLC Phases](#3-agentic-ai-sdlc-phases)
4. [System Architecture](#4-system-architecture)
5. [Features](#5-features)
6. [AI Ethics & Guardrails](#6-ai-ethics--guardrails)
7. [Technology Stack](#7-technology-stack)
8. [Project File Structure](#8-project-file-structure)
9. [Data Flow](#9-data-flow)
10. [Testing Strategy](#10-testing-strategy)
11. [Deployment Plan](#11-deployment-plan)
12. [Maintenance & Monitoring](#12-maintenance--monitoring)
13. [Risk Management](#13-risk-management)
14. [Timeline](#14-timeline)

---

## 1. Project Overview

This application is a **web-based Agentic AI assistant** that helps individuals, creators, and businesses craft high-quality, personalized social media content. Powered by **IBM Granite LLM** via **IBM watsonx.ai**, the agent collects user preferences through a guided onboarding form and then acts as a personal social media strategist — generating posts, captions, hashtags, content ideas, and scheduling suggestions.

The application follows a **Human-AI Mediated (HAM)** interaction model: the AI assists and suggests, but the human always reviews and approves content before publishing. Ethical guardrails are applied at every generation step.

---

## 2. Objectives

| # | Objective |
|---|-----------|
| 1 | Collect user details (name, platform, content type, audience, language, tone) via an onboarding form |
| 2 | Generate personalized social media posts, captions, and hashtags using IBM Granite LLM |
| 3 | Provide content ideas and optimal posting time suggestions |
| 4 | Allow free-form Q&A about social media strategy and best practices |
| 5 | Enforce AI ethics: no harmful, misleading, or privacy-violating content |
| 6 | Deliver a respectful, helpful, human-centered (HAM) experience |
| 7 | Provide a one-command Windows launcher (`run.bat`) |

---

## 3. Agentic AI SDLC Phases

### Phase 1 — Planning
- Define use case: social media content generation assistant
- Identify stakeholders: individual creators, small businesses, marketing teams
- Establish scope, constraints, and ethical boundaries
- Select IBM Granite as the LLM due to enterprise safety features and watsonx.ai integration
- Define guardrails: no hate speech, no misinformation, no personal data retention

### Phase 2 — Design
- Design conversational agent flow:
  1. Onboarding → collect user profile
  2. Main chat loop → generate content or answer queries
  3. Safety filter → block disallowed content before display
- Design REST API endpoints (`/`, `/onboard`, `/chat`, `/generate`)
- Design UI: onboarding form page + chat interface page
- Design user profile schema (in-memory session, no persistent PII storage)
- Create wireframes for onboarding and chat screens

### Phase 3 — Development
- Set up Python/Flask backend
- Integrate IBM watsonx.ai SDK (`ibm-watsonx-ai`)
- Implement agent logic with system prompt engineering for IBM Granite
- Build safety/guardrail middleware (content classification, topic blocking)
- Develop responsive HTML/CSS/JS frontend
- Implement session-based user profile management
- Write content generation prompts for each platform and content type

### Phase 4 — Testing
- Unit tests: agent functions, safety filter, prompt builder
- Integration tests: API endpoints with mock LLM responses
- End-to-end tests: onboarding flow → content generation
- Adversarial tests: inject harmful prompts to verify guardrails block them
- Usability tests: review UI clarity and response quality
- Performance tests: response latency under expected load

### Phase 5 — Deployment
- Local deployment via `run.bat` (Windows) / `run.sh` (Linux/macOS)
- Environment variables via `.env` file (API keys, model IDs)
- Optional: containerize with Docker for cloud deployment
- Optional: deploy to IBM Cloud Code Engine or any WSGI host

### Phase 6 — Maintenance & Monitoring
- Log all user interactions (anonymized) for quality review
- Monitor LLM response quality monthly
- Update system prompts based on platform algorithm changes
- Review and update guardrail keywords/rules quarterly
- Version-bump IBM watsonx.ai SDK as new Granite models release

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Browser (User)                    │
│   Onboarding Form  ──►  Chat UI  ──►  Results View  │
└──────────────────────────┬──────────────────────────┘
                           │ HTTP (REST/JSON)
┌──────────────────────────▼──────────────────────────┐
│               Flask Web Application                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  /onboard    │  │  /chat       │  │ /generate │  │
│  │  Route       │  │  Route       │  │ Route     │  │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘  │
│         └─────────────────┼────────────────┘         │
│                    ┌──────▼───────┐                  │
│                    │  AI Agent    │                  │
│                    │  (agent.py)  │                  │
│                    │  - Prompt    │                  │
│                    │    Builder   │                  │
│                    │  - Safety    │                  │
│                    │    Filter    │                  │
│                    └──────┬───────┘                  │
└───────────────────────────┼──────────────────────────┘
                            │ IBM watsonx.ai SDK
┌───────────────────────────▼──────────────────────────┐
│              IBM watsonx.ai Platform                 │
│           IBM Granite LLM (granite-13b-chat)         │
└──────────────────────────────────────────────────────┘
```

---

## 5. Features

### 5.1 User Onboarding
- Collect: Full Name, Preferred Platform (Instagram / LinkedIn / Twitter/X / Facebook / YouTube / TikTok), Content Type (Educational / Promotional / Motivational / Entertainment / News), Target Audience description, Preferred Language, Communication Style (Professional / Casual / Humorous / Inspirational)
- Store profile in Flask session (server-side, not logged to disk)

### 5.2 Content Generation
| Feature | Description |
|---------|-------------|
| Post Generator | Full platform-optimized post with body text |
| Caption Generator | Short snappy captions for images/videos |
| Hashtag Generator | Relevant, trending-style hashtag sets |
| Content Ideas | Weekly content calendar suggestions |
| Posting Time Tips | Platform-specific best-time recommendations |

### 5.3 Q&A Assistant
- Answer questions about social media strategy, algorithms, engagement tips, analytics basics, and best practices
- Refuse to answer off-topic, harmful, or privacy-violating questions

### 5.4 Safety & Review Reminder
- Banner on every generated output: *"AI-generated content. Please review before publishing."*
- Input safety check before sending to LLM
- Output safety check before displaying to user

---

## 6. AI Ethics & Guardrails

### Principles Applied
1. **Beneficence** — Content helps users grow their authentic voice
2. **Non-maleficence** — Block generation of harmful, hateful, or misleading content
3. **Privacy** — No user PII is stored persistently; sessions expire on browser close
4. **Transparency** — Every AI response is clearly labelled as AI-generated
5. **Human Oversight** — Users are always reminded to review content before publishing
6. **Fairness** — Prompts are designed to avoid bias in tone and representation

### Guardrail Implementation
- **Blocked topics:** violence, hate speech, political propaganda, personal attacks, medical/legal advice, explicit content, instructions to deceive followers
- **Input sanitization:** strip prompt injection attempts before forwarding to LLM
- **Output filtering:** scan responses for flagged keywords before displaying
- **System prompt hardening:** IBM Granite system prompt explicitly instructs the model to refuse harmful requests
- **Disclaimer injection:** every content output includes a human-review reminder

---

## 7. Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Web Framework | Flask 3.x |
| LLM Provider | IBM watsonx.ai |
| LLM Model | `ibm/granite-13b-chat-v2` |
| Frontend | HTML5 · CSS3 · Vanilla JavaScript |
| Session Management | Flask server-side sessions |
| Environment Config | python-dotenv |
| Deployment (local) | `run.bat` (Windows) |
| Optional Container | Docker |

---

## 8. Project File Structure

```
social_media_agent/
├── app.py                  # Flask application entry point
├── agent.py                # AI agent: prompt builder, LLM calls, safety filter
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── run.bat                 # One-click Windows launcher
├── PROJECT_PLAN.md         # This document
├── README.md               # Setup and run instructions
├── templates/
│   ├── index.html          # Onboarding / landing page
│   └── chat.html           # Chat and content generation interface
└── static/
    ├── css/
    │   └── style.css       # Application stylesheet
    └── js/
        └── app.js          # Chat UI JavaScript
```

---

## 9. Data Flow

1. **User opens app** → `GET /` → renders `index.html` (onboarding form)
2. **User submits profile** → `POST /onboard` → profile saved to Flask session → redirect to `GET /chat`
3. **User sends message** → `POST /chat` (JSON) → agent receives message + session profile
4. **Agent: input safety check** → if blocked, return refusal message
5. **Agent: build prompt** → system prompt + user profile context + conversation history + user message
6. **Agent: call IBM Granite** → via `ibm-watsonx-ai` SDK
7. **Agent: output safety check** → scan response for disallowed content
8. **Agent: inject disclaimer** → append review reminder to content outputs
9. **Response returned** → rendered in chat UI

---

## 10. Testing Strategy

### Unit Tests (`tests/test_agent.py`)
- `test_safety_filter_blocks_hate_speech()`
- `test_safety_filter_allows_normal_request()`
- `test_prompt_builder_includes_user_profile()`
- `test_hashtag_generation_returns_list()`

### Integration Tests (`tests/test_routes.py`)
- `test_onboard_saves_session()`
- `test_chat_returns_200()`
- `test_chat_without_session_redirects()`

### Adversarial Tests
- Send prompts containing hate speech → assert guardrail blocks
- Send prompt injection attempts → assert sanitization strips them
- Request generation of misinformation → assert refusal

### Manual QA Checklist
- [ ] Onboarding form validates all required fields
- [ ] Generated posts match selected platform style
- [ ] Hashtags are relevant to topic
- [ ] Disclaimer appears on all generated content
- [ ] Off-topic questions receive helpful redirect
- [ ] Session clears on browser close

---

## 11. Deployment Plan

### Local (Windows)
```
1. Install Python 3.10+
2. Clone / download project
3. Double-click run.bat  (handles venv + install + launch)
4. Open http://127.0.0.1:5000 in browser
```

### Cloud (Optional)
- Containerize: `docker build -t social-media-agent .`
- Deploy to IBM Cloud Code Engine, Heroku, or any WSGI host
- Set environment variables from `.env.example` in the hosting platform's config

---

## 12. Maintenance & Monitoring

| Activity | Frequency |
|----------|-----------|
| Review LLM response quality samples | Monthly |
| Update guardrail keyword list | Quarterly |
| Upgrade `ibm-watsonx-ai` SDK | On new release |
| Rotate API keys | Every 90 days |
| Review platform best-practice guides | Quarterly |
| Security dependency audit (`pip audit`) | Monthly |

---

## 13. Risk Management

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| LLM generates harmful content | Low | High | Multi-layer guardrails + output filter |
| IBM watsonx.ai API downtime | Low | Medium | Graceful error message; retry logic |
| User submits PII in chat | Medium | Medium | Privacy notice; no PII logging |
| Prompt injection attack | Medium | Medium | Input sanitization before LLM call |
| API key exposed | Low | High | `.env` file; `.gitignore` protection |
| Rate limit exceeded | Medium | Low | Exponential back-off; user feedback |

---

## 14. Timeline

| Week | Milestone |
|------|-----------|
| 1 | Planning, architecture design, environment setup |
| 2 | Backend: Flask app, agent logic, IBM Granite integration |
| 3 | Frontend: onboarding form, chat UI, styling |
| 4 | Guardrails, safety filters, ethical review |
| 5 | Testing (unit, integration, adversarial) |
| 6 | Bug fixes, UX polish, documentation |
| 7 | Deployment scripts, final QA, release |

---

*This plan is a living document and should be updated as the project evolves.*
