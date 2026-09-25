/**
 * Easeprompt Client-Side Application Controller
 * Pure built-in prompt generation engine with live streaming,
 * one-click copy, and markdown rendering.
 */

// Application State
const state = {
  currentPromptText: "",
  targetAgent: "coding_assistant",
  isGenerating: false,
  viewMode: "rendered" // "rendered" | "raw"
};

// DOM Elements
const elements = {
  // Input elements
  promptInput: document.getElementById("promptInput"),
  charCount: document.getElementById("charCount"),
  clearInputBtn: document.getElementById("clearInputBtn"),
  clarifyBox: document.getElementById("clarifyBox"),
  clarifyChips: document.getElementById("clarifyChips"),
  categoryPills: document.getElementById("categoryPills"),
  presetChips: document.getElementById("presetChips"),
  generateBtn: document.getElementById("generateBtn"),

  // Output elements
  statsBadge: document.getElementById("statsBadge"),
  toggleViewBtn: document.getElementById("toggleViewBtn"),
  toggleViewText: document.getElementById("toggleViewText"),
  downloadBtn: document.getElementById("downloadBtn"),
  copyBtn: document.getElementById("copyBtn"),
  streamLine: document.getElementById("streamLine"),
  renderedOutput: document.getElementById("renderedOutput"),
  rawOutput: document.getElementById("rawOutput"),

  // Toasts
  toastContainer: document.getElementById("toastContainer")
};

// Broad / Underspecified keywords that benefit from clarification archetypes
const BROAD_SEEDS = new Set([
  "app", "apps", "an app", "the app", "application", "website", "web app",
  "mobile app", "tool", "saas", "game", "dashboard", "bot", "script", "software"
]);

function isBroadSeed(text) {
  const clean = text.replace(/[^a-zA-Z0-9\s]/g, "").trim().toLowerCase();
  const words = clean.split(/\s+/).filter(Boolean);
  if (words.length === 0) return false;
  if (BROAD_SEEDS.has(clean)) return true;
  if (words.length <= 2) {
    const lastWord = words[words.length - 1];
    if (BROAD_SEEDS.has(lastWord)) {
      const prefix = words[0];
      if (["build", "make", "create", "develop", "code", "design", "new", "simple", "a", "an", "the", "my"].includes(prefix)) {
        return true;
      }
    }
  }
  return false;
}

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
  // Input live character counter and broad seed detection
  elements.promptInput.addEventListener("input", () => {
    const text = elements.promptInput.value;
    const len = text.length;
    elements.charCount.textContent = `${len} character${len === 1 ? "" : "s"}`;

    if (elements.clarifyBox) {
      if (isBroadSeed(text)) {
        elements.clarifyBox.style.display = "block";
      } else {
        elements.clarifyBox.style.display = "none";
      }
    }
  });

  // Clear button
  elements.clearInputBtn.addEventListener("click", () => {
    elements.promptInput.value = "";
    elements.charCount.textContent = "0 characters";
    if (elements.clarifyBox) elements.clarifyBox.style.display = "none";
    elements.promptInput.focus();
  });

  // Keyboard shortcut: Ctrl + Enter / Cmd + Enter
  elements.promptInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      startPromptGeneration();
    }
  });

  // Clarification archetype chips
  if (elements.clarifyChips) {
    elements.clarifyChips.querySelectorAll(".clarify-chip").forEach(chip => {
      chip.addEventListener("click", () => {
        const template = chip.dataset.template;
        elements.promptInput.value = template;
        elements.charCount.textContent = `${template.length} characters`;
        if (elements.clarifyBox) elements.clarifyBox.style.display = "none";
        
        // Select Coding category
        state.targetAgent = "coding_assistant";
        elements.categoryPills.querySelectorAll(".pill").forEach(p => {
          const match = p.dataset.agent === "coding_assistant";
          p.classList.toggle("active", match);
          p.setAttribute("aria-checked", match ? "true" : "false");
        });

        elements.promptInput.focus();
        showToast("Archetype selected! Click Generate Prompt or customize details.", "info");
      });
    });
  }

  // Category Pills
  elements.categoryPills.querySelectorAll(".pill").forEach(pill => {
    pill.addEventListener("click", () => {
      elements.categoryPills.querySelectorAll(".pill").forEach(p => {
        p.classList.remove("active");
        p.setAttribute("aria-checked", "false");
      });
      pill.classList.add("active");
      pill.setAttribute("aria-checked", "true");
      state.targetAgent = pill.dataset.agent || "coding_assistant";
    });
  });

  // Preset Chips
  elements.presetChips.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const text = btn.dataset.text;
      const agent = btn.dataset.agent;
      
      elements.promptInput.value = text;
      elements.charCount.textContent = `${text.length} characters`;
      if (elements.clarifyBox) elements.clarifyBox.style.display = "none";
      
      if (agent) {
        state.targetAgent = agent;
        elements.categoryPills.querySelectorAll(".pill").forEach(p => {
          const match = p.dataset.agent === agent;
          p.classList.toggle("active", match);
          p.setAttribute("aria-checked", match ? "true" : "false");
        });
      }

      startPromptGeneration();
    });
  });

  // Generate Button
  elements.generateBtn.addEventListener("click", () => startPromptGeneration());

  // Copy Prompt Button
  elements.copyBtn.addEventListener("click", copyPromptToClipboard);

  // Download Button
  elements.downloadBtn.addEventListener("click", downloadPromptFile);

  // Toggle View Button (Markdown vs Plain Text)
  elements.toggleViewBtn.addEventListener("click", toggleViewMode);

  // Sync edits in raw textarea back to markdown
  elements.rawOutput.addEventListener("input", () => {
    state.currentPromptText = elements.rawOutput.value;
    updateRenderedMarkdown(state.currentPromptText);
    updateStatsBadge(state.currentPromptText);
  });
}

// Keyboard mash and gibberish patterns
const KEYBOARD_WALKS = [
  "qwerty", "wertyu", "ertyui", "rtyuio", "tyuiop",
  "asdfgh", "sdfghj", "dfghjk", "fghjkl",
  "zxcvbn", "xcvbnm", "poiuyt", "lkjhgf", "mnbvcx",
  "qazwsx", "wsxedc", "edcrfv", "12345", "23456", "34567", "45678", "56789"
];

const ALPHABET_CONSONANT_WALKS = [
  "bcdf", "cdfg", "dfgh", "fghj", "ghjk", "hjkl", "jklm",
  "klmn", "lmnp", "mnpq", "npqr", "pqrs", "qrst", "rstv", "stvw", "tvwx", "vwxz"
];

const VALID_TECH_ACRONYMS = new Set([
  "api", "cli", "sdk", "rest", "crud", "graphql", "gql", "grpc", "mqtt", "rpc",
  "http", "https", "dns", "tcp", "udp", "ip", "ssh", "ssl", "tls",
  "cors", "csrf", "xss", "jwt", "oauth", "sso", "rbac", "abac", "pkce",
  "cdn", "url", "uri", "uuid", "dom", "html", "css", "svg", "pwa", "spa", "ssr",
  "js", "ts", "py", "sql", "wasm", "nosql", "php", "npm", "npx", "pip",
  "db", "dw", "etl", "elt", "dbt", "json", "yaml", "xml", "csv", "s3", "gcs", "rds", "redis", "kafka",
  "aws", "gcp", "k8s", "ecs", "ec2", "iam", "vpc", "ci", "cd", "pr",
  "ai", "ml", "llm", "rag", "nlp", "ocr", "cpu", "gpu", "ram", "ssd",
  "ui", "ux", "mrr", "arr", "clv", "roi", "kpi", "crm", "cms", "erp", "pos",
  "tv", "id", "ok", "app", "bot", "doc", "faq", "bio", "dev", "ops", "sec"
]);

function checkClientInputQuality(text) {
  const cleaned = text.trim();
  if (!cleaned) {
    return { valid: false, message: "Please type an idea or task first." };
  }

  // Check alphanumeric count
  const alnumCount = (cleaned.match(/[a-zA-Z0-9]/g) || []).length;
  if (alnumCount < 2) {
    return {
      valid: false,
      message: "Please enter a meaningful task or concept. A symbol like '.' is not enough to construct a valid prompt."
    };
  }

  // Check letters count (must have at least 2 letters, not just numbers/symbols)
  const letterCount = (cleaned.match(/[a-zA-Z]/g) || []).length;
  if (letterCount < 2) {
    return {
      valid: false,
      message: "Please include descriptive words. Numbers and symbols alone cannot be converted into a prompt."
    };
  }

  // Check tokens for keyboard mash and gibberish
  const tokens = cleaned.match(/[a-zA-Z0-9]+/g) || [];
  for (const token of tokens) {
    const w = token.toLowerCase();
    if (w.length < 2 || VALID_TECH_ACRONYMS.has(w)) continue;

    // Single character repeated 3+ times (e.g. zzzzzz, aaaaa)
    if (/(.)\1{2,}/.test(w)) {
      return {
        valid: false,
        message: `Detected repeated character gibberish in "${token}". Please enter meaningful words.`
      };
    }

    // Repetitive 2-3 char patterns (e.g. asdasd, qwqwqw)
    if (/(.{2,3})\1{2,}/.test(w)) {
      return {
        valid: false,
        message: `Detected repetitive keyboard pattern in "${token}". Please enter meaningful words.`
      };
    }

    // Keyboard mash walks
    for (const kw of KEYBOARD_WALKS) {
      if (w.includes(kw)) {
        return {
          valid: false,
          message: `Detected keyboard mash ("${kw}") in "${token}". Please describe what you want to create.`
        };
      }
    }

    // Alphabet consonant walks (e.g. bcdf, dfgh in ABCDFGHAG)
    for (const cw of ALPHABET_CONSONANT_WALKS) {
      if (w.includes(cw)) {
        return {
          valid: false,
          message: `Detected nonsensical or keyboard-mashed text in "${token}". Please use real words.`
        };
      }
    }

    // 5+ consecutive consonants
    if (/[bcdfghjklmnpqrstvwxz]{5,}/.test(w) && !["strengths", "lengths", "twelfths"].includes(w)) {
      return {
        valid: false,
        message: `Unpronounceable consonant cluster in "${token}". Please describe your project with real words.`
      };
    }

    // Words >= 4 characters without vowels
    if (w.length >= 4 && !/[aeiouy]/.test(w)) {
      return {
        valid: false,
        message: `"${token}" does not contain any vowels. Please enter a valid idea or task.`
      };
    }
  }

  return { valid: true, message: "" };
}

// ==========================================================================
// Generation Engine & SSE Streaming
// ==========================================================================
async function startPromptGeneration() {
  const inputText = elements.promptInput.value.trim();
  
  // Comprehensive Quality & Gibberish Validation
  const qualityCheck = checkClientInputQuality(inputText);
  if (!qualityCheck.valid) {
    showToast(qualityCheck.message, "error");
    elements.promptInput.focus();
    return;
  }

  if (state.isGenerating) return;
  setGeneratingState(true);

  // Reset output
  state.currentPromptText = "";
  elements.rawOutput.value = "";
  elements.renderedOutput.innerHTML = '<div class="streaming-indicator"><span>Easeprompt is crafting your prompt...</span></div>';
  elements.statsBadge.textContent = "Crafting...";

  // Ensure view is on rendered
  if (state.viewMode === "raw") toggleViewMode();

  try {
    const response = await fetch("/api/expand-stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        input_text: inputText,
        target_agent: state.targetAgent,
        framework_style: "art_framework",
        depth: "comprehensive",
        provider: "builtin"
      })
    });

    if (!response.ok) {
      let errMsg = `Server error (${response.status})`;
      try {
        const errJson = await response.json();
        if (errJson.detail) {
          if (Array.isArray(errJson.detail)) {
            errMsg = errJson.detail.map(d => d.msg || (typeof d === "string" ? d : JSON.stringify(d))).join("; ");
          } else {
            errMsg = typeof errJson.detail === "string" ? errJson.detail : JSON.stringify(errJson.detail);
          }
        }
      } catch (_) {
        const errText = await response.text();
        if (errText) errMsg += `: ${errText}`;
      }
      throw new Error(errMsg);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith("data: ")) continue;

        try {
          const data = JSON.parse(trimmed.slice(6));
          handleSseEvent(data);
        } catch (e) {
          console.error("SSE parse error", e);
        }
      }
    }

    showToast("Prompt generated successfully!", "success");
  } catch (error) {
    console.error("Generation error:", error);
    showToast(`Error: ${error.message || "Failed to generate prompt"}`, "error");
    elements.renderedOutput.innerHTML = `<div class="empty-state"><h4>Generation Error</h4><p>${escapeHtml(error.message)}</p></div>`;
  } finally {
    setGeneratingState(false);
    updateStatsBadge(state.currentPromptText);
  }
}

function handleSseEvent(data) {
  if (data.type === "token") {
    state.currentPromptText += data.content;
    elements.rawOutput.value = state.currentPromptText;
    updateRenderedMarkdown(state.currentPromptText);
    updateStatsBadge(state.currentPromptText);
  } else if (data.type === "done") {
    state.currentPromptText = data.full_content || state.currentPromptText;
    elements.rawOutput.value = state.currentPromptText;
    updateRenderedMarkdown(state.currentPromptText);
    updateStatsBadge(state.currentPromptText);
  } else if (data.type === "warning") {
    showToast(data.message, "warning");
  }
}

function updateRenderedMarkdown(text) {
  if (!text) {
    elements.renderedOutput.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">✨</div>
        <h4>Your prompt will appear here</h4>
        <p>Type a topic on the left or click an example above, then click <strong>Generate Prompt</strong>.</p>
        <div class="empty-checklist">
          <span>✓ High-status domain authority role</span>
          <span>✓ Extrapolated production context</span>
          <span>✓ Strict negative anti-patterns</span>
          <span>✓ Formatted deliverable schema</span>
        </div>
      </div>`;
    return;
  }

  // Parse Markdown using marked
  let html = marked.parse(text);

  // Stylize parameter placeholders like [INSERT ...] or [SPECIFY ...]
  html = html.replace(/\[(INSERT|SPECIFY|TARGET)[A-Z0-9_\s|"]+?\]/g, match => {
    return `<span class="prompt-placeholder">${escapeHtml(match)}</span>`;
  });

  elements.renderedOutput.innerHTML = html;

  // Highlight syntax in code blocks
  elements.renderedOutput.querySelectorAll("pre code").forEach(block => {
    hljs.highlightElement(block);
  });
}

function updateStatsBadge(text) {
  if (!text || !text.trim()) {
    elements.statsBadge.textContent = "Ready";
    return;
  }
  const words = text.trim().split(/\s+/).filter(Boolean).length;
  elements.statsBadge.textContent = `${words} words`;
}

function setGeneratingState(isGenerating) {
  state.isGenerating = isGenerating;
  elements.generateBtn.disabled = isGenerating;
  
  const btnText = elements.generateBtn.querySelector(".btn-text") || elements.generateBtn;
  if (isGenerating) {
    btnText.textContent = "Writing Prompt...";
    elements.streamLine.classList.add("active");
  } else {
    btnText.textContent = "Generate Prompt";
    elements.streamLine.classList.remove("active");
  }
}

// ==========================================================================
// User Actions: Copy, Download, Toggle View
// ==========================================================================
async function copyPromptToClipboard() {
  const text = state.currentPromptText.trim();
  if (!text) {
    showToast("Generate a prompt first before copying.", "error");
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
    elements.copyBtn.classList.add("copied");
    const copyLabel = elements.copyBtn.querySelector(".copy-label") || elements.copyBtn;
    copyLabel.textContent = "✓ Copied!";
    showToast("Prompt copied to clipboard!", "success");

    setTimeout(() => {
      elements.copyBtn.classList.remove("copied");
      copyLabel.textContent = "Copy Prompt";
    }, 2000);
  } catch (err) {
    console.error("Clipboard copy error:", err);
    showToast("Failed to copy automatically. Please select and copy manually.", "error");
  }
}

function downloadPromptFile() {
  const text = state.currentPromptText.trim();
  if (!text) {
    showToast("No prompt to download yet.", "error");
    return;
  }

  const rawTopic = elements.promptInput.value.trim().slice(0, 20).replace(/[^a-zA-Z0-9]/g, "_") || "Prompt";
  const filename = `Easeprompt_${rawTopic}_${Date.now()}.md`;

  const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Downloaded .md file!", "success");
}

function toggleViewMode() {
  if (state.viewMode === "rendered") {
    state.viewMode = "raw";
    elements.renderedOutput.style.display = "none";
    elements.rawOutput.style.display = "block";
    elements.toggleViewText.textContent = "Formatted View";
    elements.rawOutput.focus();
  } else {
    state.viewMode = "rendered";
    elements.renderedOutput.style.display = "block";
    elements.rawOutput.style.display = "none";
    elements.toggleViewText.textContent = "Plain Text";
  }
}

// ==========================================================================
// Utilities & Toasts
// ==========================================================================
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  
  const icon = type === "success" ? "✓" : type === "error" ? "✕" : "ℹ";
  toast.innerHTML = `<span class="toast-icon">${icon}</span><span class="toast-message">${escapeHtml(message)}</span>`;

  elements.toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("fade-out");
    setTimeout(() => toast.remove(), 250);
  }, 3200);
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
