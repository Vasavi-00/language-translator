/* ==========================================================================
   LingoStamp — Language Translator frontend logic
   Vanilla JS, no frameworks. Talks to the Django REST API.
   ========================================================================== */

(function () {
  "use strict";

  // ------------------------------------------------------------------
  // Element references
  // ------------------------------------------------------------------
  const inputText = document.getElementById("inputText");
  const outputText = document.getElementById("outputText");
  const sourceLang = document.getElementById("sourceLang");
  const targetLang = document.getElementById("targetLang");
  const translateBtn = document.getElementById("translateBtn");
  const swapBtn = document.getElementById("swapBtn");
  const clearBtn = document.getElementById("clearBtn");
  const copyBtn = document.getElementById("copyBtn");
  const listenInputBtn = document.getElementById("listenInputBtn");
  const listenOutputBtn = document.getElementById("listenOutputBtn");
  const charCount = document.getElementById("charCount");
  const outputCharCount = document.getElementById("outputCharCount");
  const loadingSpinner = document.getElementById("loadingSpinner");
  const errorBanner = document.getElementById("errorBanner");
  const detectedBadge = document.getElementById("detectedBadge");
  const themeToggle = document.getElementById("themeToggle");
  const historyList = document.getElementById("historyList");
  const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");
  const toast = document.getElementById("toast");
  const audioPlayer = document.getElementById("audioPlayer");
  const tickerTrack = document.getElementById("tickerTrack");

  const LANGUAGES = window.__LANGUAGES__ || {};
  const MAX_CHARS = 5000;
  const DEBOUNCE_MS = 700;

  let debounceTimer = null;
  let lastTranslatedValue = "";

  // ------------------------------------------------------------------
  // Utilities
  // ------------------------------------------------------------------
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2200);
  }

  function showError(message) {
    errorBanner.textContent = message;
    errorBanner.classList.remove("d-none");
  }

  function clearError() {
    errorBanner.classList.add("d-none");
    errorBanner.textContent = "";
  }

  function setLoading(isLoading) {
    loadingSpinner.classList.toggle("d-none", !isLoading);
    translateBtn.disabled = isLoading;
  }

  async function apiRequest(url, options = {}) {
    const csrftoken = getCookie("csrftoken");
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken || "",
        ...(options.headers || {}),
      },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const message = data.error || "Something went wrong. Please try again.";
      throw new Error(message);
    }
    return data;
  }

  // ------------------------------------------------------------------
  // Character counter
  // ------------------------------------------------------------------
  inputText.addEventListener("input", () => {
    const len = inputText.value.length;
    charCount.textContent = len;
    charCount.parentElement.style.color = len > MAX_CHARS ? "var(--coral)" : "";
    scheduleAutoTranslate();
  });

  function scheduleAutoTranslate() {
    clearTimeout(debounceTimer);
    const text = inputText.value.trim();
    if (!text) {
      outputText.textContent = "";
      outputCharCount.textContent = "";
      clearError();
      return;
    }
    debounceTimer = setTimeout(() => {
      if (text !== lastTranslatedValue) {
        translate();
      }
    }, DEBOUNCE_MS);
  }

  // ------------------------------------------------------------------
  // Translate
  // ------------------------------------------------------------------
  async function translate() {
    const text = inputText.value.trim();

    if (!text) {
      showError("Please enter some text to translate.");
      return;
    }
    if (text.length > MAX_CHARS) {
      showError(`Text is too long. Please limit input to ${MAX_CHARS} characters.`);
      return;
    }

    clearError();
    setLoading(true);
    detectedBadge.classList.add("d-none");

    try {
      const data = await apiRequest("/api/translate/", {
        method: "POST",
        body: JSON.stringify({
          text: text,
          source_lang: sourceLang.value,
          target_lang: targetLang.value,
        }),
      });

      outputText.textContent = data.translated_text;
      outputCharCount.textContent = `${data.translated_text.length} chars`;
      lastTranslatedValue = text;

      if (sourceLang.value === "auto" && data.detected_language) {
        const name = LANGUAGES[data.detected_language] || data.detected_language;
        detectedBadge.textContent = `Detected: ${name}`;
        detectedBadge.classList.remove("d-none");
      }

      loadHistory();
    } catch (err) {
      showError(err.message);
      outputText.textContent = "";
    } finally {
      setLoading(false);
    }
  }

  translateBtn.addEventListener("click", translate);

  // ------------------------------------------------------------------
  // Swap languages
  // ------------------------------------------------------------------
  swapBtn.addEventListener("click", () => {
    if (sourceLang.value === "auto") {
      showToast("Can't swap while source is Auto Detect");
      return;
    }
    const tempLang = sourceLang.value;
    sourceLang.value = targetLang.value;
    targetLang.value = tempLang;

    const tempText = inputText.value;
    inputText.value = outputText.textContent;
    outputText.textContent = tempText;

    charCount.textContent = inputText.value.length;
    scheduleAutoTranslate();
  });

  // ------------------------------------------------------------------
  // Clear
  // ------------------------------------------------------------------
  clearBtn.addEventListener("click", () => {
    inputText.value = "";
    outputText.textContent = "";
    charCount.textContent = "0";
    outputCharCount.textContent = "";
    clearError();
    detectedBadge.classList.add("d-none");
    inputText.focus();
  });

  // ------------------------------------------------------------------
  // Copy translated text
  // ------------------------------------------------------------------
  copyBtn.addEventListener("click", async () => {
    const text = outputText.textContent;
    if (!text) {
      showToast("Nothing to copy yet");
      return;
    }
    try {
      await navigator.clipboard.writeText(text);
      showToast("Copied to clipboard");
    } catch (err) {
      showToast("Could not copy text");
    }
  });

  // ------------------------------------------------------------------
  // Text-to-Speech
  // ------------------------------------------------------------------
  async function speak(text, lang, button) {
    if (!text || !text.trim()) {
      showToast("Nothing to read aloud");
      return;
    }
    const icon = button.querySelector("i");
    icon.classList.remove("fa-volume-high");
    icon.classList.add("fa-spinner", "fa-spin");

    try {
      const data = await apiRequest("/api/speak/", {
        method: "POST",
        body: JSON.stringify({ text, lang }),
      });
      audioPlayer.src = data.audio_url;
      await audioPlayer.play();
    } catch (err) {
      showToast(err.message || "Could not generate speech");
    } finally {
      icon.classList.remove("fa-spinner", "fa-spin");
      icon.classList.add("fa-volume-high");
    }
  }

  listenInputBtn.addEventListener("click", () => {
    const lang = sourceLang.value === "auto" ? "en" : sourceLang.value;
    speak(inputText.value, lang, listenInputBtn);
  });

  listenOutputBtn.addEventListener("click", () => {
    speak(outputText.textContent, targetLang.value, listenOutputBtn);
  });

  // ------------------------------------------------------------------
  // Dark mode
  // ------------------------------------------------------------------
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const icon = themeToggle.querySelector("i");
    icon.className = theme === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
    localStorage.setItem("lingostamp-theme", theme);
  }

  themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    applyTheme(current === "dark" ? "light" : "dark");
  });

  (function initTheme() {
    const saved = localStorage.getItem("lingostamp-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(saved || (prefersDark ? "dark" : "light"));
  })();

  // ------------------------------------------------------------------
  // History
  // ------------------------------------------------------------------
  function formatDate(isoString) {
    const d = new Date(isoString);
    return d.toLocaleString(undefined, {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });
  }

  async function loadHistory() {
    try {
      const data = await apiRequest("/api/history/?limit=8", { method: "GET" });
      if (!data.length) {
        historyList.innerHTML = '<p class="history-empty">Your translated phrases will appear here.</p>';
        return;
      }
      historyList.innerHTML = data
        .map(
          (item) => `
        <div class="history-item">
          <div class="h-original">
            <span class="h-label">${item.source_language}${item.detected_language ? " → " + item.detected_language : ""}</span>
            ${escapeHtml(item.original_text)}
          </div>
          <div class="h-translated">
            <span class="h-label">${item.target_language}</span>
            ${escapeHtml(item.translated_text)}
          </div>
          <div class="h-meta">${formatDate(item.created_at)}</div>
        </div>`
        )
        .join("");
    } catch (err) {
      // Non-fatal: history is a nice-to-have.
      console.error("Failed to load history:", err);
    }
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  refreshHistoryBtn.addEventListener("click", loadHistory);

  // ------------------------------------------------------------------
  // Ticker: rotating greetings in various languages/scripts
  // ------------------------------------------------------------------
  const GREETINGS = [
    ["Hello", "English"], ["Hola", "Spanish"], ["Bonjour", "French"],
    ["Ciao", "Italian"], ["Hallo", "German"], ["こんにちは", "Japanese"],
    ["안녕하세요", "Korean"], ["你好", "Chinese"], ["नमस्ते", "Hindi"],
    ["مرحبا", "Arabic"], ["Olá", "Portuguese"], ["Привет", "Russian"],
    ["สวัสดี", "Thai"], ["Xin chào", "Vietnamese"], ["வணக்கம்", "Tamil"],
  ];
  function initTicker() {
    const items = [...GREETINGS, ...GREETINGS]
      .map(([word, lang]) => `<span>${word}<small>${lang}</small></span>`)
      .join("");
    tickerTrack.innerHTML = items;
  }

  // ------------------------------------------------------------------
  // Init
  // ------------------------------------------------------------------
  initTicker();
  loadHistory();
})();
