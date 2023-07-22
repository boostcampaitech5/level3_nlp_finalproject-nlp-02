window.onload = function() {

    console.log(userBookmark)

    var tags = new Set();
    var selectedTags = new Set();

    userBookmark.forEach(bookmark => {
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
        outputElement.textContent = "입력된 내용: " + inputValue;
    
        if (inputValue !== '') {
            if (tags.indexOf(inputValue) !== -1) {
                if (!selectedTags.has(inputValue)){
                    selectedTags.add(inputValue);
    
                    // find the corresponding tag in the UI and add the 'selected-tag' class
                    var tagElements = Array.from(document.querySelectorAll('#tags .tag'));
                    var tagElement = tagElements.find(element => element.textContent === inputValue);
                    if (tagElement) {
                        tagElement.classList.add('selected-tag');
                    }
    
                    showSelectedTags();
                    showSelectedRows();
                }
            }
        }
    
        // Clear the input after adding the tag
        inputElement.value = '';
    }
    

    function showSelectedTags() {
        var selectedTagsElement = document.getElementById('selected-tags');
        selectedTagsElement.innerHTML = ''; // Clear the previous content
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
        const dynamicTbody = document.getElementById("bookmarks_whole");
        let html = '';
        for(const bookmark of userBookmark){
            const tagsArray = bookmark.tags.split(',').map(tag => tag.trim());
            html += '<tr>';
            // html += '<td>'+'<a href="http://' + bookmark.url + '">' + bookmark.title + '</a>'+'</td>';
            // html += '<tr onClick="window.open(\'' + bookmark.url + '\')">';
            html += '<td onClick="window.open(\'' + bookmark.url + '\')">'+bookmark.title+'</td>';
            html += '<td onClick="window.open(\'' + bookmark.url + '\')">';
            for (const tag of tagsArray) {
                html += '<div class="tag">' + tag + '</div>';
            }
            html += '</td>';
            html += '<td>' + '<div class="tags-block-container"></div>' + '</td>';
            html += '</tr>';
            }
        dynamicTbody.innerHTML = html;  
    }
    function showSelectedRows() {
        const rows = document.getElementById("bookmarks_whole").querySelectorAll('tr');
        for (const row of rows) {
            const bookmarkTags = Array.from(row.cells[1].querySelectorAll('.tag')).map(tagElement => tagElement.textContent.trim());
            if (selectedTags.size === 0 || bookmarkTags.some(tag => selectedTags.has(tag))) {
              row.style.display = '';
            } else {
              row.style.display = 'none';
            }
        }
    }

    // Function to show the modal
    function showModal(bookmark) {
        var modal = document.getElementById('myModal');
        modal.style.display = 'block';

        // 바뀐 부분
        var bookmarkInfoElement = document.getElementById('bookmark-info');
        bookmarkInfoElement.innerHTML = ''; // Clear previous content

        // Get the bookmark data for the clicked row
        var bookmarkTitle = bookmark.title;
        var bookmarkURL = bookmark.url;
        var bookmarkTags = bookmark.tags;

        // Create p elements to show bookmark information
        var titleElement = document.createElement('p');
        titleElement.textContent = 'Title: ' + bookmarkTitle;

        var urlElement = document.createElement('p');
        urlElement.innerHTML = 'URL: <a href="' + bookmarkURL + '" target="_blank">' + bookmarkURL + '</a>';

        var tagsElement = document.createElement('p');
        tagsElement.textContent = 'Tags: ' + bookmarkTags;

        var tmp = document.createElement('p');
        tmp.innerHTML = '<span class="tags">x &times;</span>';

        // Append the p elements to the bookmark-info div
        bookmarkInfoElement.appendChild(titleElement);
        bookmarkInfoElement.appendChild(urlElement);
        bookmarkInfoElement.appendChild(tagsElement);
        bookmarkInfoElement.appendChild(tmp);
    }
  


    // Add event listener to the button in each row
    var rows = document.getElementById('bookmarks_whole').querySelectorAll('tr');
    rows.forEach(row => {
        var button = document.createElement('button');
        button.textContent = '>';
        button.className = 'modal-btn';
        // button.onclick = showModal;
        button.onclick = function() {
            var bookmark = userBookmark[row.rowIndex - 1]; // Get the corresponding bookmark object
            showModal(bookmark); // Pass the 'bookmark' object as an argument
        };
        row.cells[2].appendChild(button);
    });
    // Add event listener to the close button in the modal
    var closeBtn = document.getElementsByClassName('close')[0];
    // closeBtn.addEventListener('click', closeModal);
    closeBtn.onclick = closeModal;
    // Add an event listener to the overlay (modal) to close it when clicked outside the modal content
    var modal = document.getElementById('myModal');
    modal.addEventListener('click', function(event) {
    if (event.target === modal) {
        closeModal();
    }
    });
        // Function to close the modal
    function closeModal() {
        var modal = document.getElementById('myModal');
        modal.style.display = 'none';
    }

}
