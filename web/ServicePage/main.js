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
            // showBookmarks();
            showSelectedRows();
        };
        tagsElement.appendChild(tagElement);
    });

    function showSelectedTags() {
        var selectedTagsElement = document.getElementById('selected-tags');
        selectedTagsElement.innerHTML = 'Selected tags: ' + Array.from(selectedTags).join(', ');
    }

    function showRows(){   
        // selectedTags
        // var table = document.getElementById('bookmarks_whole')
        const dynamicTbody = document.getElementById("bookmarks_whole");
        let html = '';
        for(const bookmark of data.bookmark_ids){
            html += '<tr>';
            html += '<td>'+bookmark.title+'</td>';
            html += '<td>'+'<a href="http://' + bookmark.url + '">' + bookmark.url + '</a>'+'</td>';
            html += '<td>'+bookmark.tags+'</td>';
            html += '</tr>';
            }
        dynamicTbody.innerHTML = html;
    }
    function showSelectedRows() {
        const rows = document.getElementById("bookmarks_whole").querySelectorAll('tr');
        for (const row of rows) {
            const bookmarkTags = row.cells[2].textContent.split(',').map(tag => tag.trim());
            if (selectedTags.size === 0 || bookmarkTags.some(tag => selectedTags.has(tag))) {
              row.style.display = '';
            } else {
              row.style.display = 'none';
            }
        }
    }
}
