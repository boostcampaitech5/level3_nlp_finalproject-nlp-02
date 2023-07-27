// message listener
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  console.log("chrome.runtime.onMessage.addListener called!! ")
  if (request.message === 'collect_page_info') {
    // Gather the pageInfo from DOM
    const pageInfo = {
      title: document.title,
      url: window.location.href,
      content: document.body.innerText,
    };
    console.log("hd", pageInfo)
    // Send response to the popup script - 이게 애초부터 계속 undefined이다...
    sendResponse({pageInfo: pageInfo});

    // Send the data to the background script
    chrome.runtime.sendMessage({message: 'collect_page_info', pageInfo: pageInfo}, function(response) {
      console.log(response);
    });
  }

  // collect only page's content
  else if (request.message === 'collect_page_only_content') {
    const rawContent = {
      content: document.body.innerText
    };
    // console.log("rconent: ", rcontent);
    sendResponse({ message: 'collect_page_only_content', onlyPage: rawContent });

    // Send the data to the background script
    chrome.runtime.sendMessage({ message: 'collect_page_only_content', onlyPage: rawContent }, function(response) {
      console.log(response);
    });
    return true;
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