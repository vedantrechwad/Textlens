chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyze-nlp-lens",
    title: "Analyze with NLP Lens",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "analyze-nlp-lens") {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => {
        alert("Text selected for NLP Lens. Please click the NLP Lens extension icon to see the analysis.");
      }
    });
  }
});

// Listen for messages from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "analyzeText") {
    const API_URL = "http://127.0.0.1:5000/api/analyze";
    
    fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: request.text })
    })
    .then(response => response.json())
    .then(data => {
      sendResponse(data);
    })
    .catch(error => {
      console.error("Fetch error:", error);
      sendResponse({ success: false, error: error.toString() });
    });
    
    // Return true to indicate we will send a response asynchronously
    return true;
  }
});
