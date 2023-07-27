var userBookmark = [];
var tags = new Set();
var selectedTags = new Set();
var $ = jQuery;

$(document).ready(function() {
    // This part ensures the first character is always '#'
    var placeholderText = "검색할 태그를 입력해 주세요: 형식은 #tag";
    $("#input-tag").on("input", function() {
        var val = $(this).val();
        if (val && val[0] !== "#") {
            $(this).val("#" + val);
        } else if (!val) {
            $(this).val("#");
        }
    }).on("focus", function() {
        var val = $(this).val();
        if (val === "") {
            $(this).val("#");
        }
    }).on("blur", function() {
        var val = $(this).val();
        if (val === "#") {
            $(this).val("");
        }
    }).attr("placeholder", placeholderText);

    console.log(userBookmark)

    // var tags = new Set();
    // var selectedTags = new Set();
    showRows()
    collectAllTags()
    function collectAllTags(){
        tags.clear();
        userBookmark.forEach(bookmark => {
            if (bookmark.tags===null){}
            else{
                bookmark.tags.split(',').forEach(tag => {
                tags.add(tag.trim());
            });
        }
        });

        var tagsElement = document.getElementById('tags');
        tagsElement.innerHTML = ''; // Clear the previous content
        var tags_ = Array.from(tags).sort();
        if (tags_.length != 0) {
            console.log('yes');
            console.log(tags_);
            tags_.forEach(tag => {
                var tagElement = document.createElement('div');
                tagElement.textContent = tag;
                tagElement.className = 'tag';
                tagElement.onclick = function(event) {
                    var tag = tagElement.textContent;
                    selectTags(tag, event.target);
                };
                tagsElement.appendChild(tagElement);
            });
        }else{
            // tagsElement.appendChild();
            console.log('no');
        }
    }

    $(function() {
        var tagArray = Array.from(tags);
        
        $("#input-tag").autocomplete({
          source: function(request, response) {
            var results = $.ui.autocomplete.filter(tagArray, request.term);
            response(results.slice(0, 10));
          },
          minLength: 2, // Show suggestions only after one character is typed
          select: function(event, ui) {
            // code to execute when a suggestion is selected
          }
        });
      });
      

    function selectTags(tag,tagElement){   //클릭으로 태그를 선택하는 함수

        if (selectedTags.has(tag)) {
            selectedTags.delete(tag);
            tagElement.classList.remove('selected-tag');
        } else {
            selectedTags.add(tag);
            tagElement.classList.add('selected-tag');
        }
        showSelectedTags();
        showSelectedRows();
    }

    document.getElementById('input-tag').addEventListener('change', () => {
        selectTagsbyInput();
    });
    
    function selectTagsbyInput() {
        var inputElement = document.getElementById('input-tag');
        var inputValue = inputElement.value.trim();
        var tags_ = Array.from(tags);

    
        if (inputValue !== '') {
            if (tags_.indexOf(inputValue) !== -1) {
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
          } 
          
        else {
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
            
            html += '<tr>';
            // html += '<td>'+'<a href="http://' + bookmark.url + '">' + bookmark.title + '</a>'+'</td>';
            // html += '<tr onClick="window.open(\'' + bookmark.url + '\')">';
            html += '<td onClick="window.open(\'' + bookmark.url + '\')" title="'+bookmark.url+'" style="font-weight: bold;">'+bookmark.name+'</td>';
            html += '<td onClick="window.open(\'' + bookmark.url + '\')" title="'+bookmark.url+'">';
            if (bookmark.tags === null){
                
            }
            else{
                const tagsArray = bookmark.tags.split(',').map(tag => tag.trim());
                for (const tag of tagsArray) {
                    
                    html += '<div class="tag-display">' + tag + '</div>';
                }
                }
            html += '</td>';
            html += '<td>' + '<div class="tags-block-container"></div>' + '</td>';
            html += '<td><input type="checkbox" class="check_btn" ></td>';
            html += '</tr>';
            }
        dynamicTbody.innerHTML = html;  
        showModalBtn()
    }

    $('.check_all').click(function(){ 
    console.log('check');
    if($("input:checkbox[id='check_btn']").prop("checked")){
        $("input[type=checkbox]").prop("checked",true);
    } else{
        $("input[type=checkbox]").prop("checked",true);
    }
     
    });


    function showSelectedRows() {
        const rows = document.getElementById("bookmarks_whole").querySelectorAll('tr');
        for (const row of rows) {
            const bookmarkTags = Array.from(row.cells[1].querySelectorAll('.tag-display')).map(tagElement => tagElement.textContent.trim());
            if (selectedTags.size === 0 || bookmarkTags.some(tag => selectedTags.has(tag))) {
              row.style.display = '';
            } else {
              row.style.display = 'none';
            }
        }
    }

    // Function to show the modal
    function showModal(bookmark) {
        bookmarkIndex = userBookmark.indexOf(bookmark);

        var modal = document.getElementById('myModal');
        modal.style.display = 'block';

        // 바뀐 부분
        var bookmarkInfoElement = document.getElementById('bookmark-info');
        bookmarkInfoElement.innerHTML = ''; // Clear previous content

        // Get the bookmark data for the clicked row
        var bookmarkTitle = bookmark.name;
        var bookmarkURL = bookmark.url;
        var bookmarkTags = bookmark.tags;

        // Create p elements to show bookmark information
        var titleElement = document.createElement('h1');
        titleElement.innerHTML = '<a href="http://' + bookmarkURL + '" title="'+bookmarkURL+'">' + bookmarkTitle + '</a>';
        titleElement.style.fontWeight = 'bold'; 

        // var urlElement = document.createElement('p');
        // urlElement.innerHTML = 'URL: <a href="' + bookmarkURL + '" target="_blank">' + bookmarkURL + '</a>';
        // '<a href="http://' + bookmarkURL + '" title="'+bookmarkURL+'">' + bookmarkTitle + '</a>'

        var tagsElement = document.createElement('p');
        tagsElement.className = 'tags-block-container-modal';
        tagsElement.setAttribute('data-index', bookmarkIndex); 

        tagsElement.innerHTML = '';
        if(bookmarkTags === null){

        }
        else{
            var tagsArray_modal = bookmarkTags.split(',').map(tag => tag.trim());
            for (const tag_ of tagsArray_modal) {
                tagsElement.innerHTML += '<div class="tag-delete">' + tag_ + '</div>';
            }
        }
        
        var addTags = document.createElement('p');
        addTags.innerHTML = '<input type="text" class="flexible-textbox" id = "add-tag"  placeholder="추가할 태그를 입력해 주세요: 형식은 #tag" />';

        // Append the p elements to the bookmark-info div
        bookmarkInfoElement.appendChild(titleElement);
        // bookmarkInfoElement.appendChild(urlElement);
        bookmarkInfoElement.appendChild(tagsElement);
        bookmarkInfoElement.appendChild(addTags);
        
            // modify user tag by adding
        // document.getElementById('add-tag').addEventListener('change', () => {
        //     handleAddTag();
        // });
        addTags.addEventListener('change', event => handleAddTag(event, tagsElement));
        
        var tagDeleteElements = bookmarkInfoElement.querySelectorAll('.tag-delete');

        // Add click event listener to each tag-delete element
        tagDeleteElements.forEach(tagDeleteElement => {
            tagDeleteElement.addEventListener('click', function() {
                // Ask for confirmation before deleting the tag
                var clickedTag = this.textContent;
                var confirmDelete = window.confirm('Do you want to delete the tag: ' + clickedTag + '?');
        
                // If the user confirms the deletion (clicks "OK")
                if (confirmDelete) {
                    // Perform the tag deletion
                    handleDeleteTag(clickedTag, tagsElement);
                } else {
                    // If the user cancels the deletion (clicks "Cancel"), do nothing
                    // You may add additional logic here if needed
                }
            });
        });
        
        
        
    }
    
    function handleAddTag(event, tagsElement) {
        var addTagElement = document.getElementById('add-tag');
        var inputValue = addTagElement.value.trim();

        // Check if the input value is valid (starts with '#')
        if (inputValue && inputValue.startsWith('#')) {
            // Get the bookmark index from the data-index attribute
            var bookmarkIndex = parseInt(tagsElement.getAttribute('data-index'));

            // Update the bookmark's tags in the data.bookmark_ids array
            if (userBookmark[bookmarkIndex].tags===null){
                userBookmark[bookmarkIndex].tags = inputValue;
            }
            else{userBookmark[bookmarkIndex].tags += ', ' + inputValue;}

            // userBookmark[bookmarkIndex].tags += ', ' + inputValue;

            // Clear the input after adding the tag
            addTagElement.value = '';

            // TODO: tag delete / add 클릭에 따라 db update 요청 보내기
            updatedTags = userBookmark[bookmarkIndex].tags.split(',').map(tag => tag.trim());
            updateTag(updatedTags)
                .then(() => {
                    // Update the modal with the updated bookmark

                    showModal(userBookmark[bookmarkIndex]);
                    collectAllTags();
                    showSelectedTags();
                    showRows();
                })

        }
    }

    function handleDeleteTag(tagToDelete, tagsElement) {
        // Get the bookmark index from the data-index attribute
        tagToDelete = tagToDelete
        var bookmarkIndex = parseInt(tagsElement.getAttribute('data-index'));
    
        // Update the bookmark's tags in the data.bookmark_ids array by removing the clicked tag
        var bookmarkTags = userBookmark[bookmarkIndex].tags.split(',').map(tag => tag.trim());
        var updatedTags = bookmarkTags.filter(tag => tag !== tagToDelete);
        console.log('update',updatedTags);
        if (updatedTags.length != 0){
            console.log(updatedTags.length);
            userBookmark[bookmarkIndex].tags = updatedTags.join(', ');}
        else{userBookmark[bookmarkIndex].tags = null;
        console.log('userBookmark',userBookmark[bookmarkIndex].tags);
    }

        // TODO: tag delete / add 클릭에 따라 db update 요청 보내기
        updateTag(updatedTags)
            .then(() => {
                // Update the modal with the updated bookmark

                showModal(userBookmark[bookmarkIndex]);
                collectAllTags();
                showSelectedTags();
                showRows();
            })
        
    }
  

    function showModalBtn(){
        // Add event listener to the button in each row
        var rows = document.getElementById('bookmarks_whole').querySelectorAll('tr');
        rows.forEach(row => {
            var button = document.createElement('button');
            button.textContent = '>';
            button.className = 'modal-btn';
            // button.onclick = showModal;
            button.onclick = function() {
                var bookmark = userBookmark[row.rowIndex - 1]; // Get the corresponding bookmark object
                showModal(bookmark, userBookmark); // Pass the 'bookmark' object as an argument
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

    // 삭제 및 추가 된 태그 정보를 서버로 전송하는 함수
    function updateTag(updatedTags){
        totalDataForUpdate = {
            'customer_id': customer_id,             // index.html 로 부터 획득
            'bookmark_no': userBookmark[bookmarkIndex].bookmark_no,
            'new_tags': updatedTags
        };
        
        return fetch(SERVER_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(totalDataForUpdate)
            })
            .then((response) => {
                if (response.ok) {
                return response.json();
                } else {
                throw new Error('Network response is not ok')
                }
            }) 
            .catch(error =>{
            console.error('Error:', error);
            })
    }
});
