const API_URL = "http://127.0.0.1:5000/api/analyze";

document.addEventListener("DOMContentLoaded", async () => {
  const btnAnalyzeSelection = document.getElementById("btn-analyze-selection");
  const btnAnalyzePage = document.getElementById("btn-analyze-page");
  const btnAnalyzeThread = document.getElementById("btn-analyze-thread");
  const selectionStatus = document.getElementById("selection-status");
  const toggleStats = document.getElementById("toggle-stats");
  
  const engineSelect = document.getElementById("sentiment-engine-select");
  
  // Load saved preference
  chrome.storage.local.get(["sentimentEngine"], (result) => {
    if (result.sentimentEngine) {
      engineSelect.value = result.sentimentEngine;
    }
  });

  engineSelect.addEventListener("change", (e) => {
    chrome.storage.local.set({ sentimentEngine: e.target.value });
  });

  let selectedText = "";

  // Check for selected text in the active tab
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id },
        function: () => window.getSelection().toString()
      },
      (results) => {
        if (results && results[0] && results[0].result) {
          selectedText = results[0].result.trim();
          if (selectedText.length > 0) {
            selectionStatus.textContent = "Selected text detected.";
            btnAnalyzeSelection.disabled = false;
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

  btnAnalyzePage.addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
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
    // Basic extraction for threads (e.g., getting paragraph texts)
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
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
             return texts.join('\\n\\n');
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

  async function analyzeText(text) {
    document.getElementById("controls").classList.add("hidden");
    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("error").classList.add("hidden");
    document.getElementById("results").classList.add("hidden");

    try {
      // Determine engine
      const engine = document.getElementById("sentiment-engine-select").value || "vader";

      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          text: text,
          options: {
            sentiment_model: engine,
            sentiment: true,
            summary: true,
            keywords: true,
            entities: true,
            pos: true,
            statistics: true
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
      document.getElementById("error-msg").textContent = err.message || "Failed to connect to backend.";
      document.getElementById("controls").classList.remove("hidden");
    }
  }

  function renderResults(data) {
    document.getElementById("loading").classList.add("hidden");
    document.getElementById("results").classList.remove("hidden");

    // Sentiment
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
          s.className = "chip";
          s.textContent = i;
          indBox.appendChild(s);
        });
      } else {
        indCont.classList.add("hidden");
      }
    }

    // Summary
    if (data.summary) {
      document.getElementById("summary-text").textContent = data.summary;
    }

    // Keywords
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

    // Entities
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

    // Stats
    if (data.statistics) {
      document.getElementById("stat-words").textContent = data.statistics.words;
      document.getElementById("stat-sentences").textContent = data.statistics.sentences;
      document.getElementById("stat-complexity").textContent = data.statistics.readingComplexity;
    }
    
    // POS
    if (data.pos) {
      const pc = document.getElementById("pos-container");
      pc.innerHTML = `<div>Nouns: ${data.pos.Nouns} | Verbs: ${data.pos.Verbs} | Adjectives: ${data.pos.Adjectives}</div>`;
    }
  }
});
