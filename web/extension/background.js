// show bookmarked urls
chrome.bookmarks.onCreated.addListener(function (bookmark) {

    console.log("new bookmark added.")

    chrome.bookmarks.get(bookmark, function (bookmarks) {
        if (bookmarks && bookmarks.length > 0 && bookmarks[0].url) {
            const bookmarkedUrl = bookmarks[0].url

            console.log('Newly bookmarked URL:', bookmarkedUrl);
            
            // chrome.tabs.create({ url: bookmarkedUrl }, function (tab) { // url을 연다. create를 통해서 tab object를 받는다.
            //     chrome.tabs.executeScript(tab.id, { code: "document.body.innerHTML" }, function (result) {
            //         if (result && result.length > 0) {
            //             const pageContent = result[0];
            //             console.log('Content of bookmarked URL:', pageContent);
            //             // Perform further actions with the page content if needed
            //         }
            //     });
            // });
        }
    });

    chrome.identity.getProfileUserInfo({'accountStatus': 'ANY'}, function(userInfo) {
        console.log(JSON.stringify(userInfo));
    });
});



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
  