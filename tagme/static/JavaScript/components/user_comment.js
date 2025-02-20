// vars instead of consts because elements will change whenever comment current_page is changed
var commentContainers = document.querySelectorAll('.comment');
var editCommentButton = document.getElementById('edit-comment-button');
var commentForm = document.getElementById('comment-form');
var commentFormTextarea = document.getElementById('user-comment-input');
var commentFormRequestDelete = document.getElementById('id_request_delete_comment');
var deleteCommentButton = document.getElementById('delete-comment-button');
var cancelCommentButton = document.getElementById('cancel-comment-button');

let isReadingMoreComment = false;

function setResponsiveCommentHeaderBehaviour() {
    // TODO: Test when no comments in page

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


/* TODO
function toggleCommentReadMore(commentTextDiv, readMoreCommentButton) {
    if (isReadingMoreComment) {
        // If user is reading more --> button should say "Read Less"
        commentTextDiv.classList.remove('reading-less');
        commentTextDiv.style.maxHeight = 'fit-content';
        readMoreCommentButton.innerHTML = 'Read less <i class="fa fa-angle-up" aria-hidden="true"></i>';
    }
    else {
        // If user is reading less (i.e., button should say "Read More")
        commentTextDiv.classList.add('reading-less'); // Only apply gradient if button says "Read More"
        commentTextDiv.style.maxHeight = '125px';
        readMoreCommentButton.innerHTML = 'Read more <i class="fa fa-angle-down" aria-hidden="true"></i>';
    }
}

function checkCommentOverflow(commentTextDiv, readMoreCommentButton) {
    // If commentTextDiv is overflowing its commentContainer on page load or resize --> show "Read More" button
    if (commentTextDiv.scrollHeight > 125) { // Need to show "Read More" button
        readMoreCommentButton.style.display = 'inline-block';
        isReadingMoreComment = false;
        toggleCommentReadMore(commentTextDiv, readMoreCommentButton);
    } else { // If commentTextDiv is NOT overflowing --> don't need to show "Read More" button
        readMoreCommentButton.style.display = 'none';
        isReadingMoreComment = true; // Is technically "reading more" because everything is visible (no overflow)
        toggleCommentReadMore(commentTextDiv, readMoreCommentButton);
    }
}

function checkAllCommentsOverflow() {
    // Need this function for the 100ms timeout on page resize
    // Otherwise, would timeout 100ms after checking EACH comment
    if (commentContainers != null) {
        commentContainers.forEach(commentContainer => {
            commentTextDiv = commentContainer.querySelector('.comment-text');
            readMoreCommentButton = commentContainer.querySelector('.comment-read-more');
            checkCommentOverflow(commentTextDiv, readMoreCommentButton);
        })
    }
}
*/

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

function updateCommentText(userCommentTextDiv) {
    // Doing this in JavaScript instead of requiring a page reload (smoother experience)
    userCommentTextDiv.innerHTML = ''; // Empty out userCommentTextDiv
    const paragraphs = commentFormTextarea.value.split("\n\n");
    paragraphs.forEach(textString => {
        const p = document.createElement("p");
        lineBreaks = textString.split('\n');
        lineBreaks.forEach(line => {
            textLine = document.createTextNode(line);
            p.appendChild(textLine);
            p.appendChild(document.createElement("br"));s
        })
        userCommentTextDiv.appendChild(p);
    });
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
            // TODO checkCommentOverflow(userCommentTextDiv, userCommentReadMoreButton);
        });

        // No need to set "Post" button behaviour for commentForm --> Default is what we need
    } else if (commentForm != null) {
        commentForm.style.display = 'flex'; // Make commentForm visible
    }

    /*
    // TODO Set "Read More" button behaviour (for comments)
    if (commentContainers != null) {
        commentContainers.forEach(commentContainer => {
            commentTextDiv = commentContainer.querySelector('.comment-text');
            readMoreCommentButton = commentContainer.querySelector('.comment-read-more');

            // For each comment --> Determine if "Read More" button should be displayed or not
            // TODO checkCommentOverflow(commentTextDiv, readMoreCommentButton);

            // For each comment --> Set behaviour of "Read More" button
            readMoreCommentButton.addEventListener('click', function () {
                isReadingMoreComment = isReadingMoreComment === true ? false : true;
                toggleCommentReadMore(commentTextDiv, readMoreCommentButton);
            });
        });
    }
    */
}

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", setCommentsBehaviour);

// Triggers after window has finished loading (i.e., all CSS and JavaScript has already been applied)
window.addEventListener("load", setResponsiveCommentHeaderBehaviour);

// Triggers when window is resized
window.addEventListener("resize", setResponsiveCommentHeaderBehaviour);

/*
// Triggers when viewport is resized --> in item_page.js
let resizeCommentTimeout;
window.addEventListener("resize", () => {
    clearTimeout(resizeCommentTimeout);
    resizeCommentTimeout = setTimeout(checkAllCommentsOverflow, 100); // Only run the function every 100ms minimum
});
*/
