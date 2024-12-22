const referrerInputFields = document.querySelectorAll(".referrer-input")

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function() {
    // Store referrer link in sessionStorage to keep the correct referrer even if the page is reloaded (e.g., form errors)
    // ONLY referrer links that aren't /signup-submit are valid
    if (document.URL != document.referrer) {
        sessionStorage.setItem("referrer-to-signup-login", document.referrer);
    }

    referrerInputFields.forEach(input => {
        input.value = sessionStorage.getItem("referrer-to-signup-login");
    });
});