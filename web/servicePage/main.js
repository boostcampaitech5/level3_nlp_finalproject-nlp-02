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
            showBookmarks();
        };
        tagsElement.appendChild(tagElement);
    });

    function showSelectedTags() {
        var selectedTagsElement = document.getElementById('selected-tags');
        selectedTagsElement.innerHTML = 'Selected tags: ' + Array.from(selectedTags).join(', ');
    }

    function showBookmarks() {
        var bookmarksElement = document.getElementById('bookmarks');
        bookmarksElement.innerHTML = '';
        data.bookmark_ids.forEach(bookmark => {
            var bookmarkTags = bookmark.tags.split(',').map(tag => tag.trim());
            for (let i = 0; i < bookmarkTags.length; i++) {
                if (selectedTags.has(bookmarkTags[i])) {
                    var bookmarkElement = document.createElement('div');
                    bookmarkElement.className = 'bookmark';
                    bookmarkElement.innerHTML = '<h2>' + bookmark.title + '</h2><a href="http://' + bookmark.url + '">' + bookmark.url + '</a>';
                    bookmarksElement.appendChild(bookmarkElement);
                    break;
                }
            }
        });
    }
}
