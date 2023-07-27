// message listener
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  console.log("chrome.runtime.onMessage.addListener called!! ");
  if (request.message === "collect_page_info") {
    // Gather the pageInfo from DOM
    const urlInfo = {
      url: window.location.href,
    };

    let sourceInfo;

    if (
      urlInfo.url.startsWith("https://velog.io") ||
      urlInfo.url.startsWith("http://velog.io")
    ) {
      console.log("This is velog page");

      let clue;

      if (document.querySelectorAll(".sc-bTfYFJ").length > 0) {
        clue = Array.from(document.querySelectorAll(".sc-bTfYFJ")).map(
          (tag) => tag.innerText
        );
      } else {
        clue = Array.from(document.querySelectorAll(".sc-fWCJzd")).map(
          (tag) => tag.innerText
        );
      }

      sourceInfo = {
        title: document.querySelector("div.head-wrapper h1").innerText,
        content: Array.from(document.querySelectorAll("div")).filter((div) =>
          div.classList.contains("atom-one")
        )[0].innerText,
        clue: clue,
      };
    } else if (
      urlInfo.url.startsWith("https://blog.naver.com") ||
      urlInfo.url.startsWith("http://blog.naver.com")
    ) {
      console.log("This is naverBlog page");

      var iframe = document.querySelector("iframe#mainFrame");
      var iframeDocument =
        iframe.contentDocument || iframe.contentWindow.document;

      let clue;

      if (iframeDocument.querySelector("h4.title") !== null) {
        clue = iframeDocument.querySelector("h4.title strong").innerText;
      } else if (iframeDocument.querySelector("span.cate") !== null) {
        clue = iframeDocument.querySelector("span.cate").innerText;
      } else {
        clue = null;
      }

      sourceInfo = {
        title: iframeDocument.querySelector("div.se-module").innerText,
        content: iframeDocument.querySelector("div.se-main-container")
          .innerText,
        clue: clue,
      };
    } else if (
      document
        .querySelector('meta[property="article:pc_service_home"]')
        .content.endsWith("tistory.com")
    ) {
      console.log("This is tistoryBlog page");

      sourceInfo = {
        title: document.querySelector('meta[name="title"]').content,
        content: document.querySelector("div.contents_style").innerText,
        clue: document
          .querySelector("div.another_category")
          .querySelector("h4")
          .innerText.split(" 카테고리의 다른 글")[0]
          .split(" > "),
      };
    } else {
      console.log("Not assigned blog");

      sourceInfo = {
        title: document.title,
        content: document.body.innerText,
      };
    }

    console.log("sourceInfo", sourceInfo);

    const pageInfo = Object.assign(urlInfo, sourceInfo);
    console.log("hd", pageInfo);

    ////// 북마크 태그 정보 송수신 파트 //////
    // Send response to the popup script -> 시퀀스 변경. 백그라운드에서 response 획득 시 보내는 것으로.
    // sendResponse({ pageInfo: pageInfo });

    // 함수 선언 - 백그라운드로 메세지 보내고 대기
    function sendMessageToBackground(message){
      return new Promise( function(resolve, reject) {
        chrome.runtime.sendMessage(message, function(response) {
          if (response){
            resolve(response);
          } else {
            reject();
          }
        })
      })
    }

    // 송신 함수 수행 - 백그라운드로부터 메세지를 받았다면
    sendMessageToBackground({
      message: "collect_page_info",
      pageInfo: pageInfo,
    })
      .then((responseData) =>{
        console.log("Response from background script:", responseData);
        sendResponse( { tags_result: responseData['tags_result'], pageInfo: pageInfo })
      })
      .catch((error) =>{
        console.error("ERROR in contentScript.js, ", error);
      })

  return true;  
  }

  // collect only page's content
  else if (request.message === "collect_page_only_content") {
    const rawContent = {
      content: document.body.innerText,
    };
    // console.log("rconent: ", rcontent);
    sendResponse({
      message: "collect_page_only_content",
      onlyPage: rawContent,
    });

    // Send the data to the background script
    chrome.runtime.sendMessage(
      { message: "collect_page_only_content", onlyPage: rawContent },
      function (response) {
        console.log(response);
      }
    );
    return true;
  }
});

// connection checker from background.js
const port = chrome.runtime.connect({ name: "contentScriptConnection" });

// Example: Sending a message to the background script
port.postMessage({ message: "Hello from the content script!" });

// Example: Receiving a message from the background script
port.onMessage.addListener(function (message) {
  console.log("Received message from background script:", message);
});
