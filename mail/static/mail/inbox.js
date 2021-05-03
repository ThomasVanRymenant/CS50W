document.addEventListener('DOMContentLoaded', function () {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => {
        // NOTE: push a new state after the load_mailbox function (not inside of it), 
        // so a new state won't be created AGAIN when we call load_mailbox onpopstate-event, 
        // in order to restore the state (browser's back-button functionality)
        load_mailbox('inbox');
        history.pushState({ mailbox: 'inbox' }, "", `/inbox`);
    });
    document.querySelector('#sent').addEventListener('click', () => {
        load_mailbox('sent');
        history.pushState({ mailbox: 'sent' }, "", `/sent`);
    });
    document.querySelector('#archived').addEventListener('click', () => {
        load_mailbox('archive');
        history.pushState({ mailbox: 'archive' }, "", `/archive`);
    });
    document.querySelector('#compose').addEventListener('click', () => {
        compose_email();
        history.pushState({ compose: true }, "", `/compose`);
    });

    // By default, load the inbox
    load_mailbox('inbox');
    history.pushState({ mailbox: 'inbox' }, "", `/inbox`);

    // notice when the user submits a new email
    document.querySelector('#compose-form').addEventListener('submit', (event) => {

        // call function that sends email
        send_email();

        // prevent form from actually submitting
        event.preventDefault();
    });
});


function compose_email() {

    document.querySelector('#compose-form-title').innerHTML = 'New Email';

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-detailed-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
}


function load_mailbox(mailbox) {

    // Show the mailbox and hide other views
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-detailed-view').style.display = 'none';
    document.querySelector('#emails-view').style.display = 'block';

    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    // fetch and render emails from the relevant mailbox
    fetch_render_emails(mailbox);
}

// Send email
function send_email() {

    // post email to server and load the sent mailbox after that
    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: document.querySelector('#compose-recipients').value,
            subject: document.querySelector('#compose-subject').value,
            body: document.querySelector('#compose-body').value
        })
    })
        .then(response => response.json())
        .then(() => {

            // load sent mailbox and create a new history entry
            load_mailbox('sent');
            history.pushState({ mailbox: 'sent' }, "", `/sent`);
        })
        .catch(error => alert(`Network ${error}`));
}


function fetch_render_emails(mailbox) {

    fetch(`/emails/${mailbox}`)
        .then(response => response.json())
        .then(emails => {

            // indicate when mailbox is empty 
            if (emails.length === 0) {
                let emptyMessage = document.createElement('div');
                emptyMessage.textContent = 'Mailbox is empty';
                document.querySelector('#emails-view').append(emptyMessage);
            }

            // render emails
            emails.forEach(email => {

                // create email's info element container
                let emailRow = document.createElement('div');
                if (email.read) {
                    emailRow.classList.add('read');
                }
                emailRow.classList.add('email');
                emailRow.addEventListener('click', function () {
                    view_email(email.id);
                    history.pushState({ email_id: email.id }, "", `/email/${email.id}`)
                });

                // create email's info elements
                let senderEl = document.createElement('span');
                let subjectEl = document.createElement('span');
                let timestampEl = document.createElement('span');
                senderEl.textContent = `${email.sender}`;
                subjectEl.textContent = `${email.subject}`;
                timestampEl.textContent = `${email.timestamp}`;
                senderEl.classList.add('sender', 'truncate-1l');
                subjectEl.classList.add('subject', 'truncate-1l');
                timestampEl.classList.add('timestamp', 'font-s-sm');

                // append info-elements to their container
                emailRow.append(senderEl, subjectEl, timestampEl);

                // append email to wrapper (for the purpose of allowing a cool hover effect by relative and absolute positioning)
                let wrapper = document.createElement('div');
                wrapper.classList.add('wrapper');
                wrapper.append(emailRow);

                // add email to list of emails
                document.querySelector('#emails-view').append(wrapper);
            })
        });
}


function view_email(emailId) {
    // fetch email data and render it
    fetch(`/emails/${emailId}`)
        .then(response => response.json())
        .then(email => {

            // populate email info
            email_view = document.querySelector("#email-detailed-view");
            email_view.querySelector("#sender").textContent = email.sender;
            email_view.querySelector("#recipients").textContent = email.recipients;
            email_view.querySelector("#subject").textContent = email.subject;
            email_view.querySelector("#timestamp").textContent = email.timestamp;
            email_view.querySelector("#body").textContent = email.body;

            // show archive/unarchive button (except for the 'sent mailbox')
            if (email.sender === document.querySelector('#logged-in-user-email').textContent) {

                // hide archive/unarchive button
                document.querySelector('#archiveBtn').style.display = 'none';

            } else {

                // poppulate button as needed
                let archiveBtn = document.querySelector('#archiveBtn');
                if (!email.archived) {
                    archiveBtn.innerHTML = '<span style="margin: 0px 3px;">Archive</span><span class="material-icons">archive</span>';
                    archiveBtn.onclick = function () {
                        archive_email(emailId);
                    }
                } else {
                    archiveBtn.innerHTML = '<span style="margin: 0px 3px;">Unarchive</span><span class="material-icons">unarchive</span>';
                    archiveBtn.onclick = function () {
                        unarchive_email(emailId);
                    }
                }

                // show archive/unarchive button
                archiveBtn.style.display = 'flex';
            }

            // Notice when user clicks reply-button
            document.querySelector('#replyBtn').onclick = function () {
                compose_reply(email);
                history.pushState({ reply: true, email: email }, "", `/reply/${emailId}`);
            }

            // mark email as read
            if (!email.read) {
                mark_as_read(emailId);
            }
        });

    // Show email_detailed view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-detailed-view').style.display = 'block';
}


function mark_as_read(emailId) {
    fetch(`/emails/${emailId}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
    })
        .catch(error => alert(`Error: ${error}`));
}


function archive_email(emailId) {
    return fetch(`/emails/${emailId}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: true
        })
    })
        .then(response => load_mailbox('inbox'))
        .catch(error => alert(`Error: ${error}`));
}


function unarchive_email(emailId) {
    // mark email as unarchived and load inbox
    return fetch(`/emails/${emailId}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: false
        })
    })
        .then(load_mailbox('inbox'))
        .catch(error => alert(`Error: ${error}`));
}


function compose_reply(email) {

    // open the compose-email view
    compose_email();

    // overwrite form-title
    document.querySelector('#compose-form-title').innerHTML = 'Reply';

    // pre-fill recipients, subject, body
    document.querySelector('#compose-recipients').value = email.sender;
    document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:\n${email.body}\n\n`;
    console.log(document.querySelector('#compose-body').value);
    if (email.subject.slice(0, 3).toLowerCase() !== "re:") {
        document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
    } else {
        document.querySelector('#compose-subject').value = `${email.subject}`;
    }
}


// make the user able to go back in history
window.onpopstate = function (event) {
    if (event.state.mailbox != undefined) {
        load_mailbox(event.state.mailbox);
    } else if (event.state.email_id != undefined) {
        view_email(event.state.email_id);
    } else if (event.state.compose != undefined) {
        compose_email();
    } else if (event.state.reply != undefined) {
        compose_reply(event.state.email)
    }
}