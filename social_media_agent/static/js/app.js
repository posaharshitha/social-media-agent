/**
 * app.js — Chat UI Logic
 * SocialMind AI · Social Media Agentic AI
 *
 * Handles:
 *  - Message send / receive via fetch POST /chat
 *  - Message rendering with Markdown-lite formatting
 *  - Typing indicator
 *  - Auto-growing textarea
 *  - Quick action buttons
 *  - Copy-to-clipboard
 *  - Toast notifications
 *  - Keyboard shortcuts
 */

(function () {
  "use strict";

  /* ── DOM refs ──────────────────────────────────────────────── */
  const messageInput    = document.getElementById("messageInput");
  const sendBtn         = document.getElementById("sendBtn");
  const messagesContainer = document.getElementById("messagesContainer");
  const typingIndicator = document.getElementById("typingIndicator");
  const charCounter     = document.getElementById("charCounter");
  const toast           = document.getElementById("toast");

  /* ── Set welcome timestamp ─────────────────────────────────── */
  const welcomeTime = document.getElementById("welcomeTime");
  if (welcomeTime) welcomeTime.textContent = formatTime(new Date());

  /* ── State ─────────────────────────────────────────────────── */
  let isSending = false;

  /* ── Utility: format time ──────────────────────────────────── */
  function formatTime(date) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  /* ── Utility: escape HTML ──────────────────────────────────── */
  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /* ── Markdown-lite renderer ────────────────────────────────── */
  function renderMarkdown(text) {
    let html = escapeHtml(text);

    // Disclaimer block (before HR line)
    html = html.replace(
      /---\n⚠️ \*\*AI-Generated Content\*\*([\s\S]*?)$/,
      '<hr/><div class="disclaimer-block">⚠️ <strong>AI-Generated Content</strong>$1</div>'
    );

    // Headers
    html = html.replace(/^### (.+)$/gm, "<h4>$1</h4>");
    html = html.replace(/^## (.+)$/gm,  "<h3>$1</h3>");

    // Bold
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

    // Italic
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    // Inline code
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Numbered list (lookahead)
    html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>)/s, "<ol>$1</ol>");

    // Bullet list
    html = html.replace(/^[-•] (.+)$/gm, "<li>$1</li>");

    // Wrap consecutive <li> in <ul> (simple pass)
    html = html.replace(/(<li>[^<]*<\/li>\n?)+/g, function (match) {
      // check if already inside ol
      return "<ul>" + match + "</ul>";
    });

    // Horizontal rule
    html = html.replace(/^---$/gm, "<hr/>");

    // Paragraphs — double newlines
    html = html
      .split(/\n{2,}/)
      .map(function (block) {
        block = block.trim();
        if (!block) return "";
        if (/^<(h[2-4]|ul|ol|hr|div)/.test(block)) return block;
        return "<p>" + block.replace(/\n/g, "<br/>") + "</p>";
      })
      .join("\n");

    return html;
  }

  /* ── Append a message bubble ───────────────────────────────── */
  function appendMessage(role, text) {
    const isUser = role === "user";
    const time = formatTime(new Date());

    const wrapper = document.createElement("div");
    wrapper.className = "message " + (isUser ? "message-user" : "message-ai");

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = isUser ? "👤" : "🤖";

    const body = document.createElement("div");
    body.className = "message-body";

    const meta = document.createElement("div");
    meta.className = "message-meta";
    meta.innerHTML = isUser
      ? `You <span class="message-time">${time}</span>`
      : `SocialMind AI <span class="message-time">${time}</span>`;

    const bubble = document.createElement("div");
    bubble.className = "message-text";

    if (isUser) {
      bubble.innerHTML = "<p>" + escapeHtml(text) + "</p>";
    } else {
      bubble.innerHTML = renderMarkdown(text);
      // Add copy button for AI messages
      const copyBtn = document.createElement("button");
      copyBtn.className = "btn btn-ghost btn-sm copy-btn";
      copyBtn.style.cssText = "margin-top:0.6rem;font-size:0.75rem;";
      copyBtn.textContent = "📋 Copy";
      copyBtn.addEventListener("click", function () {
        copyToClipboard(text, copyBtn);
      });
      bubble.appendChild(copyBtn);
    }

    body.appendChild(meta);
    body.appendChild(bubble);
    wrapper.appendChild(avatar);
    wrapper.appendChild(body);
    messagesContainer.appendChild(wrapper);

    scrollToBottom();
    return wrapper;
  }

  /* ── Scroll messages to bottom ─────────────────────────────── */
  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  /* ── Show / hide typing indicator ─────────────────────────── */
  function showTyping() {
    typingIndicator.classList.remove("hidden");
    scrollToBottom();
  }

  function hideTyping() {
    typingIndicator.classList.add("hidden");
  }

  /* ── Copy to clipboard ─────────────────────────────────────── */
  function copyToClipboard(text, btn) {
    // Strip the disclaimer trailing text for cleaner copy
    const cleanText = text.replace(/\n\n---\n⚠️ AI-Generated Content[\s\S]*$/, "").trim();
    navigator.clipboard.writeText(cleanText).then(function () {
      const original = btn.textContent;
      btn.textContent = "✅ Copied!";
      setTimeout(function () { btn.textContent = original; }, 1800);
    }).catch(function () {
      showToast("Could not copy. Please select and copy manually.");
    });
  }

  /* ── Toast ─────────────────────────────────────────────────── */
  let toastTimer = null;
  function showToast(message) {
    toast.textContent = message;
    toast.classList.remove("hidden");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toast.classList.add("hidden");
    }, 3000);
  }

  /* ── Send message ──────────────────────────────────────────── */
  function sendMessage() {
    if (isSending) return;
    const text = messageInput.value.trim();
    if (!text) return;

    // Append user message
    appendMessage("user", text);
    messageInput.value = "";
    messageInput.style.height = "auto";
    charCounter.textContent = "0/1000";
    isSending = true;
    sendBtn.disabled = true;
    showTyping();

    // POST to /chat
    fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    })
      .then(function (response) {
        if (response.status === 401) {
          throw new Error("session_expired");
        }
        if (!response.ok) {
          throw new Error("server_error");
        }
        return response.json();
      })
      .then(function (data) {
        hideTyping();
        appendMessage("ai", data.reply);
      })
      .catch(function (err) {
        hideTyping();
        if (err.message === "session_expired") {
          appendMessage(
            "ai",
            "⚠️ Your session has expired. Please [restart the app](/reset) to continue."
          );
        } else {
          appendMessage(
            "ai",
            "⚠️ Something went wrong connecting to the AI. Please check your connection and try again."
          );
        }
      })
      .finally(function () {
        isSending = false;
        sendBtn.disabled = false;
        messageInput.focus();
      });
  }

  /* ── Event: Send button click ──────────────────────────────── */
  sendBtn.addEventListener("click", sendMessage);

  /* ── Event: Enter key sends, Shift+Enter is newline ───────── */
  messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  /* ── Event: Auto-grow textarea ─────────────────────────────── */
  messageInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 160) + "px";
    charCounter.textContent = this.value.length + "/1000";
    if (this.value.length > 900) {
      charCounter.style.color = "#cf222e";
    } else {
      charCounter.style.color = "";
    }
  });

  /* ── Event: Quick action buttons ──────────────────────────── */
  document.querySelectorAll(".quick-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const prompt = this.dataset.prompt;
      if (!prompt) return;
      messageInput.value = prompt;
      messageInput.dispatchEvent(new Event("input"));
      messageInput.focus();
      // On mobile, scroll to input
      messageInput.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });

  /* ── Keyboard shortcut: Ctrl+/ focuses input ──────────────── */
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === "/") {
      e.preventDefault();
      messageInput.focus();
    }
  });

  /* ── Initial scroll ────────────────────────────────────────── */
  scrollToBottom();
})();
