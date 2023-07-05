document.addEventListener('DOMContentLoaded', function() {
  var collectInfoButton = document.getElementById('collectInfo');

  // When button is pushed...
  collectInfoButton.addEventListener('click', function() {
    // Get current tab
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      var activeTab = tabs[0];
      console.log(typeof activeTab)
      console.log(activeTab)

      // Bookmarking the current tab
      chrome.bookmarks.create({ title: activeTab.title, url: activeTab.url }, function (bookmark) {
        console.log('Page bookmarked:', bookmark);
        alert('Page bookmarked!');
      });
      
      // Send a message to the current tab to collect page info 
      chrome.tabs.sendMessage(activeTab.id, {"message": "collect_page_info"}, function(response) {
        if (response && response.pageInfo) {
          console.log(response);
          let pageInfo = response.pageInfo;
          alert(pageInfo);
        }
      });
    });
  });
});
