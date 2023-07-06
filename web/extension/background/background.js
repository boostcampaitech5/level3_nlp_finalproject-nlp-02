// bookmark listener
chrome.bookmarks.onCreated.addListener(function (bookmark) {
  chrome.bookmarks.get(bookmark, function (bookmarks) {
    if (bookmarks && bookmarks.length > 0 && bookmarks[0].url) {
      const bookmarkedUrl = bookmarks[0].url
      console.log("new bookmark added. url from background: ", bookmarkedUrl)
     }
  });
});

// message listener
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  let pageInfo = request.pageInfo;

  chrome.identity.getProfileUserInfo({'accountStatus':'ANY'}, function(userInfo) { 
    console.log(userInfo)
    console.log(typeof userInfo)

    // Merge pageInfo and userInfo into totalInfo
    const totalInfo = Object.assign(pageInfo, userInfo);
    console.log(totalInfo)
    console.log(typeof totalInfo)

    // Send data to Server
    fetch('http://101.101.211.226:30006/API/inference', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(totalInfo)
    })
    .then(response => console.log(response.json()))
    .catch((error) => {
      console.error('Error:', error);
    });
  });
});

// content.js connection checker
chrome.runtime.onConnect.addListener(function(port) {
    if (port.name === "contentScriptConnection") {
      console.log("Content script connected!");
  
      // Example: Sending a message to the content script
      port.postMessage({ message: "Hello from the background script!" });
  
      // Example: Receiving a message from the content script
      port.onMessage.addListener(function(message) {
        console.log("Received message from content script:", message);
      });
    }
    else{
        console.log("onConnect does not work")
    }
});