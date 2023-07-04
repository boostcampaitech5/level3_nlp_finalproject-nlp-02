document.addEventListener('DOMContentLoaded', function() {
  var bookmarkButton = document.getElementById('bookmarkButton');
  var exportButton = document.getElementById('exportButton');

  bookmarkButton.addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      var url = tabs[0].url;
      var title = tabs[0].title;

      // Bookmark the page
      chrome.bookmarks.create({title: title, url: url}, function(bookmark) {
        alert('Page bookmarked successfully!');
      });
    });
  });

  exportButton.addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      var tab = tabs[0];

      // Send a message to the content script to retrieve the page's contents
      chrome.tabs.sendMessage(tab.id, {action: 'get_page_contents'}, function(response) {
        if (response && response.contents) {
          // Process the page contents (e.g., save to a file, display in a popup, etc.)
          var pageContents = response.contents;
          console.log(pageContents);
          // You can perform further processing or export the contents as needed
          alert('Page contents exported!' + pageContents);
        } else {
          alert('Failed to retrieve page contents.');
        }
      });
    });
  });
});
