// vars instead of consts because elements will change whenever comment current_page is changed
var commentContainers = document.querySelectorAll('.comment');
var editCommentButton = document.getElementById('edit-comment-button');
var commentForm = document.getElementById('comment-form');
var commentFormTextarea = document.getElementById('user-comment-input');
var commentFormRequestDelete = document.getElementById('id_request_delete_comment');
var deleteCommentButton = document.getElementById('delete-comment-button');
var cancelCommentButton = document.getElementById('cancel-comment-button');
var postCommentButton = document.getElementById('post-comment-button');

function setResponsiveCommentHeaderBehaviour() {
    const commentHeaders = document.querySelectorAll('.comment-header');
    commentHeaders.forEach(commentHeader => {
        // If comment-date is not on same line as username --> text-align: left (otherwise, right)
        const commentUsername = commentHeader.querySelector('h2');
        const commentDate = commentHeader.querySelector('.comment-date');
        if (commentDate.getBoundingClientRect().top > commentUsername.getBoundingClientRect().bottom) {
            commentDate.style.textAlign = "left";
        } else {
            commentDate.style.textAlign = ''; // reset to CSS default (should be "right")
        }

        if (commentHeader.scrollWidth > commentHeader.clientWidth) {
            commentHeader.classList.add("compact");
        } else {
            commentHeader.classList.remove("compact");
            const commentEquippedTitles = commentHeader.querySelector('.comment-equipped-titles');
            if (commentHeader.clientWidth < commentEquippedTitles.getBoundingClientRect().width) {
                commentHeader.classList.add("compact");
            }
        }
    });
}

function autofillCommentTextarea(userCommentTextDiv) {
    // Auto-fill commentFormTextarea with user's comment + Set height of textarea to same height as userCommentTextDiv
    let commentFullText = "";
    const paragraphs = userCommentTextDiv.querySelectorAll('p');
    paragraphs.forEach(p => {
        commentFullText += p.textContent + "\n\n";
    });
    commentFormTextarea.value = commentFullText.trim();
    commentFormTextarea.style.height = userCommentTextDiv.scrollHeight + 'px';
}

// In its own function so that pagination.js can call it whenever it fetches a new comment page
function setCommentsBehaviour() {
    commentContainers = document.querySelectorAll('.comment');
    editCommentButton = document.getElementById('edit-comment-button');
    commentForm = document.getElementById('comment-form');
    commentFormTextarea = document.getElementById('user-comment-input');
    commentFormRequestDelete = document.getElementById('id_request_delete_comment');
    deleteCommentButton = document.getElementById('delete-comment-button');
    cancelCommentButton = document.getElementById('cancel-comment-button');
    postCommentButton = document.getElementById('post-comment-button');

    // If the user already posted a comment (i.e., if editCommentButton exists)
    if (editCommentButton != null) {
        const userCommentTextDiv = editCommentButton.parentNode.parentNode.querySelector('.comment-text');
        const userCommentReadMoreButton = editCommentButton.parentNode.parentNode.querySelector('.comment-read-more');

        // Display "Delete" & "Cancel" comment button in form (i.e., will be visible whenever form is visible)
        deleteCommentButton.style.display = 'block';
        cancelCommentButton.style.display = 'block';

        // Set "Edit comment" button behaviour
        editCommentButton.addEventListener('click', function() {
            autofillCommentTextarea(userCommentTextDiv);
            userCommentTextDiv.style.display = 'none';
            userCommentReadMoreButton.style.display = 'none';
            commentForm.style.display = 'flex';
        });

        // Set "Delete" button behaviour for commentForm
        deleteCommentButton.addEventListener('click', function(event) {
            // Blank comments will be deleted by the server (empty comments straight up not processed)
            event.preventDefault();
            commentFormRequestDelete.checked = true;
            commentForm.submit();
        });

        // Set "Cancel" button behaviour for commentForm
        cancelCommentButton.addEventListener('click', function(event) {
            event.preventDefault();
            commentForm.style.display = 'none';
            userCommentTextDiv.style.display = 'block';
            checkNeedSeeMoreButtons(); // defined in global.js
        });

        // No need to set "Post" button behaviour for commentForm --> Default is what we need
    } else if (commentForm != null) {
        commentForm.style.display = 'flex'; // Make commentForm visible
    }
}

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", setCommentsBehaviour);

// Triggers after window has finished loading (i.e., all CSS and JavaScript has already been applied)
window.addEventListener("load", setResponsiveCommentHeaderBehaviour);

// Triggers when window is resized
window.addEventListener("resize", setResponsiveCommentHeaderBehaviour);