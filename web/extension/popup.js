const SERVER_URL = 'http://118.67.131.212:30005'

// // Bookmarks node traversing search function (folder version)
// function traverseBookmarks(bookmarkTreeNodes, bookmarkFoldersDropdown) {
//   for (let i = 0; i < bookmarkTreeNodes.length; i++) {
//     let node = bookmarkTreeNodes[i];
//     if (node.children) {
//       // Add folder to the dropdown
//       let option = document.createElement('option');
//       option.text = node.title;  // Just using the node title here
//       option.value = node.id;
//       bookmarkFoldersDropdown.add(option);

//       // Recursively traverse children
//       traverseBookmarks(node.children, bookmarkFoldersDropdown);
//     }
//   }
// }

// Bookmarks node traversing search function (path version)
// function traverseBookmarks(
//   bookmarkTreeNodes,
//   bookmarkFoldersDropdown,
//   path = ""
// ) {
//   for (let i = 0; i < bookmarkTreeNodes.length; i++) {
//     let node = bookmarkTreeNodes[i];
//     if (node.children) {
//       let newPath = path + "/" + node.title;

//       // Add folder to the dropdown
//       let option = document.createElement("option");
//       option.text = newPath; // Using newPath as option text
//       option.value = node.id;
//       bookmarkFoldersDropdown.add(option);

//       traverseBookmarks(node.children, bookmarkFoldersDropdown, newPath);
//     }
//   }
// }

function traverseBookmarks(bookmarkTreeNodes, parentElement, path = "") {
  for (let i = 0; i < bookmarkTreeNodes.length; i++) {
    let node = bookmarkTreeNodes[i];
    if (node.url) continue;
    let newPath = path + "/" + node.title;

    // Create list item and checkbox
    let listItem = document.createElement("li");
    let checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = node.id;

    // Create label
    let label = document.createElement("label");
    label.htmlFor = node.id;
    label.setAttribute("data-title", node.title); // Add this line

    // Create icon
    let icon = document.createElement("span");
    icon.className = "material-icons-outlined";
    icon.textContent = node.children ? "unfold_less" : "unfold_less";
    icon.classList.add(icon.textContent); // Add the class corresponding to the icon

    // Add title
    let title = document.createTextNode(" " + node.title);

    // Append icon and title to label
    label.appendChild(icon);
    label.appendChild(title);

    // Append checkbox and label to list item
    listItem.appendChild(checkbox);
    listItem.appendChild(label);

    // Add click listener to label
    label.addEventListener("click", function (e) {
      if (checkbox.checked) {
        icon.textContent = "unfold_more";
      } else {
        icon.textContent = "unfold_less";
      }
    });

    // Create a new ul element only if this node has children
    if (node.children) {
      let newList = document.createElement("ul");
      newList.classList.add("tree");
      listItem.appendChild(newList);
      traverseBookmarks(node.children, newList, newPath);
    }

    // Add class to indicate if the node has children
    if (!listItem.querySelector("ul")) {
      listItem.classList.add("no-children");
    }

    parentElement.appendChild(listItem);
  }
}

let selectedListItemId = null; // Define the variable outside of the DOMContentLoaded event handler

document.addEventListener("DOMContentLoaded", function () {
  // Get the modal
  var modal = document.getElementById("myModal");

  // Get the button that opens the modal
  var btn = document.getElementById("openModal");

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close")[0];

  // Check if the button exists before setting its onclick property
  if (btn) {
    btn.onclick = function () {
      modal.style.display = "block";
    };
  } else {
    console.error("Button with id 'openModal' does not exist.");
  }

  // When the user clicks on <span> (x), close the modal
  if (span) {
    span.onclick = function () {
      modal.style.display = "none";
    };
  }

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };

  var collectInfoButton = document.getElementById("collectInfo");
  var bookmarkTree = document.getElementById("bookmarkTree");
  var exportBookmarkHistory = document.getElementById("exportBookmarkHistory");
  var openAppPage = document.getElementById("openAppPage");

  // Loading menus for bookmark hierarchy...
  chrome.bookmarks.getTree(function (bookmarkTreeNodes) {
    let rootNode = {
      id: "0",
      parentId: "",
      title: "ROOT",
      children: bookmarkTreeNodes[0].children,
    };

    traverseBookmarks([rootNode], bookmarkTree);

    // Attach click events to labels here
    document.querySelectorAll("ul.tree > li > label").forEach(function (label) {
      label.addEventListener("click", function (e) {
        // Remove the "selectedLabel" class from any other labels
        document
          .querySelectorAll("ul.tree > li > label.selectedLabel")
          .forEach(function (selectedLabel) {
            selectedLabel.classList.remove("selectedLabel");
          });

        // Add the "selectedLabel" class to the clicked label
        this.classList.add("selectedLabel");

        // Store the id of the clicked list item
        selectedListItemId = this.previousElementSibling.id;

        // Enable the "Collect Page Info" button if not ROOT
        if (selectedListItemId == 0) {
          collectInfoButton.disabled = true;
          document.querySelector("#selectedFolderName").innerHTML =
            this.previousElementSibling.title;
        } else {
          collectInfoButton.disabled = false;
          document.querySelector("#selectedFolderName").innerHTML =
            this.getAttribute("data-title");
        }

        e.stopPropagation();
      });
    });

    // Event handlers for checkboxes to collapse/expand
    document
      .querySelectorAll("ul.tree > li > input[type='checkbox']")
      .forEach(function (checkbox) {
        checkbox.addEventListener("click", function (e) {
          var nestedUl = this.nextSibling.nextSibling;
          if (nestedUl) {
            nestedUl.style.display =
              nestedUl.style.display == "none" ? "block" : "none";
          }
          e.stopPropagation();
        });
      });
  });

  ////// 북마크 추가 버튼 관련 시퀀스 함수 //////
  // 변수 선언
  const tagsInput = document.getElementById("tagsInput");

  // 북마크 추가 버튼('collect page info') 를 눌렀을 때의 Event Handler
  collectInfoButton.addEventListener("click", function () {
    tagsInput.value = "적절한 태그를 추론하는 중...";
    tagsInput.readOnly = true;

    // Get current tab
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      var activeTab = tabs[0];
      // console.log("active tab: ", activeTab);

      // Bookmarking the current tab
      chrome.bookmarks.create(
        {
          parentId: selectedListItemId, // Use the stored id here
          title: activeTab.title,
          url: activeTab.url,
        },
        function (bookmark) {
          console.log("Page bookmarked:", bookmark);
          alert("Page bookmarked!");
        }
      );

      // 탭 정보를 획득하기 위해 메세지 전송
      function sendMessageToContent(){
        return new Promise((resolve, reject) => {
          chrome.tabs.sendMessage(
            activeTab.id,
            { message: "collect_page_info" },
            function (response) {
              if (response) { // && response.pageInfo) {
                resolve(response);
              }
              else {
                reject();
                console.log("Something went wrong.");
              }
            }
          );
        })
      }
      
      // 함수 실행 및 콘솔 로그 확인 부분
      sendMessageToContent()
        .then(response => {
          console.log(response)
          tags_result = response.tags_result
          
          let tagsArray = tags_result.split(',');

          tagsArray = tagsArray.map(tag => {
              let startIdx = tag.indexOf('(');
              let endIdx = tag.indexOf(')');
              return tag.substring(startIdx+1, endIdx);
          });

          tags_result = tagsArray.join(' | ');
          tagsInput.value = tags_result;  // 태그 추론 결과가 익스텐션에 나타나게 된다.
        })
        .catch(error => {
          console.error(error)
        })
    });
  });

  // Export bookmark 버튼이 눌렸을 경우
  exportBookmarkHistory.addEventListener("click", function () {
    // 1. 북마크 히스토리를 탐색한다.
    // 2. 북마크 히스토리 url을 토대로 content 를 긁어온다.
    // 3. 이를 fetch 하여 서버로 보낸다.

    chrome.bookmarks.getTree(bookmarkTree => {
      processBookmarkTree(bookmarkTree)
      // 북마크 정보 생성되면 then ->
        .then(bookmarkHistory => {
          const promises = bookmarkHistory.map(bookmark => {
            return fetch(bookmark.url)
              .then(response => {
                if (!response.ok) {
                  throw new Error("Error fetching URL: " + bookmark.url);
                }
                return response.text();
              })
              .then(response => {
                if (response.ok){
                  console.log("response is valid!")
                }

                // content, title 긁어오기
                var parser = new DOMParser();
                var doc = parser.parseFromString(response, "text/html");
                const title = doc.title;
                const content = doc.body.innerText;
                // const reference = extractDomain(doc.url);

                bookmark.title = title;
                bookmark.content = content;
                // bookmark.refernce = reference;
                return bookmark;
              })
              .catch(error => {
                // console.error("Error, ", bookmark.url, error);
              });
          });
          return Promise.all(promises)
        })
        .then(bookmarkHistory => {
          // 백그라운드로 userBookmark 정보 전송
          // chrome.runtime.sendMessage({ message: "export_bookmark_history", bookmarkHistory: promises }, function(response){
          //   console.log("response: ", response);
          // });
          
          // console.log("promises: ", promises);
          console.log("bookmarkHistory: ", bookmarkHistory);

          simpleFetcher(SERVER_URL + '/API/post_history/', bookmarkHistory)
            .then(responseData => {
              if (responseData) {
                console.log("Sending bookmarkHistory is done!, ", responseData);
              }
              else {
                console.log("fetcher error.")
              }
            })
        });
    });
  });


// // 정규표현식 for url -> reference
// function extractDomain(url) {
//   var regex = /^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)/im;
//   var match = url.match(regex);
  
//   if (match && match[1]) {
//     var domain = match[1].split('.');
//     return domain[domain.length - 2];
//   }
  
//   return null;
// }


  // app 버튼이 눌렸을 경우
  openAppPage.addEventListener("click", function () {
    chrome.identity.getProfileUserInfo({'accountStatus':'ANY'}, function(userProfile) { 
      const userName = userProfile.email.match(/^([^@]*)@/)[1];

      userInfo = {'id': userProfile['id'], 'email': userProfile['email']}
      console.log("user info in popup: ", userInfo)

      const queryString = new URLSearchParams(userInfo).toString();
      const newTabUrl = `${SERVER_URL}/API/get_my_data/?${queryString}`;
      chrome.tabs.create({ url: newTabUrl});
      // chrome.tabs.create({ url: `${SERVER_URL}/API/get_my_data/?id=${userInfo.id}&email=${userInfo.email}`});

      // simpleFetcher(SERVER_URL + '/API/get_my_data/', userInfo)
      //   .then(responseData => {
      //     if (responseData) {
      //       console.log("Open app page is done!, ", responseData);

      //       const queryString = new URLSearchParams(userInfo).toString();
      //       console.log("URL params: ", queryString)
      //       const newTabUrl = `${SERVER_URL}/API/get_my_data/?${queryString}`;
      //       chrome.tabs.create({ url: newTabUrl});
      //     }
      //     else {
      //       console.log("fetcher error.");
      //     }
      //   })
    });
  });
});

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
      // var username = userInfo.email.match(/^([^@]*)@/)[1];
      var userBookmarkArray = []
      console.log(userInfo)
      function traverseNodes(nodes, ) {
        nodes.forEach(node =>{
          // 노드에 바로 url이 있을 경우(북마크 파일)
          if (node.url) {
            var bookmarkInfo = {
              'customer_id': userInfo.id,
              'url': node.url,
              'title': "",              // 글 원본 제목
              'name': node.title,       // 유저가 원하는 북마크명
              'content': "",            // 글 본문
              'summarize': "",          // 글 본문을 요약한 내용
              'reference': "",          // 글 url에서 플랫폼이 어딘지, ex) naver.com => naver, velog.io => velog
              'topic': "",              // 글 주제 또는 글 카테고리
              'tags': "",               // content를 자동 태깅한 결과
              'created_date': "",       // 북마크 생성 날짜
              'update_date': "",        // 북마크 최근 업데이트 날짜
              'save_path_at_chrome': "", // 크롬에서 북마크가 저장되는 경로
              'save_path_at_ours': "",  // 우리 플랫폼에서 북마크가 저장되는 경로
            };
            userBookmarkArray.push(bookmarkInfo)
            // 추후 url의 context를 가져와야 한다..
          }
          // 노드에 children이 있는 경우(하위 폴더)
          else if (node.children) {
            try{
              if (FolderTitle){
                var FolderTitle = FolderTitle + '/' + node.title;
              } else {
                var FolderTitle = node.title;
              }
            } catch(ReferenceError){
              var FolderTitle = node.title;
            }
            console.log("folder: ", FolderTitle)
            // Process the folder or its children recursively
            traverseNodes(node.children, FolderTitle);
          }
        });
      }
      traverseNodes(bookmarkNodes);
      resolve(userBookmarkArray);
    });
  });
}