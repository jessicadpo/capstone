const reportTagOverlay = document.getElementById('report-tag-overlay');
const reportTagModal = document.getElementById('report-tag-dialog');

const reportTagForm = document.getElementById('report-tag-form');
const reportedTagComponent = document.querySelector('#report-tag-dialog .tag-content span');
const otherCheckbox = document.getElementById('id_is_other');
const otherTextInput = document.getElementById('other-input');
const otherRequiredError = document.getElementById('other-required-error');
const submitReportButton = document.getElementById('submit-tag-report-button');


function setResponsiveReportModalBehaviour() {
    // Position report-dialog horizontally depending on width of visible overlay
    const visibleOverlayWidth = window.innerWidth - parseFloat(getComputedStyle(tagSidebar).width);
    if (visibleOverlayWidth > 520) { /* 500px + 10px horizontal gap between modal & sidebar */
        const xPos = visibleOverlayWidth * 0.5;
        reportTagModal.style.left = xPos + "px";
        reportTagOverlay.classList.remove('active');
    } else {
        reportTagModal.style.left = "50%";
        if (reportTagModal.open) {
            reportTagOverlay.classList.add('active');
            document.documentElement.style.overflowY = "hidden"; // Disable scrolling on the main content
        }
    }

    // Responsive layout if modal-footer has overflow
    preventResponsiveGridOverflow(reportTagModal.querySelector('.modal-footer')); // defined in global.js
}

function openReportModal(reportButton) {
    const reportedTagValue = reportButton.getAttribute('data-tag');
    reportedTagComponent.textContent = reportedTagValue; // Pre-fill <span> inside tag button (visible)
    document.getElementById('reported-tag-input').value = reportedTagValue; // Pre-fill reported-tag-input text field (invisible)

    reportTagModal.show();
    setResponsiveReportModalBehaviour(); // Activates overlay & disables scrolling (depending on dialog position)

    requestAnimationFrame(() => {
        reportTagModal.classList.add('visible');  // Fade-in the modal
    });
}

function closeReportModal() {
    reportTagModal.classList.remove('visible'); // Ensures next re-open of modal will also fade in
    reportTagModal.close();
    reportTagOverlay.classList.remove('active');
}

window.addEventListener("resize", setResponsiveReportModalBehaviour);

document.addEventListener('keydown', function(event) {
    if ((event.key === 'Escape' || event.keyCode === 27) && reportTagModal.open) {
        reportTagModal.setAttribute("data-just-closed", "true"); // To prevent both modal AND sidebar closing on ESC keypress
        closeReportModal();
    }
});

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function () {
    // Disable link (keyboard navigation) of reportedTagElement
    reportedTagComponent.setAttribute('tabindex', '-1');
    reportedTagComponent.setAttribute('aria-disabled', 'true');

    // Set close modal button behaviour
    document.getElementById('close-report-modal-button').addEventListener('click', closeReportModal);
    document.getElementById('cancel-tag-report-button').addEventListener('click', closeReportModal);

    // Client-side check that form is valid
    // (Server-side check would reload the page and make it look like there were no form errors)
    submitReportButton.addEventListener("click", (event) => {
        event.preventDefault();

        checkboxes = reportTagForm.querySelectorAll('input[type="checkbox"');
        var reasonGiven = Array.from(checkboxes).some(checkbox => checkbox.checked);

        if (!reasonGiven) {
            alert("At least one reason must be given.")
        }
        else if (otherCheckbox.checked && (otherTextInput.value).trim().length === 0) {
            otherTextInput.style.borderColor = "#B52801";
            otherRequiredError.style.display = "block";
        } else {
            reportTagForm.submit();
        }
    });
});
