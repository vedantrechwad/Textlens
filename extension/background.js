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
    
    const doFetch = (engine) => {
      fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
          text: request.text,
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
      })
      .then(response => response.json())
      .then(data => {
        sendResponse(data);
      })
      .catch(error => {
        console.error("Fetch error:", error);
        sendResponse({ success: false, error: error.toString() });
      });
    };

    try {
      if (chrome.storage && chrome.storage.local) {
        chrome.storage.local.get(["sentimentEngine"], (result) => {
          doFetch(result.sentimentEngine || "vader");
        });
      } else {
        doFetch("vader");
      }
    } catch (e) {
      console.error("Storage error:", e);
      doFetch("vader");
    }
    
    // Return true to indicate we will send a response asynchronously
    return true;
  }
});
