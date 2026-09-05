chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyze-textlens",
    title: "Analyze with Textlens",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "analyze-textlens") {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => {
        alert("Text selected for Textlens. Please click the Textlens extension icon to see the analysis.");
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
