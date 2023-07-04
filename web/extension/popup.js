document.addEventListener('DOMContentLoaded', function() {
  var collectInfoButton = document.getElementById('collectInfo');
      // Query for the active tab in the current window
      chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
          var activeTab = tabs[0];
          console.log(typeof activeTab)
          console.log(activeTab)

          // Adding bookmarks
          collectInfoButton.addEventListener('click', function() {
            chrome.bookmarks.create({ title: activeTab.title, url: activeTab.url }, function (bookmark) {
              console.log('Page bookmarked:', bookmark);
              alert('Page bookmarked!');
          });

          // Send a message to the active tab to collect page info
          chrome.tabs.sendMessage(activeTab.id, {"message": "collect_page_info"}, function(response) {
            if (response && response.pageInfo) {
              let pageInfo = response.pageInfo
              alert(pageInfo)
            };
              console.log(response)
          });
      });
  });
});
