window.onload = function() {
    var data = {
        "bookmark_ids": [
            {
                "title": "title1",
                "url": "url1.com",
                "tags": "#foo, #bar"
            },
            {
                "title": "title2",
                "url": "url2.com",
                "tags": "#foobar, #foo"
            },
            {
                "title": "title3",
                "url": "url3.com",
                "tags": "#foo, #foobar"
            }
        ]
    };

    console.log(userBookmark)

    var tags = new Set();
    var selectedTags = new Set();

    data.bookmark_ids.forEach(bookmark => {
        bookmark.tags.split(',').forEach(tag => {
            tags.add(tag.trim());
        });
    });

    tags = Array.from(tags).sort();

    var tagsElement = document.getElementById('tags');
    
    showRows()

    tags.forEach(tag => {
        var tagElement = document.createElement('div');
        tagElement.textContent = tag;
        tagElement.className = 'tag';
        tagElement.onclick = function() {
            if (selectedTags.has(tag)) {
                selectedTags.delete(tag);
                this.classList.remove('selected-tag');
            } else {
                selectedTags.add(tag);
                this.classList.add('selected-tag');
            }
            showSelectedTags();
            showSelectedRows();
        };
        tagsElement.appendChild(tagElement);
    });
    document.getElementById('input-tag').addEventListener('change', () => {
        showInput();
    });
    
    function showInput() {
        
        var inputElement = document.getElementById('input-tag');
        var outputElement = document.getElementById('tag-output');
        var inputValue = inputElement.value.trim();
        outputElement.textContent = "입력된 내용은: " + inputValue;

        if (inputValue !== '') {
            if (tags.indexOf(inputValue) !== -1) {
                if (!selectedTags.has(inputValue)){
                    selectedTags.add(inputValue);

                    // var tagElement = document.createElement('div');
                    // tagElement.className = 'tag selected-tag';
                    // tagElement.textContent = inputValue;
                    // // tagElement.classList.add('selected-tag');
                    // // inputElement.classList.add('selected-tag');
                    // tagsElement.appendChild(tagElement);
                    showSelectedTags();
                    showSelectedRows();
                }
            }else{}
        }

        // Clear the input after adding the tag
        inputElement.value = '';
    }

    function showSelectedTags() {
        var selectedTagsElement = document.getElementById('selected-tags');
        selectedTagsElement.innerHTML = ''; // Clear the previous content
        // selectedTagsElement.innerHTML = 'Selected tags: ' + Array.from(selectedTags).join(', ');
        // selectedTagsElement.innerHTML = Array.from(selectedTags)[0];
        if (selectedTags.size === 0 ) {
            selectedTagsElement.innerHTML = Array.from(selectedTags)
          } else {
            // selectedTagsElement.innerHTML = Array.from(selectedTags)
            var selectedTagsArray = Array.from(selectedTags);
            for (var i = 0; i < selectedTagsArray.length; i++) {
                var blockElement = document.createElement('div');
                blockElement.className = 'selected-tags-block';
                blockElement.textContent = selectedTagsArray[i];
                selectedTagsElement.appendChild(blockElement);
              }
          }
    }

    function showRows(){   
        // selectedTags
        // var table = document.getElementById('bookmarks_whole')
        const dynamicTbody = document.getElementById("bookmarks_whole");
        let html = '';
        for(const bookmark of data.bookmark_ids){
            html += '<tr>';
            html += '<td>'+'<a href="http://' + bookmark.url + '">' + bookmark.title + '</a>'+'</td>';
            html += '<td>'+bookmark.tags+'</td>';
            html += '<td>' + '<div class="tags-block-container"></div>' + '</td>';
            html += '<td>'+ '' + '</td>';
            html += '</tr>';
            }
        dynamicTbody.innerHTML = html;  
    }
    function showSelectedRows() {
        const rows = document.getElementById("bookmarks_whole").querySelectorAll('tr');
        for (const row of rows) {
            const bookmarkTags = row.cells[1].textContent.split(',').map(tag => tag.trim());
            if (selectedTags.size === 0 || bookmarkTags.some(tag => selectedTags.has(tag))) {
              row.style.display = '';
            } else {
              row.style.display = 'none';
            }
        }
    }

    // Function to show the modal
    function showModal() {
        var modal = document.getElementById('myModal');
        modal.style.display = 'block';

        // 바뀐 부분
        var bookmarkInfoElement = document.getElementById('bookmark-info');
        bookmarkInfoElement.innerHTML = ''; // Clear previous content

        // Get the bookmark data for the clicked row
        var row = this.parentNode.parentNode;
        var bookmarkTitle = row.cells[0].querySelector('a').textContent;
        var bookmarkURL = row.cells[0].querySelector('a').href;
        var bookmarkTags = row.cells[1].textContent;

        // Create p elements to show bookmark information
        var titleElement = document.createElement('p');
        titleElement.textContent = 'Title: ' + bookmarkTitle;

        var urlElement = document.createElement('p');
        urlElement.textContent = 'URL: ' + bookmarkURL;

        var tagsElement = document.createElement('p');
        tagsElement.textContent = 'Tags: ' + bookmarkTags;

        // Append the p elements to the bookmark-info div
        bookmarkInfoElement.appendChild(titleElement);
        bookmarkInfoElement.appendChild(urlElement);
        bookmarkInfoElement.appendChild(tagsElement);

        
      
    }
  


    // Add event listener to the button in each row
    var rows = document.getElementById('bookmarks_whole').querySelectorAll('tr');
    rows.forEach(row => {
        var button = document.createElement('button');
        button.textContent = '>';
        button.className = 'modal-btn';
        button.onclick = showModal;
        row.cells[2].appendChild(button);
    });

    // Add event listener to the close button in the modal
    var closeBtn = document.getElementsByClassName('close')[0];
    // closeBtn.addEventListener('click', closeModal);
    closeBtn.onclick = closeModal;

        // Function to close the modal
    function closeModal() {
        var modal = document.getElementById('myModal');
        modal.style.display = 'none';
    }
}