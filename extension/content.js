let currentSelection = "";
let savedSelectionRange = null;
let savedSelectionText = "";
let floatingBtn = null;
let modal = null;

// Track selection range continuously
document.addEventListener("selectionchange", () => {
  const selection = window.getSelection();
  if (selection && selection.rangeCount > 0 && !selection.isCollapsed) {
    const text = selection.toString().trim();
    if (text.length > 0) {
      savedSelectionText = text;
      try {
        savedSelectionRange = selection.getRangeAt(0).cloneRange();
      } catch (e) {}
    }
  }
});

document.addEventListener("mouseup", (e) => {
  // Wait a tiny bit for the selection to register fully in the browser
  setTimeout(() => {
    const selection = window.getSelection();
    const text = selection.toString().trim();
    
    // Ignore clicks inside our own UI
    if (floatingBtn && floatingBtn.contains(e.target)) return;
    if (modal && modal.contains(e.target)) return;

    if (text.length > 0) {
      savedSelectionText = text;
      if (selection.rangeCount > 0) {
        try {
          savedSelectionRange = selection.getRangeAt(0).cloneRange();
        } catch (e) {}
      }
    }

    if (text.length > 0 && text !== currentSelection) {
      currentSelection = text;
      showFloatingButton(selection, e.clientX, e.clientY);
    } else if (text.length === 0) {
      currentSelection = "";
      hideFloatingButton();
      hideModal();
    }
  }, 10);
});

function showFloatingButton(selection, mouseX, mouseY) {
  hideFloatingButton(); // remove existing
  
  floatingBtn = document.createElement("div");
  floatingBtn.id = "textlens-floating-btn";
  floatingBtn.innerText = "T";
  floatingBtn.title = "Analyze with Textlens";
  
  // Position near the mouse cursor
  floatingBtn.style.top = (window.scrollY + mouseY + 15) + "px";
  floatingBtn.style.left = (window.scrollX + mouseX + 5) + "px";
  
  floatingBtn.addEventListener("mousedown", (e) => {
    e.preventDefault(); // prevent selection clear
    e.stopPropagation();
    analyzeSelectedText();
  });
  
  document.body.appendChild(floatingBtn);
}

function hideFloatingButton() {
  if (floatingBtn) {
    floatingBtn.remove();
    floatingBtn = null;
  }
}

function showModal(x, y) {
  hideModal();
  
  modal = document.createElement("div");
  modal.id = "textlens-modal";
  
  // Keep it within screen bounds roughly
  const maxW = window.innerWidth - 360;
  const actualX = Math.min(x, Math.max(10, maxW));
  
  modal.style.top = y + "px";
  modal.style.left = actualX + "px";
  
  modal.innerHTML = `
    <div id="textlens-modal-header">
      <h4>🔍 Textlens Insights</h4>
      <div id="textlens-close-btn" title="Close">&times;</div>
    </div>
    <div id="textlens-modal-body">
      <div class="textlens-loader">Analyzing & decoding text...</div>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  document.getElementById("textlens-close-btn").addEventListener("click", () => {
    hideModal();
  });
}

function hideModal() {
  if (modal) {
    modal.remove();
    modal = null;
  }
}

function analyzeSelectedText() {
  if (!currentSelection) return;
  
  // Hide button, show modal at button's position
  const btnRect = floatingBtn.getBoundingClientRect();
  const top = window.scrollY + btnRect.bottom + 5;
  const left = window.scrollX + btnRect.left;
  
  hideFloatingButton();
  showModal(left, top);
  
  // Send message to background script to fetch data
  try {
    chrome.runtime.sendMessage({ action: "analyzeText", text: currentSelection }, (response) => {
      const body = document.getElementById("textlens-modal-body");
      if (!body) return; // Modal was closed before response
      
      if (chrome.runtime.lastError) {
        body.innerHTML = `<div style="color:#dc2626;">Failed to analyze: Extension connection lost. Please refresh the webpage.</div>`;
        return;
      }
      
      if (!response || !response.success) {
        body.innerHTML = `<div style="color:#dc2626;">Failed to analyze: ${response ? response.error : "Unknown error. Ensure Flask backend is running on http://127.0.0.1:5000"}</div>`;
        return;
      }
      
      // Render results
      let html = "";

      // 1. Language Tag (if present)
      if (response.language) {
        html += `
          <div>
            <span class="textlens-lang-badge">🌐 ${response.language.detected_name} (${Math.round(response.language.confidence * 100)}%)</span>
          </div>
        `;
        if (response.language.was_translated && response.language.translated_to_english) {
          html += `
            <div class="textlens-section">
              <h5>English Translation</h5>
              <div style="color:#1e293b;">${response.language.translated_to_english}</div>
            </div>
          `;
        }
      }

      // 2. Gen-Z Slang Decoder (RENDERED PROMINENTLY FIRST)
      if (response.genz && response.genz.has_slang && response.genz.detected_terms.length > 0) {
        const slangCount = response.genz.term_count;
        const level = response.genz.slang_level || `${slangCount} Terms`;
        
        html += `
          <div class="textlens-genz-card">
            <div class="textlens-genz-header">
              <span class="textlens-genz-title">🔮 Gen-Z Slang Decoder</span>
              <span class="textlens-genz-badge">${slangCount} Slang</span>
            </div>
            <div class="textlens-genz-meter">Level: <b>${level}</b></div>
            <div class="textlens-chips" style="margin-bottom:6px;">
        `;
        response.genz.detected_terms.forEach(t => {
          html += `<span class="textlens-chip slang interactive-modal-slang" data-term="${t.term}" title="${t.definition} (${t.category}) — Click to highlight in text">✨ "${t.term}" ➔ ${t.translation}</span>`;
        });
        html += `
            </div>
            <div class="textlens-decoded-text">
              <div class="textlens-decoded-header">
                <span>Plain English Translation:</span>
                <button class="textlens-btn-copy" id="textlens-modal-copy-btn">Copy</button>
              </div>
              <div id="textlens-modal-decoded-content">${response.genz.plain_english}</div>
            </div>
          </div>
        `;
      }

      // 3. Sentiment
      if (response.sentiment) {
        html += `
          <div class="textlens-section">
            <h5>Sentiment</h5>
            <span class="textlens-badge ${response.sentiment.label}">${response.sentiment.label} (${Math.round(response.sentiment.confidence * 100)}%)</span>
        `;
        if (response.sentiment.indicators && response.sentiment.indicators.length > 0) {
          html += `<div style="margin-top:6px;"><span style="font-size:10px; color:#64748b; font-weight:600;">Key Indicators: </span><span style="font-size:11px; font-weight:600; color:#334155;">${response.sentiment.indicators.join(', ')}</span></div>`;
        }
        html += `</div>`;
      }
      
      // 4. Summary
      if (response.summary) {
        html += `
          <div class="textlens-section">
            <h5>TL;DR</h5>
            <div style="color:#334155;">${response.summary}</div>
          </div>
        `;
      }
      
      // 5. Keywords
      if (response.keywords && response.keywords.length > 0) {
        html += `<div class="textlens-section"><h5>Keywords</h5><div class="textlens-chips">`;
        response.keywords.slice(0, 5).forEach(k => {
          html += `<span class="textlens-chip">${k.term}</span>`;
        });
        html += `</div></div>`;
      }
      
      body.innerHTML = html;

      // Attach click listeners to Gen-Z slang chips inside modal
      body.querySelectorAll(".interactive-modal-slang").forEach(chip => {
        chip.addEventListener("click", () => {
          const term = chip.getAttribute("data-term");
          highlightWordInWebpage(term, term, currentSelection);
        });
      });

      // Attach copy button handler if present
      const copyBtn = document.getElementById("textlens-modal-copy-btn");
      if (copyBtn) {
        copyBtn.addEventListener("click", () => {
          const content = document.getElementById("textlens-modal-decoded-content");
          if (content && content.textContent) {
            navigator.clipboard.writeText(content.textContent).then(() => {
              copyBtn.textContent = "Copied!";
              setTimeout(() => { copyBtn.textContent = "Copy"; }, 1500);
            });
          }
        });
      }
    });
  } catch (err) {
    const body = document.getElementById("textlens-modal-body");
    if (body) {
      body.innerHTML = `<div style="color:#dc2626;">Extension was updated. Please <b>refresh this webpage (F5)</b> to use the latest Textlens features.</div>`;
    }
  }
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

function clearWebHighlights() {
  const marks = document.querySelectorAll("mark.textlens-web-highlight");
  marks.forEach(mark => {
    const parent = mark.parentNode;
    if (parent) {
      while (mark.firstChild) {
        parent.insertBefore(mark.firstChild, mark);
      }
      mark.remove();
      parent.normalize();
    }
  });
}

function highlightWordInWebpage(term, matchedText, fullText) {
  if (!term || !term.trim()) return { success: false, reason: "empty term" };

  clearWebHighlights();

  const termToSearch = term.trim();
  const regex = createTermRegex(termToSearch);

  // Determine root container and whether we can use saved range
  let targetRoot = document.body;
  let useRange = null;

  if (savedSelectionRange && savedSelectionRange.startContainer && savedSelectionRange.startContainer.isConnected) {
    const rangeText = savedSelectionRange.toString();
    regex.lastIndex = 0;
    if (regex.test(rangeText)) {
      useRange = savedSelectionRange;
      targetRoot = savedSelectionRange.commonAncestorContainer;
      if (targetRoot.nodeType === Node.TEXT_NODE) {
        targetRoot = targetRoot.parentNode;
      }
    }
  }

  // If saved range didn't contain it, check window.getSelection()
  if (!useRange) {
    const sel = window.getSelection();
    if (sel && sel.rangeCount > 0 && !sel.isCollapsed) {
      const curRange = sel.getRangeAt(0);
      regex.lastIndex = 0;
      if (regex.test(curRange.toString())) {
        useRange = curRange;
        targetRoot = curRange.commonAncestorContainer;
        if (targetRoot.nodeType === Node.TEXT_NODE) {
          targetRoot = targetRoot.parentNode;
        }
      }
    }
  }

  // If still not matched to a range, search nearest container containing fullText
  if (!useRange && fullText && fullText.length > 5) {
    const candidates = document.querySelectorAll("p, article, section, div, span, li, blockquote");
    for (const el of candidates) {
      if (el.innerText && el.innerText.includes(fullText) && !el.closest("#textlens-modal, #textlens-floating-btn")) {
        targetRoot = el;
        break;
      }
    }
  }

  // Collect text nodes
  const textNodes = [];
  const walker = document.createTreeWalker(
    targetRoot,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        const tag = parent.tagName.toLowerCase();
        if (["script", "style", "noscript", "textarea", "input"].includes(tag)) {
          return NodeFilter.FILTER_REJECT;
        }
        if (parent.closest("#textlens-modal, #textlens-floating-btn, .textlens-web-highlight")) {
          return NodeFilter.FILTER_REJECT;
        }
        if (useRange) {
          try {
            if (!useRange.intersectsNode(node)) return NodeFilter.FILTER_REJECT;
          } catch (e) {}
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    }
  );

  let cur;
  while ((cur = walker.nextNode())) {
    textNodes.push(cur);
  }

  const createdMarks = [];

  for (const node of textNodes) {
    if (!node.parentNode) continue;
    let workingNode = node;
    regex.lastIndex = 0;
    let match = regex.exec(workingNode.nodeValue);

    while (match) {
      const matchIndex = match.index;
      const matchLength = match[0].length;

      try {
        const matchedNode = workingNode.splitText(matchIndex);
        const remainderNode = matchedNode.splitText(matchLength);

        const mark = document.createElement("mark");
        mark.className = "textlens-web-highlight";
        mark.setAttribute("data-term", termToSearch);
        mark.title = `Textlens: "${termToSearch}" — Click to dismiss highlight`;

        mark.addEventListener("click", (e) => {
          e.stopPropagation();
          clearWebHighlights();
        });

        matchedNode.parentNode.insertBefore(mark, matchedNode);
        mark.appendChild(matchedNode);
        createdMarks.push(mark);

        workingNode = remainderNode;
        regex.lastIndex = 0;
        match = regex.exec(workingNode.nodeValue);
      } catch (err) {
        break;
      }
    }
  }

  if (createdMarks.length > 0) {
    createdMarks[0].scrollIntoView({ behavior: "smooth", block: "center" });
    return { success: true, count: createdMarks.length };
  }

  return { success: false, reason: "No matches found in target selection" };
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "highlightWordOnPage") {
    const res = highlightWordInWebpage(request.term, request.matchedText, request.fullText);
    sendResponse(res);
    return true;
  }
  if (request.action === "clearPageHighlights") {
    clearWebHighlights();
    sendResponse({ success: true });
    return true;
  }
  if (request.action === "getSelectedTextAndRange") {
    sendResponse({
      text: savedSelectionText || window.getSelection().toString().trim(),
      hasRange: !!savedSelectionRange
    });
    return true;
  }
});
