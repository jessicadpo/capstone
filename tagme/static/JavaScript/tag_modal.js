const pinItemButtons = document.querySelectorAll('.pin-item-button');
const addTagsOverlay = document.getElementById('add-tags-overlay');
const addTagsModal = document.getElementById('add-tags-modal');
const userTagsForm = document.getElementById('user-tags-form');
const closeXButton = document.getElementById('close-tag-modal-button');
const cancelButton = document.getElementById('cancel-tags-modal-button');
const saveTagsButton = document.getElementById('save-tags-button');
const unpinItemButton = document.getElementById('unpin-item-button');

const publicTagsContainer = document.getElementById('public-tags-list-container');
const privateTagsContainer = document.getElementById('private-tags-list-container');

const publicTagsInput = document.getElementById('public-tags-input');
const privateTagsInput = document.getElementById('private-tags-input');
const animatedTagScore = document.getElementById('animated-tag-score');
const totalPointsEarnedElement = document.getElementById('total-points-earned');
let initialTotalPointsEarned = parseInt(totalPointsEarnedElement.textContent.replace(" pts", "")); // Set on page load

const publicTagsFormField = document.getElementById('public-tags-form-field'); // Invisible to users
const privateTagsFormField = document.getElementById('private-tags-form-field'); // Invisible to users
const isPinnedFormField = document.getElementById('is-pinned-input'); // Invisible to users
const totalPointsEarnedFormField = document.getElementById('total-points-for-item-field'); // Invisible to users

function openModal() {
    setTagScore();
    setTotalPointsEarned();
    addTagsOverlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // Disable scrolling on the main content
    addTagsModal.showModal();
}

function closeModal() {
    animatedTagScore.classList.remove('play-animation'); // Prevent animation playing on modal re-open
    addTagsModal.close();
    document.body.style.overflow = ''; // Re-enable scrolling on the main content
    addTagsOverlay.classList.remove('active');
}

function isAlreadyAdded(newTagValue, isPublic) {
    newTagValue = newTagValue.toLocaleLowerCase(); // Makes check case-insensitive
    const existingTags = isPublic ? document.querySelectorAll('#public-tags-list-container .tag-value') : document.querySelectorAll('#private-tags-list-container .tag-value');
    // Can't use forEach (forEach cannot be interrupted by a return statement)
    for (let i = 0; i < existingTags.length; i++) {
        existingTag = existingTags[i].textContent.toLocaleLowerCase(); // Makes check case-insensitive
        if (existingTag.localeCompare(newTagValue) === 0) {
            return true;
        }
    }
    return false;
}

function addTag(newTagValue, isPublic) {
    // Do NOT add tag if input is empty or if tag has already been added by user
    if (newTagValue.trim() !== '' && !isAlreadyAdded(newTagValue, isPublic)) {
        const tagTemplate = document.getElementById('deletable-tag-template');
        const tagObject = tagTemplate.content.children[0].cloneNode(true);

        // Insert user input into tagObject's <a> element
        tagObject.querySelector('a').textContent = newTagValue;

        // Add tag to public/private-tags-list-container
        if (isPublic) {
            publicTagsContainer.appendChild(tagObject);
        } else {
            privateTagsContainer.appendChild(tagObject);
        }
    }
}

function removeTag(removeButton) {
    const tagDiv = removeButton.closest('.deletable-tag');
    if (tagDiv) {
        tagDiv.remove();
        setTotalPointsEarned();
    }
}

function setTotalPointsEarned() {
    // Total points earned should be based on number of tags currently added
    // but should NEVER decrement below initial minimum to prevent delete-then-re-add exploit
    // Initial minimum --> based on number of public tags already added by user --> get from server when page loads / refreshes
    const currentPublicTags = publicTagsContainer.querySelectorAll('.tag');
    let totalPointsEarned = 0;
    currentPublicTags.forEach((tag, index) => {
        if (index <= 10) {
            totalPointsEarned += (10 - index);
        }
    });
    totalPointsEarned = Math.max(initialTotalPointsEarned, totalPointsEarned);
    totalPointsEarnedElement.textContent = totalPointsEarned + " pts";
}

function setTagScore() {
    // Tag score should be based on total number of tags added (if there are any)
    const publicTagCount = publicTagsContainer.querySelectorAll('.tag').length;
    const totalPointsEarned = parseInt(totalPointsEarnedElement.textContent.replace(" pts", ""));
    // From 11 because score decrements faster than animation --> so decrement happens before animation
    // --> so need to decrement form 11 for "+10" to show correctly
    let newTagScore = 11 - publicTagCount;

    // Tag score should be shown if there are less than 10 public tags added
    // && if total points earned is under 55 pts (max possible for an item)
    // && if totalPointsEarned is greater than initialTotalPointsEarned
    if (publicTagCount > 10 || totalPointsEarned > 55 || totalPointsEarned <= initialTotalPointsEarned) {
        animatedTagScore.textContent = "";
    } else {  // If between 0 and 10 public tags added && totalPointsEarned <= 55 && newTagScore > initialTotalPointsEarned
        animatedTagScore.textContent = "+" + newTagScore;
    }
}

function playScoreAnimation() {
    // REMINDER: Private tags do not give points
    animatedTagScore.classList.remove('play-animation');
    void animatedTagScore.offsetWidth; // Force browser to re-render span before re-applying class
    animatedTagScore.classList.add('play-animation');
}

/*--------------------------------------------------------------------------------------------------------------------*/
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' || event.keyCode === 27) {
        closeModal();
    }
});

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function() {
    // Set close modal button behaviour
    closeXButton.addEventListener('click', closeModal);
    cancelButton.addEventListener('click', closeModal);

    // Set "Pin Item" button behaviour
    pinItemButtons.forEach(pinItemButton => {
        pinItemButton.addEventListener('click', function() {
            const pinningItem = this.closest('.result-item'); // i.e., closest common ancestor of "Pin Item" button and element containing item title
            const pinningItemTitle = pinningItem.querySelector('.item-title').textContent;
            const pinningItemId = this.value;

            // Reset form before opening it (always)
            const tagsInModal = document.querySelectorAll("#tagging-section .remove-tag-button");
            tagsInModal.forEach(tag => {
                removeTag(tag)
            });
            publicTagsInput.value = '';
            privateTagsInput.value = '';
            userTagsForm.reset();

            // Fill with user's tags for the current item (if there are any)
            // regardless of whether or not item is pinned
            const publicUserTagsForItem = this.nextElementSibling.querySelectorAll("span");
            const privateUserTagsForItem = this.nextElementSibling.nextElementSibling.querySelectorAll("span");
            publicUserTagsForItem.forEach(tag => {
                addTag(tag.textContent, true);
            });
            privateUserTagsForItem.forEach(tag => {
                addTag(tag.textContent, false)
            });

            if (this.classList.contains('pin-True')) {
                // Show the "Unpin" button inside form if the item has already been pinned by user
                // (Unpin button is hidden by default)
                unpinItemButton.style.display = "block";
            } else {
                // Hide the "Unpin" button inside form if item is NOT already pinned
                unpinItemButton.style.display = "none";
            }

            // Pre-fill <b> inside modal header (visible)
            document.getElementById('saving-item-title').textContent = pinningItemTitle;

            // Pre-fill item-id-input text field (invisible)
            document.getElementById('item-id-input').value = pinningItemId;

            // Open modal --> disables interaction outside of modal (unlike .show())
            openModal();
        });
    });

    // Set tag text input behaviour (Public tags)
    publicTagsInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();  // Prevent default behaviour
            const newPublicTag = publicTagsInput.value;
            addTag(newPublicTag, true); // Add tag HTML
            setTotalPointsEarned(); // MUST be done before setTagScore()
            // Setting tag score is faster than animation, so score is decremented before animation plays
            // If use set timeout of 1 second (animation duration) --> score doesn't decrement in time if user types really fast
            setTagScore();
            playScoreAnimation();
            publicTagsInput.value = ''; // Clear input field
        }
    });

    // Set tag text input behaviour (Private tags)
    privateTagsInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();  // Prevent default behaviour
            const newPrivateTag = privateTagsInput.value;
            addTag(newPrivateTag, false); // Add tag HTML
            privateTagsInput.value = ''; // Clear input field
        }
    });

    // Make the "Save" button submit the form & close the modal
    // Must use JavaScript because hidden forms aren't submittable otherwise
    saveTagsButton.addEventListener('click', function() {
        event.preventDefault();
        // Fill hidden form fields with all tags in modal
        isPinnedFormField.value = "True"; // MUST have first capital letter for compatibility with Python
        totalPointsEarnedFormField.value = parseInt(totalPointsEarnedElement.textContent.replace(" pts", ""));

        const publicTags = document.querySelectorAll('#public-tags-list-container .tag-value')
        const privateTags = document.querySelectorAll('#private-tags-list-container .tag-value')
        publicTags.forEach(tag => {
            publicTagsFormField.value += tag.textContent + '\\n';
        });
        privateTags.forEach(tag => {
            privateTagsFormField.value += tag.textContent + '\\n';
        });
        userTagsForm.submit();
        closeModal();
    });

    // Make the "Unpin" button submit the form (only care about isPinned) & close the modal
    // Must use JavaScript because hidden forms aren't submittable otherwise
    unpinItemButton.addEventListener('click', function() {
        event.preventDefault();
        isPinnedFormField.value = "False"; // MUST have first capital letter for compatibility with Python
        totalPointsEarnedFormField.value = parseInt(totalPointsEarnedElement.textContent.replace(" pts", ""));
        userTagsForm.submit();
        closeModal();
    });
});