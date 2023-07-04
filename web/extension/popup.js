document.addEventListener('DOMContentLoaded', function() {
  var collectInfoButton = document.getElementById('collectInfo');
  
  collectInfoButton.addEventListener('click', function() {
      // Query for the active tab in the current window
      chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
          var activeTab = tabs[0];
          console.log(typeof activeTab)
          console.log(activeTab)
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
