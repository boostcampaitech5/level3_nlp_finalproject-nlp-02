chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    let pageInfo = request.pageInfo;

    chrome.identity.getProfileUserInfo({'accountStatus':'ANY'}, function(userInfo) { 
        console.log(userInfo)
        console.log(typeof userInfo)

        // Merge pageInfo and userInfo into totalInfo
        const totalInfo = Object.assign(pageInfo, userInfo);
        console.log(totalInfo)
        console.log(typeof totalInfo)

        // Send data to Server
        fetch('http://101.101.211.226:30006/API/inference', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(totalInfo)
        })
        // .then(response => response.json())
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});