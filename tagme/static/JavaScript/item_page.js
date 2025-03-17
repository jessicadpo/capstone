const backLink = document.getElementById('back-link');

const entireItemSection = document.getElementById('item-info-section');

const tagsContainer = document.querySelector('#tags-column #tags-container');
const columnTags = document.querySelectorAll('#tags-column .tag');

const openTagSidebarButtons = document.querySelectorAll('.open-sidebar-button');
const closeTagSidebarButton = document.getElementById('close-sidebar-button');
const tagSidebar = document.getElementById('tag-sidebar');

const reportButtons = document.querySelectorAll('.report-button');

function setBackLink() {
    // Store link to search results page in sessionStorage
    // ONLY store links that include "/search/#/?search_type=..." in the URL
    const search_results_URL_pattern = /\/search\/\d+\/\?search_type=/;

    if (search_results_URL_pattern.test(document.referrer)) {
        sessionStorage.setItem("search_results_referrer", document.referrer);
    }
    // If document.referrer is NOT a search_results page, NOT signup-login page, NOR the item page itself (i.e., due to page reload)
    // --> Remove "search_results_referrer" from sessionStorage
    else if (document.referrer != "" && (new URL(document.referrer)).pathname != '/signup-login' && document.URL != document.referrer) {
        sessionStorage.removeItem("search_results_referrer");
    }

    // Show & set href link of "Back to Search Results link only if there's a "search_results_referrer" in sessionStorage
    if (sessionStorage.getItem("search_results_referrer")) {
        backLink.setAttribute("href", sessionStorage.getItem("search_results_referrer"));
        backLink.classList.add("valid");
    } else {
        backLink.classList.remove("valid");
    }
}

function openTagSidebar() {
    openSidebar(tagSidebar, true); // see global.js
}

function closeTagSidebar() {
    closeReportModal(); // see report_modal.js
    closeSidebar(tagSidebar, true); // see global.js
}

function hidePartialOverflowTags() {
    // Hide tags in #tags-column if they overflow, even if just partially
    columnTags.forEach(tag => {
        if (tag.getBoundingClientRect().bottom >= tagsContainer.getBoundingClientRect().bottom) {
            tag.style.visibility = "hidden";
        } else {
            tag.style.visibility = ""; /* Reset to whatever it is in CSS */
        }
    });
}

/*--------------------------------------------------------------------------------------------------------------------*/
document.addEventListener('keydown', function(event) {
    // Only close sidebar with Escape key if reportTagModal already closed
    // reportTagModal defined in tag_modal.js
    if ((event.key === 'Escape' || event.keyCode === 27) && tagSidebar.classList.contains("open")) {
        if (reportTagModal.dataset.justClosed == "true") {
            reportTagModal.setAttribute("data-just-closed", "false");
        } else {
            closeTagSidebar();
        }
    }
});

window.addEventListener("resize", hidePartialOverflowTags);

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function () {
    // Determine if "Back to Search Results" link should be displayed + (if yes) set its link
    setBackLink();

    hidePartialOverflowTags();

    // Open/Close sidebar behaviour
    openTagSidebarButtons.forEach(openTagSidebarButton => {
        openTagSidebarButton.addEventListener('click', openTagSidebar);
    });
    sidebarOverlay.addEventListener('click', closeTagSidebar); //sidebarOverlay defined in global.js
    closeTagSidebarButton.addEventListener('click', closeTagSidebar);

    // Set report button behaviour
    let lastButton = null; // keep track of the last Report button that was clicked
    reportButtons.forEach(reportButton => {
        reportButton.addEventListener('click', function() {
            // Reset form if open for a different tag
            if (reportButton != lastButton) {
                document.getElementById('report-tag-form').reset();
                lastButton = reportButton;
            }

            openReportModal(reportButton); // defined in report_modal.js
        });
    });
});
