// Function to handle the bookmarking process
function bookmarkCurrentPage() {
  // Query the active tab
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    var tab = tabs[0];
    console.log(tab)
    // Bookmark the current page
    chrome.bookmarks.create({ title: tab.title, url: tab.url }, function (bookmark) {
      console.log('Page bookmarked:', bookmark);
      alert('Page bookmarked!');
    });

    // Send messages to background
    chrome.runtime.sendMessage({ IsBookmarkClick: true });

    // Get bookmarked urls' content(본문내용) - interaction with content.js
    chrome.tabs.sendMessage(tab.id, {action: 'get_page_contents'}, function(response) {
      if (response && response.contents) {
        var pageContents = response.contents;
        console.log(pageContents)

        chrome.runtime.sendMessage({ pageContents: pageContents });
      }
      else{
        alert('Failed to retrieve page contents.')
      }
    });
  });
}

// Add an event listener to the button
document.addEventListener('DOMContentLoaded', function () {
  var bookmarkButton = document.getElementById('bookmarkButton');
  bookmarkButton.addEventListener('click', bookmarkCurrentPage);
});