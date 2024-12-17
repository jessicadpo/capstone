const commentContainers = document.querySelectorAll('.comment');
const editCommentButton = document.getElementById('edit-comment-button');
const commentForm = document.getElementById('comment-form');
const commentFormTextarea = document.getElementById('user-comment-input');
const cancelCommentButton = document.getElementById('cancel-comment-button');
const postCommentButton = document.getElementById('post-comment-button');

let isReadingMoreComment = false;

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
    // TODO: CONTROL FOR WHEN COMMENT IS EMPTIED OUT --> treat as "delete comment" (?)
    // TODO: Add "Delete" button on left-most side of form buttons instead? (& treat empty as form error? or also as delete?)
    // Doing this in JavaScript instead of requiring a page reload (smoother experience)
    userCommentTextDiv.innerHTML = ''; // Empty out userCommentTextDiv
    const paragraphs = commentFormTextarea.value.split("\n\n");
    paragraphs.forEach(textString => {
        const p = document.createElement("p");
        lineBreaks = textString.split('\n');
        lineBreaks.forEach(line => {
            textLine = document.createTextNode(line);
            p.appendChild(textLine);
            p.appendChild(document.createElement("br"));
        })
        userCommentTextDiv.appendChild(p);
    });
}


// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function () {
    // If the user already posted a comment (i.e., if editCommentButton exists)
    if (editCommentButton != null) {
        const userCommentTextDiv = editCommentButton.parentNode.parentNode.querySelector('.comment-text');
        const userCommentReadMoreButton = editCommentButton.parentNode.parentNode.querySelector('.comment-read-more');

        // Display "Cancel" comment button in form (i.e., will be visible whenever form is visible)
        cancelCommentButton.style.display = 'block';

        // Set "Edit comment" button behaviour
        editCommentButton.addEventListener('click', function() {
            autofillCommentTextarea(userCommentTextDiv);
            userCommentTextDiv.style.display = 'none';
            userCommentReadMoreButton.style.display = 'none';
            commentForm.style.display = 'flex';
        });

        // Set "Cancel" button behaviour for commentForm
        cancelCommentButton.addEventListener('click', function(event) {
            event.preventDefault();
            commentForm.style.display = 'none';
            userCommentTextDiv.style.display = 'block';
            checkCommentOverflow(userCommentTextDiv, userCommentReadMoreButton);
        });

        // Set "Post" button behaviour for commentForm
        postCommentButton.addEventListener('click', function(event) {
            // No need to prevent default --> Button will submit the form & JavaScript will update page (no page reload)
            commentForm.style.display = 'none';
            userCommentTextDiv.style.display = 'block';
            updateCommentText(userCommentTextDiv);
            checkCommentOverflow(userCommentTextDiv, userCommentReadMoreButton);
        });
    } else {
        // Make commentForm visible
        commentForm.style.display = 'flex';

        // TODO: Set Post button behaviour --> just reload page to apply changes??
    }

    // Set "Read More" button behaviour (for comments)
    if (commentContainers != null) {
        commentContainers.forEach(commentContainer => {
            commentTextDiv = commentContainer.querySelector('.comment-text');
            readMoreCommentButton = commentContainer.querySelector('.comment-read-more');

            // For each comment --> Determine if "Read More" button should be displayed or not
            checkCommentOverflow(commentTextDiv, readMoreCommentButton);

            // For each comment --> Set behaviour of "Read More" button
            readMoreCommentButton.addEventListener('click', function () {
                isReadingMoreComment = isReadingMoreComment === true ? false : true;
                toggleCommentReadMore(commentTextDiv, readMoreCommentButton);
            });
        });
    }
});


// Triggers when viewport is resized --> in item_page.js
let resizeCommentTimeout;
window.addEventListener("resize", () => {
    clearTimeout(resizeCommentTimeout);
    resizeCommentTimeout = setTimeout(checkAllCommentsOverflow, 100); // Only run the function every 100ms minimum
});