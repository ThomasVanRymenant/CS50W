document.addEventListener('DOMContentLoaded', () => {

    // add event listener to every edit-button
    document.querySelectorAll('.editBtn').forEach(button => {
        button.addEventListener('click', (event) => {
            makePostEditable(event.target);
        })
    });

})


// make a post (to which the clicked edit-button belongs to) editable
function makePostEditable(editButton) {

    // get a reference to the post to which the editButton belongs to
    let postElementId = "#post_" + editButton.dataset.postid;
    let post = document.querySelector(postElementId);

    // stop editing of other post (should there be one in editing)
    let isAlreadyInEditing = false;
    if (document.querySelector('.post-in-edit') != null) { // check if there already is a post in edit-mode

        // if it's another post (not possible through the normal use of the app without developer tools)
        if (post != document.querySelector('.post-in-edit')) {
            stopPostEditing();
        } else { 
            // if it's the same post (than the one which is requested to be edited the most recently)
            isAlreadyInEditing = true;
        }
    }

    // make the post editable if not already
    if (isAlreadyInEditing === false) {

        // mark post as being in edit-mode
        post.classList.add('post-in-edit');

        // hide the edit-button
        editButton.style.display = 'none';

        // change the div (.content) of the post into a (wrapped) textarea (.content)
        let oriContentElement = post.querySelector('.content');
        let content = oriContentElement.innerHTML;
        let editableContentElement = document.createElement('textarea');
        editableContentElement.classList.add('content', 'post-textarea');
        editableContentElement.setAttribute("rows", "1");
        editableContentElement.style.display = 'block';
        editableContentElement.setAttribute('maxlength', "800");
        editableContentElement.innerHTML = content;
        let textareaWrapper = document.createElement('div');
        textareaWrapper.classList.add('textarea-wrapper');
        let customResizeHandle = document.createElement('div');
        customResizeHandle.classList.add('pull-tab');
        textareaWrapper.appendChild(customResizeHandle);
        textareaWrapper.appendChild(editableContentElement);

        post.querySelector('.post-body').replaceChild(textareaWrapper, oriContentElement);

        // show a save-button and save the edited post when it's clicked
        let saveButton = document.createElement('button');
        saveButton.innerHTML = 'Save';
        saveButton.classList.add('btnSavePost');
        saveButton.addEventListener('click', () => {
            savePost(post);
        });
        post.querySelector('.edit-save-btns-container').appendChild(saveButton);

        // focus the content
        editableContentElement.focus();
        // make the cursor jump to the end of the content
        editableContentElement.textContent = editableContentElement.textContent;
    }
}


// save a post and put it out of edit-mode
function savePost(post) {

    // get csrftoken
    const csrftoken = getCookie('csrftoken');

    // send data to server
    fetch('/editPost', {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
            postId: post.dataset.post_id,
            // include the textarea's value
            content: post.querySelector('.content').value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success == true) {
            // update textContent with its current value
            post.querySelector('.content').textContent = post.querySelector('.content').value
        } else {
            if (data.user_is_authenticated) {
                if (data.user_is_authenticated == false) {
                    alert('To edit a post, you need to be logged in');
                }
            } else if (data.error) {
                console.error('Error: ' + data.error);
            }
        }
        stopPostEditing();
    })
    .catch(error => {
        console.error(`Error: ${error}`)
    });
}


// close post(s) that is/are in edit-mode
function stopPostEditing() {

    // get all posts which are in edit-mode
    const postInEditMode = document.querySelector('.post-in-edit');

    // delete the save-button
    postInEditMode.querySelector('.btnSavePost').remove();

    // unhide the edit-button
    postInEditMode.querySelector('.editBtn').style.display = 'block';

    // change the textarea into a div
    const textareaWrapper = postInEditMode.querySelector('.textarea-wrapper');
    const textarea = textareaWrapper.querySelector('.content');
    textarea.blur();
    const newDiv = document.createElement('div');
    newDiv.classList.add('content');
    // assign the original content (textContent, NOT the current value) to div.textContent
    newDiv.textContent = textarea.textContent;
    postInEditMode.querySelector('.post-body').replaceChild(newDiv, textareaWrapper);

    // unmark post as being in edit-mode
    postInEditMode.classList.remove('post-in-edit');
}


// gets cookie by name (copy-pasted)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}