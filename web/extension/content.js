// content.js
///
const port = chrome.runtime.connect({ name: "contentScriptConnection" });

// Example: Sending a message to the background script
port.postMessage({ message: "Hello from the content script!" });

// Example: Receiving a message from the background script
port.onMessage.addListener(function(message) {
  console.log("Received message from background script:", message);
});

// Listen for messages from the popup script
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'get_page_contents') {
    // Retrieve the page's contents
    var pageContents = document.body.innerText;
    var pageUrl = window.location.href;

    var totalInfo = {
      pageContents: pageContents,
      pageUrl: pageUrl
    }
    // Send the contents back to the popup script
    sendResponse({contents: totalInfo});
  }
});


