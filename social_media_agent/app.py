"""
app.py — Flask Application Entry Point
Social Media Agentic AI · IBM Granite LLM

Routes:
  GET  /           → Onboarding form (index.html)
  POST /onboard    → Save user profile to session, redirect to /chat
  GET  /chat       → Chat interface (chat.html)
  POST /chat       → JSON: { message } → JSON: { reply, intent }
  GET  /reset      → Clear session and return to onboarding
  GET  /health     → Health check endpoint
"""

import os
import json
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
)
from dotenv import load_dotenv
from agent import get_agent

# ── Load environment variables ────────────────────────────────────
load_dotenv()

# ── Flask app setup ───────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-in-production")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ── Supported choices (also used in template rendering) ───────────
PLATFORMS = ["Instagram", "LinkedIn", "Twitter/X", "Facebook", "YouTube", "TikTok"]
CONTENT_TYPES = ["Educational", "Promotional", "Motivational", "Entertainment", "News & Updates"]
LANGUAGES = ["English", "Hindi", "Spanish", "French", "German", "Portuguese", "Arabic", "Japanese"]
STYLES = ["Professional", "Casual", "Humorous", "Inspirational", "Bold & Direct"]


# ─────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    """Landing page — onboarding form."""
    # If user already has a profile, send them to the chat
    if session.get("profile"):
        return redirect(url_for("chat"))
    return render_template(
        "index.html",
        platforms=PLATFORMS,
        content_types=CONTENT_TYPES,
        languages=LANGUAGES,
        styles=STYLES,
    )


@app.route("/onboard", methods=["POST"])
def onboard():
    """Process onboarding form and save profile to session."""
    name = request.form.get("name", "").strip()
    platform = request.form.get("platform", "").strip()
    content_type = request.form.get("content_type", "").strip()
    audience = request.form.get("audience", "").strip()
    language = request.form.get("language", "English").strip()
    style = request.form.get("style", "Professional").strip()

    # Basic validation
    errors = []
    if not name:
        errors.append("Name is required.")
    if platform not in PLATFORMS:
        errors.append("Please select a valid platform.")
    if content_type not in CONTENT_TYPES:
        errors.append("Please select a valid content type.")
    if not audience or len(audience) < 5:
        errors.append("Please describe your target audience (at least 5 characters).")
    if language not in LANGUAGES:
        errors.append("Please select a valid language.")
    if style not in STYLES:
        errors.append("Please select a valid communication style.")

    if errors:
        return render_template(
            "index.html",
            platforms=PLATFORMS,
            content_types=CONTENT_TYPES,
            languages=LANGUAGES,
            styles=STYLES,
            errors=errors,
            form_data=request.form,
        )

    # Save profile to session (server-side only, no PII on disk)
    session["profile"] = {
        "name": name,
        "platform": platform,
        "content_type": content_type,
        "audience": audience,
        "language": language,
        "style": style,
    }
    session["history"] = []  # Conversation history for this session

    return redirect(url_for("chat"))


@app.route("/chat", methods=["GET"])
def chat():
    """Chat interface page."""
    profile = session.get("profile")
    if not profile:
        return redirect(url_for("index"))
    return render_template("chat.html", profile=profile)


@app.route("/chat", methods=["POST"])
def chat_api():
    """
    JSON API endpoint for chat messages.
    Request body: { "message": "..." }
    Response:     { "reply": "...", "intent": "...", "safe": true/false }
    """
    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Session expired. Please restart."}), 401

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message."}), 400

    # Retrieve conversation history
    history = session.get("history", [])

    # Get AI response
    agent = get_agent()
    result = agent.chat(user_message, profile, history)

    # Append to conversation history (keep last 20 turns)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": result["text"]})
    session["history"] = history[-20:]

    return jsonify({
        "reply": result["text"],
        "intent": result["intent"],
        "safe": result["safe"],
        "has_disclaimer": result.get("has_disclaimer", False),
    })


@app.route("/reset", methods=["GET"])
def reset():
    """Clear session and return to onboarding."""
    session.clear()
    return redirect(url_for("index"))


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    agent = get_agent()
    return jsonify({
        "status": "ok",
        "llm_ready": agent.ready,
        "mode": "live" if agent.ready else "demo",
    })


# ─────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    print(f"\n  🤖  Social Media Agentic AI")
    print(f"  🌐  Running at http://127.0.0.1:{port}")
    print(f"  🔑  LLM Mode: {'Live (IBM Granite)' if get_agent().ready else 'Demo (configure .env for live mode)'}")
    print(f"  ⚠️   Press CTRL+C to stop\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
