const reportTagForm = document.getElementById('report-tag-form');
const otherCheckbox = document.getElementById('id_is_other');
const otherTextInput = document.getElementById('other-input');
const otherRequiredError = document.getElementById('other-required-error');
const submitReportButton = document.getElementById('submit-tag-report-button');

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function () {
    // Client-side check that form is valid
    // (Server-side check would reload the page and make it look like there were no form errors)
    submitReportButton.addEventListener("click", (event) => {
        event.preventDefault();
        if (otherCheckbox.checked && (otherTextInput.value).trim().length === 0) {
            otherTextInput.style.borderColor = "#B52801";
            otherRequiredError.style.display = "block";
        } else {
            reportTagForm.submit();
        }
    });
});
