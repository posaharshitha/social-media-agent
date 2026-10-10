"""
agent.py — AI Agent Core
Social Media Agentic AI · IBM Granite LLM via watsonx.ai

Responsibilities:
  - Build platform-aware system prompts
  - Call IBM Granite LLM via ibm-watsonx-ai SDK
  - Apply input & output safety filters (guardrails)
  - Classify user intent and route to appropriate prompt template
  - Inject human-review disclaimer on content outputs
"""

import os
import re

# ── IBM watsonx.ai SDK ────────────────────────────────────────────
try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────
# 1. GUARDRAILS — Blocked topic patterns
# ─────────────────────────────────────────────────────────────────

_BLOCKED_PATTERNS = [
    r"\bhate\b", r"\bracist\b", r"\bhatred\b", r"\bviolence\b",
    r"\bkill\b", r"\bterror\b", r"\bbomb\b", r"\bweapon\b",
    r"\bporn\b", r"\bexplicit\b", r"\bsex\b",
    r"\bmisinformation\b", r"\bfake news\b",
    r"\bscam\b", r"\bfraud\b", r"\billegal\b",
    r"\bmanipulate followers\b", r"\bdeceive\b",
    r"\bpersonal attack\b", r"\bdox\b", r"\bstalk\b",
    r"\bmedical advice\b", r"\blegal advice\b", r"\bfinancial advice\b",
    # Prompt injection attempts
    r"ignore previous instructions",
    r"ignore all instructions",
    r"disregard your system prompt",
    r"you are now",
    r"act as (dan|jailbreak|evil)",
    r"new persona",
]

_BLOCKED_RE = re.compile("|".join(_BLOCKED_PATTERNS), re.IGNORECASE)


def _safety_check(text: str) -> tuple[bool, str]:
    """
    Returns (is_safe, reason).
    is_safe=False means the text must not be processed.
    """
    if _BLOCKED_RE.search(text):
        return False, "blocked_content"
    if len(text.strip()) == 0:
        return False, "empty_input"
    if len(text) > 4000:
        return False, "too_long"
    return True, "ok"


_DISCLAIMER = (
    "\n\n---\n"
    "⚠️ **AI-Generated Content** — Please review this content carefully before publishing. "
    "Ensure it aligns with your brand values, is factually accurate, and complies with "
    "the platform's community guidelines."
)


# ─────────────────────────────────────────────────────────────────
# 2. INTENT CLASSIFICATION
# ─────────────────────────────────────────────────────────────────

_INTENT_PATTERNS = {
    "generate_post":     re.compile(r"\b(write|create|generate|draft|make)\b.{0,30}\b(post|content|status)\b", re.I),
    "generate_caption":  re.compile(r"\b(caption|description|alt text)\b", re.I),
    "generate_hashtags": re.compile(r"\b(hashtag|tag|#)\b", re.I),
    "content_ideas":     re.compile(r"\b(idea|suggest|plan|calendar|topic|what should i post)\b", re.I),
    "posting_tips":      re.compile(r"\b(when|best time|schedule|timing|frequency|how often)\b", re.I),
    "qa":                re.compile(r"\b(how|what|why|explain|tell me|help me understand|tips|advice)\b", re.I),
}


def classify_intent(message: str) -> str:
    """Return the most specific matching intent key, or 'qa' as default."""
    for intent, pattern in _INTENT_PATTERNS.items():
        if pattern.search(message):
            return intent
    return "qa"


# ─────────────────────────────────────────────────────────────────
# 3. PROMPT BUILDER
# ─────────────────────────────────────────────────────────────────

_PLATFORM_CHARS = {
    "Instagram":  "visually rich, emoji-friendly, community-focused",
    "LinkedIn":   "professional, insightful, thought-leadership driven",
    "Twitter/X":  "concise (under 280 chars), punchy, conversation-starting",
    "Facebook":   "conversational, story-driven, shareable",
    "YouTube":    "descriptive, SEO-friendly, engaging thumbnails/titles",
    "TikTok":     "trendy, energetic, short-form video descriptions",
}

_SYSTEM_PROMPT_BASE = """You are SocialMind, a helpful and ethical AI social media strategist powered by IBM Granite.

Your role is to help users create high-quality, authentic, and engaging social media content.

CORE PRINCIPLES:
1. Be helpful, respectful, and human-centered in every response.
2. NEVER generate hateful, violent, misleading, deceptive, explicit, or discriminatory content.
3. NEVER provide medical, legal, or financial advice.
4. NEVER help users deceive, manipulate, or harm other people.
5. Always remind users to review AI-generated content before publishing.
6. Protect user privacy — never ask for or use sensitive personal information.
7. Be transparent: you are an AI assistant, not a human.

CONTENT STYLE:
- Match the user's chosen platform, audience, and communication style.
- Be concise and engaging. Quality over quantity.
- Use inclusive and respectful language.
- Avoid stereotypes or bias in content suggestions.

If a request violates these principles, politely decline and explain why."""


def build_system_prompt(profile: dict) -> str:
    """Construct the full system prompt incorporating the user's profile."""
    platform = profile.get("platform", "general social media")
    platform_style = _PLATFORM_CHARS.get(platform, "engaging and authentic")
    audience = profile.get("audience", "general audience")
    language = profile.get("language", "English")
    style = profile.get("style", "Professional")
    content_type = profile.get("content_type", "general")

    profile_block = f"""
USER PROFILE:
- Name: {profile.get('name', 'User')}
- Platform: {platform} ({platform_style})
- Content Type: {content_type}
- Target Audience: {audience}
- Language: {language}
- Communication Style: {style}

Tailor ALL responses to this profile. Write in {language}. Use a {style.lower()} tone.
"""
    return _SYSTEM_PROMPT_BASE + profile_block


def build_intent_prompt(intent: str, user_message: str, profile: dict) -> str:
    """Return an intent-specific instruction prefix to guide the model."""
    platform = profile.get("platform", "social media")
    audience = profile.get("audience", "your target audience")

    prompts = {
        "generate_post": (
            f"Generate a complete {platform} post for {audience}. "
            f"Include the post body, 2–3 relevant emojis (if appropriate for the platform), "
            f"and 5–8 targeted hashtags. Keep it authentic and on-brand.\n\nUser request: {user_message}"
        ),
        "generate_caption": (
            f"Write a compelling {platform} caption for {audience}. "
            f"Keep it concise, engaging, and platform-appropriate.\n\nUser request: {user_message}"
        ),
        "generate_hashtags": (
            f"Generate 10–15 targeted hashtags for {platform} aimed at {audience}. "
            f"Mix popular and niche hashtags. Format as a space-separated list.\n\nUser request: {user_message}"
        ),
        "content_ideas": (
            f"Suggest 5–7 creative content ideas for {platform} tailored to {audience}. "
            f"For each idea, provide a title, brief description, and content format (reel, carousel, story, etc.)."
            f"\n\nUser request: {user_message}"
        ),
        "posting_tips": (
            f"Provide evidence-based tips on the best times and frequency to post on {platform} "
            f"for maximum engagement with {audience}.\n\nUser request: {user_message}"
        ),
        "qa": (
            f"Answer the following social media question helpfully and accurately. "
            f"If the question is unrelated to social media, politely redirect.\n\nQuestion: {user_message}"
        ),
    }
    return prompts.get(intent, prompts["qa"])


# ─────────────────────────────────────────────────────────────────
# 4. IBM GRANITE LLM CLIENT
# ─────────────────────────────────────────────────────────────────

class GraniteAgent:
    """Wraps IBM watsonx.ai ModelInference with prompt building and guardrails."""

    def __init__(self):
        self.model = None
        self.ready = False
        self._init_model()

    def _init_model(self):
        if not WATSONX_AVAILABLE:
            return

        api_key = os.getenv("WATSONX_API_KEY", "")
        project_id = os.getenv("WATSONX_PROJECT_ID", "")
        url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        model_id = os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-chat-v2")

        if not api_key or not project_id:
            return  # Will use demo mode

        try:
            credentials = Credentials(url=url, api_key=api_key)
            client = APIClient(credentials=credentials, project_id=project_id)
            self.model = ModelInference(
                model_id=model_id,
                api_client=client,
                params={
                    GenParams.MAX_NEW_TOKENS: 800,
                    GenParams.TEMPERATURE: 0.7,
                    GenParams.TOP_P: 0.9,
                    GenParams.REPETITION_PENALTY: 1.1,
                    GenParams.STOP_SEQUENCES: ["<|endoftext|>", "Human:", "User:"],
                },
            )
            self.ready = True
        except Exception as exc:
            print(f"[GraniteAgent] Init warning: {exc}")

    def chat(
        self,
        user_message: str,
        profile: dict,
        history: list[dict],
    ) -> dict:
        """
        Process a user message and return a response dict:
        {
            "text": str,           # Response text to display
            "intent": str,         # Detected intent
            "safe": bool,          # Whether input was safe
            "has_disclaimer": bool # Whether disclaimer was appended
        }
        """
        # ── Input Safety Check ────────────────────────────────────
        is_safe, reason = _safety_check(user_message)
        if not is_safe:
            if reason == "blocked_content":
                return {
                    "text": (
                        "I'm sorry, but I'm unable to help with that request. "
                        "My guidelines prevent me from generating content that could be harmful, "
                        "misleading, or violate community standards. "
                        "I'm here to help you create positive, authentic social media content! "
                        "Feel free to ask about posts, captions, hashtags, or content strategy. 😊"
                    ),
                    "intent": "blocked",
                    "safe": False,
                    "has_disclaimer": False,
                }
            elif reason == "empty_input":
                return {
                    "text": "Please type a message so I can help you!",
                    "intent": "empty",
                    "safe": False,
                    "has_disclaimer": False,
                }
            else:
                return {
                    "text": "Your message is too long. Please keep it under 4000 characters.",
                    "intent": "too_long",
                    "safe": False,
                    "has_disclaimer": False,
                }

        # ── Intent Classification ─────────────────────────────────
        intent = classify_intent(user_message)

        # ── Prompt Construction ───────────────────────────────────
        system_prompt = build_system_prompt(profile)
        intent_prompt = build_intent_prompt(intent, user_message, profile)

        # ── LLM Call ─────────────────────────────────────────────
        if self.ready and self.model:
            response_text = self._call_granite(system_prompt, intent_prompt, history)
        else:
            response_text = self._demo_response(intent, profile, user_message)

        # ── Output Safety Check ───────────────────────────────────
        out_safe, _ = _safety_check(response_text)
        if not out_safe:
            response_text = (
                "I generated a response but it was flagged by my safety filter. "
                "Please rephrase your request and try again."
            )

        # ── Inject Disclaimer for Content Outputs ─────────────────
        content_intents = {"generate_post", "generate_caption", "generate_hashtags", "content_ideas"}
        has_disclaimer = intent in content_intents
        if has_disclaimer:
            response_text += _DISCLAIMER

        return {
            "text": response_text,
            "intent": intent,
            "safe": True,
            "has_disclaimer": has_disclaimer,
        }

    def _call_granite(
        self,
        system_prompt: str,
        user_prompt: str,
        history: list[dict],
    ) -> str:
        """Call IBM Granite via watsonx.ai SDK."""
        # Build conversation context
        conversation = system_prompt + "\n\n"
        for turn in history[-6:]:  # Keep last 6 turns for context window
            role = turn.get("role", "user")
            content = turn.get("content", "")
            conversation += f"{'Human' if role == 'user' else 'Assistant'}: {content}\n"
        conversation += f"Human: {user_prompt}\nAssistant:"

        try:
            result = self.model.generate(prompt=conversation)
            return result["results"][0]["generated_text"].strip()
        except Exception as exc:
            return f"I encountered a technical issue connecting to IBM Granite: {exc}. Please try again."

    def _demo_response(self, intent: str, profile: dict, user_message: str) -> str:
        """
        Demo mode responses when IBM watsonx.ai is not configured.
        These simulate what Granite would return, for local testing.
        """
        name = profile.get("name", "there")
        platform = profile.get("platform", "your platform")
        style = profile.get("style", "Professional").lower()
        audience = profile.get("audience", "your audience")

        if intent == "generate_post":
            return (
                f"✨ Here's a sample {platform} post for you, {name}!\n\n"
                f"---\n"
                f"🚀 Excited to share something new with {audience}!\n\n"
                f"Every great journey starts with a single step — and today, we're taking ours. "
                f"Whether you're just starting out or leveling up, remember: consistency beats perfection every time.\n\n"
                f"What's one small action you'll take today toward your goal? Drop it in the comments! 👇\n\n"
                f"#Growth #Consistency #{'LinkedIn' if platform == 'LinkedIn' else 'Motivation'} "
                f"#PersonalDevelopment #Success #Community #Inspire\n"
                f"---\n\n"
                f"*Note: IBM watsonx.ai is not configured — this is a demo response. "
                f"Add your API credentials to .env to enable real Granite LLM generation.*"
            )
        elif intent == "generate_caption":
            return (
                f"Here's a caption idea for {platform}:\n\n"
                f"*\"The best time to start was yesterday. The second best time is now. 💪\"*\n\n"
                f"Short, punchy, and speaks directly to {audience}.\n\n"
                f"*Demo mode — configure watsonx.ai in .env for live generation.*"
            )
        elif intent == "generate_hashtags":
            return (
                f"Hashtag set for {platform}:\n\n"
                f"**Primary:** #YourBrand #ContentCreator #SocialMediaTips\n"
                f"**Niche:** #GrowthHacking #DigitalMarketing #OnlineCommunity\n"
                f"**Trending-style:** #Motivation #Inspiration #BehindTheScenes\n"
                f"**Audience-specific:** #SmallBusiness #Entrepreneurship #CreativeLife\n\n"
                f"*Demo mode — configure watsonx.ai in .env for personalized hashtags.*"
            )
        elif intent == "content_ideas":
            return (
                f"Here are 5 content ideas for {platform} targeting {audience}:\n\n"
                f"1. **\"Day in the Life\" Series** — Carousel/Reel showing your workflow\n"
                f"2. **Quick Tip Tuesday** — Weekly bite-sized tips (great for Stories)\n"
                f"3. **Behind the Scenes** — Show the process, not just the result\n"
                f"4. **Community Spotlight** — Feature a follower or collaborator\n"
                f"5. **Myth vs. Fact** — Debunk a common misconception in your niche\n\n"
                f"*Demo mode — configure watsonx.ai in .env for AI-personalized ideas.*"
            )
        elif intent == "posting_tips":
            tips = {
                "Instagram": "Tuesdays–Fridays, 9am–11am and 6pm–9pm local time. Post 4–7x per week.",
                "LinkedIn": "Tuesdays–Thursdays, 8am–10am. Post 3–5x per week for best reach.",
                "Twitter/X": "Weekdays 8am–10am and 6pm–9pm. Daily posting recommended.",
                "Facebook": "Wednesdays 11am–1pm. 3–5x per week.",
                "YouTube": "Thursdays–Saturdays. 2–3 videos per week for growing channels.",
                "TikTok": "Tuesday/Thursday/Friday, 7am–9am and 7pm–9pm. Post daily if possible.",
            }
            tip = tips.get(platform, "Weekdays 9am–11am tend to perform well across most platforms.")
            return (
                f"**Best Posting Times for {platform}:**\n\n"
                f"📅 {tip}\n\n"
                f"**General Tips:**\n"
                f"- Post consistently rather than sporadically\n"
                f"- Engage with comments within the first hour of posting\n"
                f"- Use platform analytics to refine your best times over 4–6 weeks\n"
                f"- Test different times and track engagement rate, not just likes\n\n"
                f"*Demo mode — configure watsonx.ai in .env for personalized scheduling advice.*"
            )
        else:  # qa / general
            return (
                f"Great question, {name}! Here's what I can help you with:\n\n"
                f"📝 **Post Generation** — Ask me to write a {platform} post about any topic\n"
                f"🏷️ **Captions & Hashtags** — Get platform-optimized captions and hashtag sets\n"
                f"💡 **Content Ideas** — Request a weekly content plan or topic suggestions\n"
                f"⏰ **Posting Strategy** — Ask about the best times to post on {platform}\n"
                f"📊 **Social Media Q&A** — Ask anything about strategy, engagement, or growth\n\n"
                f"What would you like to create today?\n\n"
                f"*Demo mode — configure watsonx.ai in .env for real IBM Granite responses.*"
            )


# Singleton agent instance
_agent_instance = None


def get_agent() -> GraniteAgent:
    """Return the singleton GraniteAgent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = GraniteAgent()
    return _agent_instance
