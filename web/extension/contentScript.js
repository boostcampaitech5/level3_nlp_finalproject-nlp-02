// message listener
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.message === 'collect_page_info') {
    // Gather the necessary page data
    let pageInfo = {
      title: document.title,
      url: window.location.href,
      docs: document.body.innerText,
    };

    sendResponse({pageInfo: pageInfo})

    // Send the data to the background script
    chrome.runtime.sendMessage({pageInfo: pageInfo}, function(response) {
      console.log(response);
    });
  }
});

// connection checker from background.js
const port = chrome.runtime.connect({ name: "contentScriptConnection" });

// Example: Sending a message to the background script
port.postMessage({ message: "Hello from the content script!" });

// Example: Receiving a message from the background script
port.onMessage.addListener(function(message) {
  console.log("Received message from background script:", message);
});