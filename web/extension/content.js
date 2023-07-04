// content.js

// Listen for messages from the popup script
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'get_page_contents') {
    // Retrieve the page's contents
    var pageContents = document.body.innerText;

    // Send the contents back to the popup script
    sendResponse({contents: pageContents});
  }
});
