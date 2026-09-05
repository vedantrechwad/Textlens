let currentSelection = "";
let floatingBtn = null;
let modal = null;

document.addEventListener("mouseup", (e) => {
  // Wait a tiny bit for the selection to register fully in the browser
  setTimeout(() => {
    const selection = window.getSelection();
    const text = selection.toString().trim();
    
    // Ignore clicks inside our own UI
    if (floatingBtn && floatingBtn.contains(e.target)) return;
    if (modal && modal.contains(e.target)) return;

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
  const maxW = window.innerWidth - 320;
  const actualX = Math.min(x, maxW);
  
  modal.style.top = y + "px";
  modal.style.left = actualX + "px";
  
  modal.innerHTML = `
    <div id="textlens-modal-header">
      <h4>Textlens</h4>
      <div id="textlens-close-btn">&times;</div>
    </div>
    <div id="textlens-modal-body">
      <div class="textlens-loader">Analyzing...</div>
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
        body.innerHTML = `<div style="color:#dc3545;">Failed to analyze: Extension connection lost. Please refresh the webpage.</div>`;
        return;
      }
      
      if (!response || !response.success) {
        body.innerHTML = `<div style="color:#dc3545;">Failed to analyze: ${response ? response.error : "Unknown error"}</div>`;
        return;
      }
      
      // Render results
      let html = "";
      
      if (response.sentiment) {
        html += `
          <div class="textlens-section">
            <h5>Sentiment</h5>
            <span class="textlens-badge ${response.sentiment.label}">${response.sentiment.label} (${Math.round(response.sentiment.confidence * 100)}%)</span>
          </div>
        `;
      }
      
      if (response.summary) {
        html += `
          <div class="textlens-section">
            <h5>TL;DR</h5>
            <div style="color:#495057;">${response.summary}</div>
          </div>
        `;
      }
      
      if (response.keywords && response.keywords.length > 0) {
        html += `<div class="textlens-section"><h5>Keywords</h5><div class="textlens-chips">`;
        response.keywords.slice(0, 5).forEach(k => {
          html += `<span class="textlens-chip">${k.term}</span>`;
        });
        html += `</div></div>`;
      }
      
      body.innerHTML = html;
    });
  } catch (err) {
    const body = document.getElementById("textlens-modal-body");
    if (body) {
      body.innerHTML = `<div style="color:#dc3545;">Extension was updated. Please <b>refresh this webpage</b> to continue using Textlens.</div>`;
    }
  }
}
