const API_URL = "http://127.0.0.1:5000/api/analyze";
const DECODE_URL = "http://127.0.0.1:5000/api/genz-decode";
const GLOSSARY_URL = "http://127.0.0.1:5000/api/genz-glossary";

document.addEventListener("DOMContentLoaded", async () => {
  // Navigation Tabs
  const tabAnalyzeBtn = document.getElementById("tab-analyze-btn");
  const tabGenzBtn = document.getElementById("tab-genz-btn");
  const tabAnalyze = document.getElementById("tab-analyze");
  const tabGenz = document.getElementById("tab-genz");

  tabAnalyzeBtn.addEventListener("click", () => {
    tabAnalyzeBtn.classList.add("active");
    tabGenzBtn.classList.remove("active");
    tabAnalyze.classList.remove("hidden");
    tabGenz.classList.add("hidden");
  });

  tabGenzBtn.addEventListener("click", () => {
    tabGenzBtn.classList.add("active");
    tabAnalyzeBtn.classList.remove("active");
    tabGenz.classList.remove("hidden");
    tabAnalyze.classList.add("hidden");
    loadGlossary();
  });

  // Tab 1 Elements
  const btnAnalyzeSelection = document.getElementById("btn-analyze-selection");
  const btnAnalyzePage = document.getElementById("btn-analyze-page");
  const btnAnalyzeThread = document.getElementById("btn-analyze-thread");
  const btnAnalyzeCustom = document.getElementById("btn-analyze-custom");
  const customTextInput = document.getElementById("custom-text-input");
  const toggleCustomInput = document.getElementById("toggle-custom-input");
  const customInputBody = document.getElementById("custom-input-body");
  const customInputArrow = document.getElementById("custom-input-arrow");

  const selectionStatus = document.getElementById("selection-status");
  const toggleStats = document.getElementById("toggle-stats");
  const engineSelect = document.getElementById("sentiment-engine-select");
  const targetLanguageSelect = document.getElementById("target-language-select");

  const btnNewAnalysis = document.getElementById("btn-new-analysis");
  const btnBackFromError = document.getElementById("btn-back-from-error");
  const btnCopyPlainEnglish = document.getElementById("btn-copy-plain-english");
  const btnClearPopupHighlight = document.getElementById("btn-clear-popup-highlight");

  // Tab 2 Elements (Interactive Decoder & Glossary)
  const standaloneInput = document.getElementById("standalone-genz-input");
  const btnStandaloneDecode = document.getElementById("btn-standalone-decode");
  const standaloneResult = document.getElementById("standalone-genz-result");
  const standaloneMeter = document.getElementById("standalone-meter");
  const standaloneTextDisplay = document.getElementById("standalone-text-display");
  const btnClearStandaloneHighlight = document.getElementById("btn-clear-standalone-highlight");
  const standaloneTerms = document.getElementById("standalone-terms");
  const standaloneDecodedBox = document.getElementById("standalone-decoded-box");
  const btnCopyStandalone = document.getElementById("btn-copy-standalone");
  const glossarySearch = document.getElementById("glossary-search-input");
  const glossaryList = document.getElementById("glossary-list");

  let fullGlossary = [];
  let currentAnalyzedText = "";
  let activePopupTerm = null;
  let activeStandaloneTerm = null;
  let popupPort = null;
  let activeTabId = null;

  function ensurePopupPort(tabId) {
    if (!tabId) return null;
    activeTabId = tabId;
    if (popupPort) return popupPort;
    try {
      popupPort = chrome.tabs.connect(tabId, { name: "textlens-popup-session" });
      popupPort.onDisconnect.addListener(() => {
        popupPort = null;
      });
    } catch (e) {
      popupPort = null;
    }
    return popupPort;
  }

  function handlePopupClose() {
    clearPageHighlights();
    if (popupPort) {
      try {
        popupPort.disconnect();
      } catch (e) {}
      popupPort = null;
    }
  }

  window.addEventListener("pagehide", handlePopupClose);
  window.addEventListener("beforeunload", handlePopupClose);

  // Load saved preferences
  chrome.storage.local.get(["sentimentEngine", "targetLanguage"], (result) => {
    if (result.sentimentEngine) {
      engineSelect.value = result.sentimentEngine;
    }
    if (result.targetLanguage) {
      targetLanguageSelect.value = result.targetLanguage;
    }
  });

  engineSelect.addEventListener("change", (e) => {
    chrome.storage.local.set({ sentimentEngine: e.target.value });
  });

  targetLanguageSelect.addEventListener("change", (e) => {
    chrome.storage.local.set({ targetLanguage: e.target.value });
  });

  // Toggle custom text input box
  toggleCustomInput.addEventListener("click", () => {
    const isHidden = customInputBody.classList.toggle("hidden");
    customInputArrow.textContent = isHidden ? "▶" : "▼";
  });

  let selectedText = "";

  // Check for selected text in active tab
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs || !tabs[0] || !tabs[0].id) return;
    ensurePopupPort(tabs[0].id);
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id },
        function: () => window.getSelection().toString()
      },
      (results) => {
        if (results && results[0] && results[0].result) {
          selectedText = results[0].result.trim();
          if (selectedText.length > 0) {
            selectionStatus.textContent = `"${selectedText.substring(0, 42)}${selectedText.length > 42 ? "..." : ""}"`;
            btnAnalyzeSelection.disabled = false;
            // Also prefill standalone input for convenience
            if (standaloneInput) standaloneInput.value = selectedText;
            // Automatically analyze selected text immediately so Gen-Z words & highlight UI show right away
            analyzeText(selectedText);
          }
        }
      }
    );
  });

  toggleStats.addEventListener("click", () => {
    const content = document.getElementById("stats-content");
    content.classList.toggle("hidden");
  });

  btnAnalyzeSelection.addEventListener("click", () => {
    if (selectedText) analyzeText(selectedText);
  });

  btnAnalyzeCustom.addEventListener("click", () => {
    const text = customTextInput.value.trim();
    if (text) {
      analyzeText(text);
    }
  });

  btnAnalyzePage.addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs || !tabs[0] || !tabs[0].id) return;
      chrome.scripting.executeScript(
        {
          target: { tabId: tabs[0].id },
          function: () => document.body.innerText
        },
        (results) => {
          if (results && results[0] && results[0].result) {
            analyzeText(results[0].result);
          }
        }
      );
    });
  });

  btnAnalyzeThread.addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs || !tabs[0] || !tabs[0].id) return;
      chrome.scripting.executeScript(
        {
          target: { tabId: tabs[0].id },
          function: () => {
            let selector = 'p, article, .comment, .usertext-body';
            const host = window.location.hostname;
            
            if (host.includes('reddit.com')) {
              selector = 'shreddit-comment p, .usertext-body, [data-test-id="comment"]';
            } else if (host.includes('twitter.com') || host.includes('x.com')) {
              selector = '[data-testid="tweetText"]';
            } else if (host.includes('quora.com')) {
              selector = '.q-text.qu-dynamicFontSize, .q-box.qu-mb--tiny';
            }
            
            const elements = document.querySelectorAll(selector);
            const texts = Array.from(elements).map(el => el.innerText).filter(t => t.trim().length > 0);
            return texts.join('\n\n');
          }
        },
        (results) => {
          if (results && results[0] && results[0].result) {
            analyzeText(results[0].result);
          }
        }
      );
    });
  });

  btnNewAnalysis.addEventListener("click", () => {
    clearPopupHighlight();
    document.getElementById("results").classList.add("hidden");
    document.getElementById("controls").classList.remove("hidden");
  });

  if (btnClearPopupHighlight) {
    btnClearPopupHighlight.addEventListener("click", () => {
      clearPopupHighlight();
    });
  }

  if (btnClearStandaloneHighlight) {
    btnClearStandaloneHighlight.addEventListener("click", () => {
      clearStandaloneHighlight();
    });
  }

  btnBackFromError.addEventListener("click", () => {
    document.getElementById("error").classList.add("hidden");
    document.getElementById("controls").classList.remove("hidden");
  });

  btnCopyPlainEnglish.addEventListener("click", () => {
    const box = document.getElementById("genz-decoded-box");
    if (box && box.textContent) {
      navigator.clipboard.writeText(box.textContent).then(() => {
        const orig = btnCopyPlainEnglish.textContent;
        btnCopyPlainEnglish.textContent = "Copied!";
        setTimeout(() => { btnCopyPlainEnglish.textContent = orig; }, 1500);
      });
    }
  });

  // Tab 2: Standalone Slang Decoder Handler
  btnStandaloneDecode.addEventListener("click", async () => {
    const text = standaloneInput.value.trim();
    if (!text) return;

    btnStandaloneDecode.textContent = "Decoding...";
    btnStandaloneDecode.disabled = true;

    try {
      const response = await fetch(DECODE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
      });
      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Decoding failed");
      }

      const genz = data.genz;
      clearStandaloneHighlight();
      standaloneResult.classList.remove("hidden");
      standaloneMeter.textContent = `Level: ${genz.slang_level} • ${genz.term_count} Slang (${genz.slang_density}% Density)`;

      if (standaloneTextDisplay) {
        renderTextWithClickableTerms(
          standaloneTextDisplay,
          text,
          genz.detected_terms || [],
          (term) => activateStandaloneHighlight(term, text, genz.detected_terms || [])
        );
      }

      standaloneTerms.innerHTML = "";
      if (genz.detected_terms && genz.detected_terms.length > 0) {
        genz.detected_terms.forEach(t => {
          const item = document.createElement("div");
          item.className = "genz-term-item interactive-term";
          item.setAttribute("data-term", t.term);
          item.innerHTML = `
            <div class="genz-term-header">
              <span class="genz-term-name">"${t.term}" ➔ ${t.translation}</span>
              <span class="genz-term-category">${t.category}</span>
            </div>
            <div class="genz-term-def">${t.definition}</div>
            <button class="btn-highlight-term" type="button" data-term="${t.term}">
              🖍️ Click to Highlight in Text
            </button>
          `;
          item.addEventListener("click", () => {
            activateStandaloneHighlight(t.term, text, genz.detected_terms);
          });
          standaloneTerms.appendChild(item);
        });
      } else {
        standaloneTerms.innerHTML = `<div style="font-size:11px; color:#64748b;">No recognizable Gen-Z slang detected.</div>`;
      }

      standaloneDecodedBox.textContent = genz.plain_english;
    } catch (err) {
      alert("Failed to decode: Make sure Flask backend is running on http://127.0.0.1:5000");
    } finally {
      btnStandaloneDecode.textContent = "Decode to Normal English";
      btnStandaloneDecode.disabled = false;
    }
  });

  btnCopyStandalone.addEventListener("click", () => {
    if (standaloneDecodedBox && standaloneDecodedBox.textContent) {
      navigator.clipboard.writeText(standaloneDecodedBox.textContent).then(() => {
        btnCopyStandalone.textContent = "Copied!";
        setTimeout(() => { btnCopyStandalone.textContent = "Copy"; }, 1500);
      });
    }
  });

  // Tab 2: Load Glossary
  async function loadGlossary() {
    if (fullGlossary.length > 0) return; // Already loaded

    try {
      const res = await fetch(GLOSSARY_URL);
      const data = await res.json();
      if (data.success && data.glossary) {
        fullGlossary = data.glossary;
        document.getElementById("glossary-count").textContent = `${fullGlossary.length} Terms`;
        renderGlossary(fullGlossary);
      }
    } catch (err) {
      glossaryList.innerHTML = `<div style="font-size:11px; color:#64748b; padding:8px;">Start backend at http://127.0.0.1:5000 to load full 150+ slang glossary.</div>`;
    }
  }

  function renderGlossary(terms) {
    glossaryList.innerHTML = "";
    if (terms.length === 0) {
      glossaryList.innerHTML = `<div style="font-size:11px; color:#64748b; padding:8px;">No matching slang terms found.</div>`;
      return;
    }
    terms.forEach(item => {
      const el = document.createElement("div");
      el.className = "glossary-item";
      el.innerHTML = `
        <div class="glossary-item-header">
          <span class="glossary-item-term">${item.term}</span>
          <span class="genz-term-category">${item.category}</span>
        </div>
        <div class="glossary-item-meaning"><strong>Means:</strong> ${item.translation} — <i>${item.definition}</i></div>
      `;
      glossaryList.appendChild(el);
    });
  }

  glossarySearch.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) {
      renderGlossary(fullGlossary);
      return;
    }
    const filtered = fullGlossary.filter(t => 
      t.term.toLowerCase().includes(q) || 
      t.translation.toLowerCase().includes(q) || 
      t.category.toLowerCase().includes(q)
    );
    renderGlossary(filtered);
  });

  // Main NLP Analysis
  async function analyzeText(text) {
    currentAnalyzedText = text;
    document.getElementById("controls").classList.add("hidden");
    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("error").classList.add("hidden");
    document.getElementById("results").classList.add("hidden");

    try {
      const engine = engineSelect.value || "vader";
      const targetLang = targetLanguageSelect.value || "en";

      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          text: text,
          options: {
            sentiment_model: engine,
            target_language: targetLang,
            sentiment: true,
            summary: true,
            keywords: true,
            entities: true,
            pos: true,
            statistics: true,
            genz: true,
            multilingual: true
          }
        })
      });

      const data = await response.json();
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || "Server error");
      }

      renderResults(data);
    } catch (err) {
      document.getElementById("loading").classList.add("hidden");
      document.getElementById("error").classList.remove("hidden");
      if (err.message && err.message.toLowerCase().includes("fetch")) {
        document.getElementById("error-msg").textContent = "Cannot connect to backend at http://127.0.0.1:5000. Please make sure 'python app.py' is running.";
      } else {
        document.getElementById("error-msg").textContent = err.message || "Failed to connect to backend.";
      }
    }
  }

  const BEVERAGE_PRE_REGEX = /\b(matcha|iced|ice|hot|cold|warm|green|black|herbal|chai|boba|milk|earl\s+grey|peppermint|chamomile|jasmine|bubble|fruit|lemon|sweet|ginger|mint|oolong|hibiscus|rooibos|darjeeling|sencha|white|loose\s+leaf|cup\s+of|mug\s+of|pot\s+of|glass\s+of|brewing|brew|drank|drinking)\s+$/i;
  const BEVERAGE_POST_REGEX = /^\s+\b(bag|bags|leaf|leaves|kettle|pot|cup|latte|tree|plantation)\b/i;

  const CULINARY_COOKED_PRE_REGEX = /(?:\b(slow|slowly|fresh|freshly|partially|well|fully|properly|evenly|under|over|home|deep|pressure|pan|oven|steam|steamed|flame|wood|kettle|perfectly|lightly|thoroughly|baker)\s+$)|(?:\b(steak|chicken|meat|vegetables?|veggies?|fish|eggs?|potatoes?|pasta|pizza|rice|burgers?|dish|dishes|meal|meals|soup|bacon|turkey|salmon|shrimp|noodles?|pie|bread|beef|pork|tofu|sausage|lobster|crab|ribs|stew)\b[^.?!;:]*?\b(it\s+(?:was|is)|was|were|is|are|being|been)\s+(?:[^.?!;:]*?\s+)?$)/i;
  const CULINARY_COOKED_POST_REGEX = /^\s+(?:(?:for\s+\w+\s+)?(?:us|me|him|her|them|everyone|someone|friends|family)?\s*(?:a\s+|an\s+|the\s+|some\s+|our\s+|my\s+|his\s+|her\s+|their\s+|fresh\s+|delicious\s+|good\s+|hot\s+|big\s+|nice\s+|tasty\s+)?(?:dinner|lunch|breakfast|meal|food|meat|steak|chicken|pasta|rice|beef|pork|fish|egg|eggs|soup|vegetables|veggies|curry|sauce|potatoes|dish|bacon|turkey|salmon|shrimp|noodles|pizza|burger|burgers|pie|bread|supper|beans|tofu|mushrooms|sausage|lobster|crab|ribs|stew)\b|to\s+(?:a\s+)?(?:crisp|perfection|death|order|medium|rare|well[- ]done|golden)\b|until\s+(?:golden|brown|tender|crispy|done|soft|translucent)\b|(?:in|on|over)\s+(?:the\s+|a\s+|an\s+)?(?:oven|stove|stovetop|grill|pan|skillet|pot|wok|air\s*fryer|microwave|fire|flame|heat|water|oil|butter|sauce|broth)\b|with\s+(?:olive\s+)?(?:oil|butter|spices|salt|sauce|herbs|garlic|seasoning)\b|at\s+\d+\s*(?:degrees|°|f|c)\b|by\s+(?:baking|boiling|roasting|frying|grilling|steaming|smoking|sauteing|braising)\b|for\s+\d+\s+(?:hours|minutes|mins|hrs)\b)/i;

  const LITERAL_CAP_PRE_REGEX = /\b(baseball|bottle|swim|shower|lens|pen|knee|salary|gas|capital|hub|ice|market|fitting)\s+$/i;
  const LITERAL_FIT_PRE_REGEX = /\b(stay|staying|keep|keeping|physically|aerobic|cardio|don't|doesn't|didn't|won't|can't|cannot|tight|snug|perfect|to)\s+$/i;
  const LITERAL_FIT_POST_REGEX = /^\s+\b(into|in|together|me|you|him|her|them|through|for)\b/i;

  function isLiteralAmbiguousContext(term, textBefore, textAfter) {
    const t = term.toLowerCase();
    if (t === "tea") {
      return BEVERAGE_PRE_REGEX.test(textBefore) || BEVERAGE_POST_REGEX.test(textAfter);
    }
    if (t === "cooked") {
      return CULINARY_COOKED_PRE_REGEX.test(textBefore) || CULINARY_COOKED_POST_REGEX.test(textAfter);
    }
    if (t === "cap" || t === "capping") {
      return LITERAL_CAP_PRE_REGEX.test(textBefore);
    }
    if (t === "fit" || t === "fits") {
      return LITERAL_FIT_PRE_REGEX.test(textBefore) || LITERAL_FIT_POST_REGEX.test(textAfter);
    }
    return false;
  }

  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function createTermRegex(term) {
    const escaped = escapeRegExp(term.trim());
    const startBound = /^\w/.test(term) ? "\\b" : "";
    const endBound = /\w$/.test(term) ? "\\b" : "";
    return new RegExp(`${startBound}${escaped}${endBound}`, "gi");
  }

  function sendHighlightToActiveTab(term, matchedText, fullText, spans) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs || !tabs[0] || !tabs[0].id) return;
      const tabId = tabs[0].id;
      ensurePopupPort(tabId);
      chrome.tabs.sendMessage(tabId, {
        action: "highlightWordOnPage",
        term: term,
        matchedText: matchedText || term,
        fullText: fullText,
        spans: spans || null
      }, (response) => {
        if (chrome.runtime.lastError) {
          // If script not yet injected in tab, inject and retry
          chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: ["content.js"]
          }, () => {
            ensurePopupPort(tabId);
            chrome.tabs.sendMessage(tabId, {
              action: "highlightWordOnPage",
              term: term,
              matchedText: matchedText || term,
              fullText: fullText,
              spans: spans || null
            });
          });
        }
      });
    });
  }

  function clearPageHighlights() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs || !tabs[0] || !tabs[0].id) return;
      chrome.tabs.sendMessage(tabs[0].id, { action: "clearPageHighlights" }, () => {
        if (chrome.runtime.lastError) {}
      });
    });
  }

  function renderTextWithClickableTerms(container, text, detectedTerms, onTermClick) {
    container.innerHTML = "";
    if (!text) return;
    if (!detectedTerms || detectedTerms.length === 0) {
      container.textContent = text;
      return;
    }

    // Sort terms by length descending to prioritize longer phrases
    const sorted = [...detectedTerms].sort((a, b) => b.term.length - a.term.length);
    const matches = [];

    sorted.forEach(t => {
      const regex = createTermRegex(t.term);
      let m;
      while ((m = regex.exec(text)) !== null) {
        const start = m.index;
        const end = start + m[0].length;
        const overlap = matches.some(prev => (start >= prev.start && start < prev.end) || (end > prev.start && end <= prev.end));
        if (overlap) continue;

        // If backend provided exact spans for this term, ensure this occurrence matches one of the detected slang spans
        if (t.spans && Array.isArray(t.spans) && t.spans.length > 0) {
          const matchesSpan = t.spans.some(([s, e]) => Math.abs(s - start) <= 3 && Math.abs(e - end) <= 3);
          if (!matchesSpan) {
            continue;
          }
        } else if (isLiteralAmbiguousContext(t.term, text.substring(0, start), text.substring(end))) {
          // Fallback: Skip literal occurrences
          continue;
        }

        matches.push({
          start,
          end,
          text: m[0],
          term: t.term
        });
      }
    });

    matches.sort((a, b) => a.start - b.start);

    let lastIndex = 0;
    matches.forEach(match => {
      if (match.start > lastIndex) {
        container.appendChild(document.createTextNode(text.substring(lastIndex, match.start)));
      }
      const span = document.createElement("span");
      span.className = "genz-inline-term";
      span.setAttribute("data-term", match.term);
      span.textContent = match.text;
      span.title = `Gen-Z Term: "${match.term}" — Click to highlight`;
      span.addEventListener("click", () => {
        if (onTermClick) onTermClick(match.term);
      });
      container.appendChild(span);
      lastIndex = match.end;
    });

    if (lastIndex < text.length) {
      container.appendChild(document.createTextNode(text.substring(lastIndex)));
    }
  }

  function activatePopupHighlight(term, detectedTerms) {
    if (activePopupTerm === term) {
      clearPopupHighlight();
      return;
    }

    activePopupTerm = term;

    const display = document.getElementById("analyzed-text-display");
    let matchCount = 0;
    let firstMatchEl = null;

    if (display) {
      display.querySelectorAll(".genz-inline-term").forEach(span => {
        if (span.getAttribute("data-term").toLowerCase() === term.toLowerCase()) {
          span.classList.add("popup-highlight-active");
          matchCount++;
          if (!firstMatchEl) firstMatchEl = span;
        } else {
          span.classList.remove("popup-highlight-active");
        }
      });
      if (firstMatchEl) {
        firstMatchEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }

    const termsContainer = document.getElementById("genz-terms-container");
    let targetCard = null;
    if (termsContainer) {
      termsContainer.querySelectorAll(".genz-term-item").forEach(card => {
        const cardTerm = card.getAttribute("data-term");
        const btn = card.querySelector(".btn-highlight-term");
        if (cardTerm && cardTerm.toLowerCase() === term.toLowerCase()) {
          card.classList.add("active-term");
          if (btn) {
            btn.classList.add("active");
            btn.innerHTML = `✨ Highlighting in Text (Active)`;
          }
          targetCard = card;
        } else {
          card.classList.remove("active-term");
          if (btn) {
            btn.classList.remove("active");
            btn.innerHTML = `🖍️ Click to Highlight in Text`;
          }
        }
      });
      if (targetCard) {
        targetCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }

    const banner = document.getElementById("highlight-status-banner");
    const statusText = document.getElementById("highlight-status-text");
    const clearBtn = document.getElementById("btn-clear-popup-highlight");
    if (banner && statusText) {
      banner.classList.remove("hidden");
      statusText.innerHTML = `✨ Highlighted <strong>"${term}"</strong> (${matchCount || 1} in text) & on webpage`;
    }
    if (clearBtn) clearBtn.classList.remove("hidden");

    const termObj = detectedTerms.find(t => t.term.toLowerCase() === term.toLowerCase());
    const matchedText = termObj ? termObj.matched_text : term;
    const spans = termObj ? termObj.spans : null;
    sendHighlightToActiveTab(term, matchedText, currentAnalyzedText, spans);
  }

  function clearPopupHighlight() {
    activePopupTerm = null;
    const display = document.getElementById("analyzed-text-display");
    if (display) {
      display.querySelectorAll(".genz-inline-term").forEach(span => {
        span.classList.remove("popup-highlight-active");
      });
    }

    const termsContainer = document.getElementById("genz-terms-container");
    if (termsContainer) {
      termsContainer.querySelectorAll(".genz-term-item").forEach(card => {
        card.classList.remove("active-term");
        const btn = card.querySelector(".btn-highlight-term");
        if (btn) {
          btn.classList.remove("active");
          btn.innerHTML = `🖍️ Click to Highlight in Text`;
        }
      });
    }

    const banner = document.getElementById("highlight-status-banner");
    if (banner) banner.classList.add("hidden");

    const clearBtn = document.getElementById("btn-clear-popup-highlight");
    if (clearBtn) clearBtn.classList.add("hidden");

    clearPageHighlights();
  }

  function activateStandaloneHighlight(term, text, detectedTerms) {
    if (activeStandaloneTerm === term) {
      clearStandaloneHighlight();
      return;
    }

    activeStandaloneTerm = term;

    const display = document.getElementById("standalone-text-display");
    let firstEl = null;
    if (display) {
      display.querySelectorAll(".genz-inline-term").forEach(span => {
        if (span.getAttribute("data-term").toLowerCase() === term.toLowerCase()) {
          span.classList.add("popup-highlight-active");
          if (!firstEl) firstEl = span;
        } else {
          span.classList.remove("popup-highlight-active");
        }
      });
      if (firstEl) {
        firstEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }

    const termsContainer = document.getElementById("standalone-terms");
    let targetCard = null;
    if (termsContainer) {
      termsContainer.querySelectorAll(".genz-term-item").forEach(card => {
        const cardTerm = card.getAttribute("data-term");
        const btn = card.querySelector(".btn-highlight-term");
        if (cardTerm && cardTerm.toLowerCase() === term.toLowerCase()) {
          card.classList.add("active-term");
          if (btn) {
            btn.classList.add("active");
            btn.innerHTML = `✨ Highlighting in Text (Active)`;
          }
          targetCard = card;
        } else {
          card.classList.remove("active-term");
          if (btn) {
            btn.classList.remove("active");
            btn.innerHTML = `🖍️ Click to Highlight in Text`;
          }
        }
      });
      if (targetCard) {
        targetCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }

    const clearBtn = document.getElementById("btn-clear-standalone-highlight");
    if (clearBtn) clearBtn.classList.remove("hidden");

    const termObj = detectedTerms.find(t => t.term.toLowerCase() === term.toLowerCase());
    const matchedText = termObj ? termObj.matched_text : term;
    const spans = termObj ? termObj.spans : null;
    sendHighlightToActiveTab(term, matchedText, text, spans);
  }

  function clearStandaloneHighlight() {
    activeStandaloneTerm = null;
    const display = document.getElementById("standalone-text-display");
    if (display) {
      display.querySelectorAll(".genz-inline-term").forEach(span => {
        span.classList.remove("popup-highlight-active");
      });
    }
    const termsContainer = document.getElementById("standalone-terms");
    if (termsContainer) {
      termsContainer.querySelectorAll(".genz-term-item").forEach(card => {
        card.classList.remove("active-term");
        const btn = card.querySelector(".btn-highlight-term");
        if (btn) {
          btn.classList.remove("active");
          btn.innerHTML = `🖍️ Click to Highlight in Text`;
        }
      });
    }
    const clearBtn = document.getElementById("btn-clear-standalone-highlight");
    if (clearBtn) clearBtn.classList.add("hidden");
    clearPageHighlights();
  }

  function renderResults(data) {
    document.getElementById("loading").classList.add("hidden");
    document.getElementById("results").classList.remove("hidden");

    clearPopupHighlight();

    // 0. Analyzed Selected Text Display & Highlighting
    const analyzedTextDisplay = document.getElementById("analyzed-text-display");
    const analyzedTextBadge = document.getElementById("analyzed-text-badge");
    const detectedTerms = (data.genz && data.genz.detected_terms) ? data.genz.detected_terms : [];

    if (analyzedTextDisplay) {
      const words = currentAnalyzedText.trim().split(/\s+/).filter(Boolean).length;
      if (analyzedTextBadge) {
        analyzedTextBadge.textContent = `${words} ${words === 1 ? 'word' : 'words'}`;
      }
      renderTextWithClickableTerms(
        analyzedTextDisplay,
        currentAnalyzedText,
        detectedTerms,
        (term) => activatePopupHighlight(term, detectedTerms)
      );
    }

    // 1. Language Detection & Translation Banner
    const langContainer = document.getElementById("language-badge-container");
    langContainer.innerHTML = "";
    const transBanner = document.getElementById("translation-banner");

    if (data.language) {
      const langBadge = document.createElement("span");
      langBadge.className = "language-badge";
      langBadge.innerHTML = `🌐 ${data.language.detected_name} (${Math.round(data.language.confidence * 100)}%)`;
      langContainer.appendChild(langBadge);

      if (data.language.was_translated && data.language.translated_to_english) {
        transBanner.classList.remove("hidden");
        document.getElementById("translation-banner-title").textContent = 
          `${data.language.detected_name} Translated to English`;
        document.getElementById("translation-banner-details").textContent = 
          `Auto-translated to English so all NLP pipelines (sentiment, summary, entities) operate accurately.`;
        document.getElementById("translated-to-english-text").textContent = 
          data.language.translated_to_english;
      } else {
        transBanner.classList.add("hidden");
      }
    } else {
      transBanner.classList.add("hidden");
    }

    // 2. Gen-Z Slang Decoder (DISPLAYED FIRST AND PROMINENTLY)
    const genzCard = document.getElementById("genz-card");
    const genzTermsContainer = document.getElementById("genz-terms-container");
    const genzDecodedBox = document.getElementById("genz-decoded-box");
    const genzCountBadge = document.getElementById("genz-count-badge");
    const genzLevelTag = document.getElementById("genz-level-tag");

    if (data.genz && data.genz.has_slang && data.genz.detected_terms.length > 0) {
      genzCard.classList.remove("hidden");
      genzCountBadge.textContent = `${data.genz.term_count} Slang ${data.genz.term_count === 1 ? 'Term' : 'Terms'}`;
      genzLevelTag.textContent = `Intensity: ${data.genz.slang_level} • ${data.genz.slang_density}% Density`;
      genzTermsContainer.innerHTML = "";

      data.genz.detected_terms.forEach(t => {
        const item = document.createElement("div");
        item.className = "genz-term-item interactive-term";
        item.setAttribute("data-term", t.term);
        item.innerHTML = `
          <div class="genz-term-header">
            <span class="genz-term-name">"${t.term}" ➔ ${t.translation}</span>
            <span class="genz-term-category">${t.category}</span>
          </div>
          <div class="genz-term-def">${t.definition}</div>
          <button class="btn-highlight-term" type="button" data-term="${t.term}">
            🖍️ Click to Highlight in Text
          </button>
        `;
        item.addEventListener("click", () => {
          activatePopupHighlight(t.term, data.genz.detected_terms);
        });
        genzTermsContainer.appendChild(item);
      });

      genzDecodedBox.textContent = data.genz.plain_english;
    } else {
      genzCard.classList.add("hidden");
    }

    // 3. Sentiment
    if (data.sentiment) {
      const lbl = document.getElementById("sentiment-label");
      lbl.textContent = data.sentiment.label;
      lbl.className = "badge " + data.sentiment.label;
      document.getElementById("sentiment-confidence").textContent = Math.round(data.sentiment.confidence * 100) + "%";
      
      const indCont = document.getElementById("sentiment-indicators-container");
      const indBox = document.getElementById("sentiment-indicators");
      indBox.innerHTML = "";
      if (data.sentiment.indicators && data.sentiment.indicators.length > 0) {
        indCont.classList.remove("hidden");
        data.sentiment.indicators.forEach(i => {
          const s = document.createElement("span");
          // Highlight if indicator is a recognized slang term
          const isSlang = data.genz && data.genz.detected_terms && data.genz.detected_terms.some(t => t.term.toLowerCase() === i.toLowerCase());
          s.className = "chip" + (isSlang ? " indicator-slang" : "");
          s.textContent = isSlang ? `✨ ${i}` : i;
          indBox.appendChild(s);
        });
      } else {
        indCont.classList.add("hidden");
      }
    }

    // 4. Summary & Target Language Translation
    const summaryText = document.getElementById("summary-text");
    const transSummaryCont = document.getElementById("translated-summary-container");
    const transSummaryText = document.getElementById("translated-summary-text");
    const transSummaryLabel = document.getElementById("translated-summary-label");
    const targetLangTag = document.getElementById("target-lang-tag");

    if (data.summary) {
      summaryText.textContent = data.summary;
    } else {
      summaryText.textContent = "Text is too brief for an extractive summary.";
    }

    if (data.translated_summary) {
      transSummaryCont.classList.remove("hidden");
      targetLangTag.classList.remove("hidden");
      const targetLangName = targetLanguageSelect.options[targetLanguageSelect.selectedIndex].text;
      targetLangTag.textContent = targetLangName.split(' ')[0];
      transSummaryLabel.textContent = `Translated TL;DR (${targetLangName}):`;
      transSummaryText.textContent = data.translated_summary;
    } else {
      transSummaryCont.classList.add("hidden");
      targetLangTag.classList.add("hidden");
    }

    // 5. Keywords
    if (data.keywords) {
      const kc = document.getElementById("keywords-container");
      kc.innerHTML = "";
      data.keywords.forEach(k => {
        const s = document.createElement("span");
        s.className = "chip";
        s.textContent = k.term;
        kc.appendChild(s);
      });
    }

    // 6. Entities
    if (data.entities) {
      const ec = document.getElementById("entities-container");
      ec.innerHTML = "";
      data.entities.forEach(e => {
        const s = document.createElement("span");
        const baseClass = e.label === 'ORG' ? 'entity-org' : (e.label === 'GPE' || e.label === 'LOC' ? 'entity-gpe' : (e.label === 'PERSON' ? 'entity-person' : ''));
        s.className = "chip " + baseClass;
        s.textContent = `${e.text} (${e.label})`;
        ec.appendChild(s);
      });
    }

    // 7. Stats
    if (data.statistics) {
      document.getElementById("stat-words").textContent = data.statistics.words;
      document.getElementById("stat-sentences").textContent = data.statistics.sentences;
      document.getElementById("stat-complexity").textContent = data.statistics.readingComplexity;
    }
    
    // 8. POS
    if (data.pos) {
      const pc = document.getElementById("pos-container");
      pc.innerHTML = `<div>Nouns: ${data.pos.Nouns || 0} | Verbs: ${data.pos.Verbs || 0} | Adjectives: ${data.pos.Adjectives || 0}</div>`;
    }
  }
});
