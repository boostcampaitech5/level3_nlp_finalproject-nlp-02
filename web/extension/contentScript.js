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
        context: Array.from(document.querySelectorAll("div")).filter((div) =>
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
        context: iframeDocument.querySelector("div.se-main-container")
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
        context: document.querySelector("div.contents_style").innerText,
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
        context: document.body.innerText,
      };
    }

    console.log("sourceInfo", sourceInfo);

    const pageInfo = Object.assign(urlInfo, sourceInfo);
    console.log("hd", pageInfo);
    // Send response to the popup script - 이게 애초부터 계속 undefined이다...
    sendResponse({ pageInfo: pageInfo });

    // Send the data to the background script
    chrome.runtime.sendMessage(
      { message: "collect_page_info", pageInfo: pageInfo },
      function (response) {
        console.log(response);
      }
    );
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
