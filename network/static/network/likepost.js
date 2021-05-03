document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll(".likeBtn").forEach(btn => {
        btn.addEventListener('click', (event) => {

            // get the post (based on the like-button that is clicked)
            let possiblePost = event.target;
            do {
                possiblePost = possiblePost.parentElement;
            } while (possiblePost.classList.contains('post') == false)

            toggleLike(possiblePost);
        })
    })
});


// like/unlike
function toggleLike(post) {

    // get csrftoken
    const csrftoken = getCookie('csrftoken');

    // send request to like/unlike the post
    fetch('/like', {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
            post_id: post.dataset.post_id
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success == true) {
            
            // toggle icon (based on liked or unliked)
            if (data.liked_or_unliked == 'liked') {

                // change like-icon displayed to a liked icon
                post.querySelector('#like-btn').style.display = 'none';
                post.querySelector('#liked-btn').style.display = 'inline-block';

                // update the number of likes
                let likeCountEl = post.querySelector('.like-count');
                likeCountEl.classList.remove('txt-grey');
                likeCountEl.classList.add('txt-rouge');
                likeCountEl.textContent = parseInt(likeCountEl.textContent) + 1;
            } else {

                // change like-icon displayed to a yet-to-like icon
                post.querySelector('#liked-btn').style.display = 'none';
                post.querySelector('#like-btn').style.display = 'inline-block';

                // update the number of likes
                let likeCountEl = post.querySelector('.like-count');
                likeCountEl.classList.remove('txt-rouge');
                likeCountEl.classList.add('txt-grey');
                likeCountEl.textContent = parseInt(likeCountEl.textContent) - 1;
            }
        } else {
            if (data.user_is_authenticated == false) {
                alert('To like a post, you need to be logged in.');
            }
        }
    })
    .catch(error => console.error(`Error: ${error}`));
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