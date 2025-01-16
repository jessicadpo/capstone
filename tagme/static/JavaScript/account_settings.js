const editUsernameButton = document.getElementById('edit-username-button');
const editEmailButton = document.getElementById('edit-email-button');
const editPasswordButton = document.getElementById('edit-password-button');

const usernameForm = document.getElementById('username-change-form');
const emailForm = document.getElementById('email-change-form');
const passwordForm = document.getElementById('password-change-form');
const allForms = document.querySelectorAll('#main-content form:not(#delete-account-form)');

const deleteAccountForm = document.getElementById('delete-account-form');

function showForm(formToShow) {
    if (formToShow === null) {
        return;
    }
    
    if (formToShow.classList.contains("invisible")) {
        formToShow.classList.remove("invisible");
    }

    // Focus on the first non-hidden, non-disabled, focusable input field in the now visible form
    const inputFields = Array.from(formToShow.querySelectorAll('input'));
    for (const input of inputFields) {
        if (input.type !== 'hidden' && !input.disabled && input.tabIndex !== -1) {
            input.focus();
            break;
        }
    }

    // If another form is already open/visible --> Clear & hide it
    allForms.forEach(form => {
        if (form !== formToShow) {
            hideForm(form);
        }
    });
}

function hideForm(formToHide) {
    if (formToHide === null) {
        return;
    }

    if (!formToHide.classList.contains("invisible")) {
        formToHide.classList.add("invisible");
    }

    // Clear all non-submit input fields in formToHide
    inputFields = formToHide.querySelectorAll('input');
    inputFields.forEach(input => {
        if (input.type !== 'submit' && input.type !== 'hidden') {
            input.value = "";
        }
    });
}

function toggleForm(relevantForm) {
    if (relevantForm.classList.contains("invisible")) {
        showForm(relevantForm);
    } else {
        hideForm(relevantForm);
    }
}

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function() {
    // Set Edit button behaviour
    editUsernameButton.addEventListener('click', function() {
        toggleForm(usernameForm);
    });
    editEmailButton.addEventListener('click', function() {
        toggleForm(emailForm);
    });
    editPasswordButton.addEventListener('click', function() {
        toggleForm(passwordForm);
    });

    // Set Delete Account form submission behaviour (confirm popup)
    deleteAccountForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const confirmMessage = "Are you sure you want to delete your TagMe account?\n\n" +
        "All data related to your account (pins, tags, rewards, etc.) will be permanently deleted.";

        if (confirm(confirmMessage)) {
            deleteAccountForm.submit();
        }
    });
});
