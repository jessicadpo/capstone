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
const publicTagsFormField = document.getElementById('public-tags-form-field'); // Invisible to users
const privateTagsFormField = document.getElementById('private-tags-form-field'); // Invisible to users

function openModal() {
    addTagsOverlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // Disable scrolling on the main content
    addTagsModal.showModal();
}

function closeModal() {
    addTagsModal.close();
    document.body.style.overflow = ''; // Re-enable scrolling on the main content
    addTagsOverlay.classList.remove('active');
}

function isAlreadyAdded(newTagValue, isPublic) {
    let existingTags = isPublic ? publicTagsFormField.value : privateTagsFormField.value;
    existingTags = existingTags.toLocaleLowerCase(); // Makes check case-insensitive
    newTagValue = newTagValue.toLocaleLowerCase(); // Makes check case-insensitive
    if (existingTags.includes('\\n'+ newTagValue +'\\n')) {
        return true;
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
    }
}

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

    // Make the "Save" button submit the form & close the modal
    // Must use JavaScript because hidden forms aren't submittable otherwise
    saveTagsButton.addEventListener('click', function() {
        event.preventDefault();
        // Fill hidden form fields with all tags in modal
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

            if (this.classList.contains('pin-True')) {
                // Show the "Unpin" button inside form if the item has already been pinned by user
                // (Unpin button is hidden by default)
                unpinItemButton.style.display = "block";

                // Fill with user's tags for the current item (if there are any)
                const publicUserTagsForItem = this.nextElementSibling.querySelectorAll("span");
                const privateUserTagsForItem = this.nextElementSibling.nextElementSibling.querySelectorAll("span");

                publicUserTagsForItem.forEach(tag => {
                    addTag(tag.textContent, true);
                });
                privateUserTagsForItem.forEach(tag => {
                    addTag(tag.textContent, false)
                });
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
});