const SERVER_URL = 'http://118.67.131.212:30005/API/post/'

// bookmark listener
chrome.bookmarks.onCreated.addListener(function (bookmark) {
  chrome.bookmarks.get(bookmark, function (bookmarks) {
    if (bookmarks && bookmarks.length > 0 && bookmarks[0].url) {
      const bookmarkedUrl = bookmarks[0].url
      // console.log("New bookmark added. url from background: ", bookmarkedUrl)
     }
  });
});

// message listener  
// send bookmark information to server
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  let pageInfo = request.pageInfo;

  chrome.identity.getProfileUserInfo({'accountStatus':'ANY'}, function(userProfile) { 
    const userName = userProfile.email.match(/^([^@]*)@/)[1];

    // Merge pageInfo and userInfo into totalInfo
    userInfo = {'userId': userName, 'userEmail': userProfile['email']}
    const totalInfo = Object.assign(pageInfo, userInfo);
    console.log(totalInfo)
    console.log(typeof totalInfo)

    // 북마크 정보 전송
    simpleFetcher(SERVER_URL, totalInfo)
      .then(responseData => {
        if (responseData) {
          console.log("Sending bookmark is done!, ", responseData);
        }
      })

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

////////////////
// 심플한 fetch 함수 구현
function simpleFetcher(url, data){
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Network response is not ok')
      }
    })
    .catch(error =>{
      console.error('Error:', error);
    })
}