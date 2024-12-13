const referrerInputFields = document.querySelectorAll(".referrer-input")

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function() {
    referrerInputFields.forEach(input => {
        input.value = document.referrer;
    });
});