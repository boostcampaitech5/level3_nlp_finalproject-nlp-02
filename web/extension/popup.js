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

  // When button is pushed...
  collectInfoButton.addEventListener("click", function () {
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

      // Send a message to the current tab to collect page info
      chrome.tabs.sendMessage(
        activeTab.id,
        { message: "collect_page_info" },
        function (response) {
          if (response && response.pageInfo) {
            console.log(response);
            // let pageInfo = response.pageInfo;
            // alert(pageInfo);
          }
          else {
            console.log("Something went wrong.");
          }
        }
      );
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

                bookmark.title = title;
                bookmark.content = content;
                return bookmark;
              })
              .catch(error => {
                // console.error("Error, ", bookmark.url);
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

          simpleFetcher('http://118.67.131.212:30005/API/post_history/', bookmarkHistory)
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
              'title': "",
              'bookmarkTitle': node.title,
              'content': "",
              'folderName': "",
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