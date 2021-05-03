document.addEventListener("DOMContentLoaded", () => {
    const followBtn = document.querySelector('#follow-btn');
    if (followBtn != null) {
        followBtn.addEventListener('click', () => {
            toggleFollow();
        });
    }
})


// send AJAX request to follow/unfollow user and change follow-btn's text
function toggleFollow() {

    // get csrftoken
    const csrftoken = getCookie('csrftoken');

    // send to server: the id of the user who needs te be followed/unfollwed
    fetch(`/follow`, {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
            id: document.querySelector("#profile-header").dataset.p
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success == true) {

            // change button's text
            followBtnText = document.querySelector('#follow-btn');
            followBtnText.innerHTML === 'Follow' ? followBtnText.innerHTML = 'Unfollow' : followBtnText.innerHTML = 'Follow';
            
            // update followers count
            const followersAmountEL = document.getElementById('profile-header').querySelector('.followers').querySelector('.amount');
            if (data.followed_or_unfollowed === 'followed') {
                followersAmountEL.textContent = parseInt(followersAmountEL.textContent) + 1;
            } else {
                followersAmountEL.textContent = parseInt(followersAmountEL.textContent) - 1;
            }
        } else {
            if (data.user_is_authenticated) {
                if (data.user_is_authenticated == false) {
                    alert('To follow someone, you need to be logged in.');
                }
            }
            if (data.error) {
                console.error(`Error: ${data.error}`)
            }
        }
    })
    .catch(error => console.error(`Error: ${error}`));
}


// gets cookie by name
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
