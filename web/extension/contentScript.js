chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.message === 'collect_page_info') {
        // Gather the necessary page data
        let pageInfo = {
            title: document.title,
            url: window.location.href,
            docs: document.body.innerText,
        };

        sendResponse({pageInfo: pageInfo})

        // Send the data to the background script
        chrome.runtime.sendMessage({pageInfo: pageInfo}, function(response) {
            console.log(response);
        });
    }
});
