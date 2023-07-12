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

// 유저의 기존 북마크 url, content 를 DB로 긁어오는 함수 - 추후 이 함수들만 빼서 파일 만들어야 함.
function processBookmarkTree(bookmarkNodes) {
  return new Promise(function(resolve, reject) {
    chrome.identity.getProfileUserInfo({'accountStatus':'ANY'}, function(userInfo) { 
      var username = userInfo.email.match(/^([^@]*)@/)[1];
      var userBookmarkArray = []
      
      function traverseNodes(nodes) {
        nodes.forEach(node =>{
          // 노드에 바로 url이 있을 경우(북마크 파일)
          if (node.url) {
            var bookmarkInfo = {
              'userId': username,
              'userEmail': userInfo.email,
              'url': node.url,
              'bookmarkTitle': node.title,
              'title': "",
              'content': "",
              'folder': "",
              'tag': "",
            };
            // console.log(bookmarkInfo)
            userBookmarkArray.push(bookmarkInfo)
            // 추후 url의 context를 가져와야 한다..
          }
          // 노드에 children이 있는 경우(하위 폴더)
          else if (node.children) {
            try{
              var FolderTitle = FolderTitle + '/' + node.title;
            } catch(ReferenceError){
              var FolderTitle = node.title;
            }
            console.log("folder: ", FolderTitle)
            // Process the folder or its children recursively
            traverseNodes(node.children);
          }
        });
      }
      traverseNodes(bookmarkNodes);
      resolve(userBookmarkArray);
    });
  });
}

// Django response가 user 정보가 없다는 response 일 경우 수행하는 함수 - 이것도 추후 다른 파일로 빼야 함.
function sendUserBookmarkHistory(data) {
  return new Promise(function(resolve, reject) {
    chrome.bookmarks.getTree(bookmarkTree => {
      
      processBookmarkTree(bookmarkTree)
        .then(function(userBookmarkArray) {
          const bookmarkHistory = JSON.stringify(userBookmarkArray);

          // 데이터 송신
          simpleFetcher(SERVER_URL, bookmarkHistory)
            .then(responseData => {
              if (responseData) {
                console.log("Sending bookmark is done!, ", responseData);
              }
            })
        })
        .catch(error =>{
          console.error("Error in [sendUserBookmarkHistory]: ",error);
        })
    
      resolve(bookmarkHistory);
    });
  });
}