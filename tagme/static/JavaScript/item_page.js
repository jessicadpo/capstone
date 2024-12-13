const backLink = document.getElementById('back-link');

const entireItemSection = document.getElementById('item-info-section');
const column2MainContent = document.getElementById('column2-main-content');
const readMoreButton = document.getElementById('column2-read-more-button');

const tagsContainer = document.getElementById('tags-container');
const column3Tags = document.querySelectorAll('.column3 .tag');

const topBar = document.getElementById('top-bar');
const mainContent = document.getElementById('main-content');
const footer = document.getElementById('footer');

const openSidebarButtons = document.querySelectorAll('.open-sidebar-button');
const closeSidebarButton = document.getElementById('close-sidebar-button');
const reportOverlay = document.getElementById('report-tag-overlay');
const sidebar = document.getElementById('tag-sidebar');

const reportButtons = document.querySelectorAll('.report-button');
const reportTagDialog = document.getElementById('report-tag-dialog');
const reportedTagComponent = document.querySelector('#report-tag-dialog .tag-content a');

let isReadingMore = false;

function toggleReadMore() {
    if (isReadingMore) {
        // If user is reading more --> button should say "Read Less"
        column2MainContent.classList.remove('reading-less');
        column2MainContent.style.maxHeight = 'none';
        entireItemSection.style.maxHeight = 'fit-content';
        readMoreButton.innerHTML = 'Read less <i class="fa fa-angle-up" aria-hidden="true"></i>';
    }
    else {
        // If user is reading less (i.e., button should say "Read More")
        column2MainContent.classList.add('reading-less'); // Only apply gradient if button says "Read More"
        column2MainContent.style.maxHeight = setMaxHeight();
        entireItemSection.style.maxHeight = '55vh';
        readMoreButton.innerHTML = 'Read more <i class="fa fa-angle-down" aria-hidden="true"></i>';
    }
}

function setMaxHeight() {
    // Set max-height of column2-main-content based on height of Read More button
    const readMoreButtonHeight = readMoreButton.offsetHeight;
    const maxHeight = 510 - readMoreButtonHeight; // Set the max-height of div1 to 510px minus the sibling's height
    column2MainContent.style.maxHeight = maxHeight + 'px';
}

function checkColumn2Overflow() {
    // If column 2 is overflowing on page load or resize --> show "Read More" button
    let thresholdHeight = Math.ceil(parseFloat(window.getComputedStyle(entireItemSection).minHeight));

    if (column2MainContent.scrollHeight > thresholdHeight) { // Need to show "Read More" button
        readMoreButton.style.display = 'inline-block';
        isReadingMore = false;
        toggleReadMore();
    } else { // If column 2 is overflowing --> don't need to show "Read More" button
        readMoreButton.style.display = 'none';
        isReadingMore = true; // Is technically "reading more" because everything is visible (no overflow)
        toggleReadMore();
    }
}

function checkTagsOverflow() {
    const containerRect = tagsContainer.getBoundingClientRect();
    column3Tags.forEach((tag, index) => {
        if (index === 0) {
            return; // Do not hide first tag even if it overflows
        }
        const tagRect = tag.getBoundingClientRect();
        if (tagRect.bottom > containerRect.bottom) {
            tag.style.display = "none";
        } else {
            tag.style.display = "flex";
        }
    });
}

function setBackLink() {
    // Store link to search results page in sessionStorage
    // ONLY store links that include "/search/#/?search_type=..." in the URL
    const search_results_URL_pattern = /\/search\/\d+\/\?search_type=/;
    if (search_results_URL_pattern.test(document.referrer)) {
        sessionStorage.setItem("search_results_referrer", document.referrer);
    }
    // If document.referrer is NOT a search_results page, NOT signup-login page, NOR the item page itself (i.e., due to page reload)
    // --> Remove "search_results_referrer" from sessionStorage
    else if ((new URL(document.referrer)).pathname != '/signup-login' && document.URL != document.referrer) {
        sessionStorage.removeItem("search_results_referrer");
    }

    // Show & set href link of "Back to Search Results link only if there's a "search_results_referrer" in sessionStorage
    if (sessionStorage.getItem("search_results_referrer")) {
        backLink.setAttribute("href", sessionStorage.getItem("search_results_referrer"))
        backLink.style.display = "flex";
    } else {
        backLink.style.display = "none";
    }
}

function openSidebar() {
    sidebar.classList.add('active');
    reportOverlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // Disable scrolling on the main content
    topBar.setAttribute('inert', ''); // Disable mouse & keyboard interaction
    mainContent.setAttribute('inert', '');
    footer.setAttribute('inert', '');
}

function closeSidebar() {
    sidebar.classList.remove('active');
    reportOverlay.classList.remove('active');
    reportTagDialog.close();
    document.body.style.overflow = ''; // Re-enable scrolling on the main content
    topBar.removeAttribute('inert');
    mainContent.removeAttribute('inert');
    footer.removeAttribute('inert');
}

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function () {
    // Determine if "Back to Search Results" link should be displayed + (if yes) set its link
    setBackLink();

    // Determine if "Read More" button should be displayed or not
    checkColumn2Overflow();
    checkTagsOverflow();

    // Set behaviour of "Read More" button
    readMoreButton.addEventListener('click', function () {
        isReadingMore = isReadingMore === true ? false : true;
        toggleReadMore();
    });

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Disable link (keyboard navigation) of reportedTagElement
    reportedTagComponent.setAttribute('tabindex', '-1');
    reportedTagComponent.setAttribute('aria-disabled', 'true');

    // Open/Close sidebar behaviour
    openSidebarButtons.forEach(openSidebarButton => {
        openSidebarButton.addEventListener('click', openSidebar);
    });
    closeSidebarButton.addEventListener('click', closeSidebar);
    reportOverlay.addEventListener('click', closeSidebar);

    // Set report button behaviour
    let lastButton = null; // keep track of the last Report button that was clicked
    reportButtons.forEach(reportButton => {
        reportButton.addEventListener('click', function() {
            const tagEntry = this.closest('.tag-entry');
            const reportedTagValue = tagEntry.querySelector('.tag-content a').textContent;

            // Reset form if open for a different tag
            if (reportButton != lastButton) {
                document.getElementById('report-tag-form').reset();
                lastButton = reportButton;
            }

            // Pre-fill <span> inside tag button (visible)
            reportedTagComponent.textContent = reportedTagValue;

            // Pre-fill reported-tag-input text field (invisible)
            document.getElementById('reported-tag-input').value = reportedTagValue;

            // Open dialog
            reportTagDialog.show();
        });
    });
});

// Triggers when viewport is resized
let resizeTimeout;
window.addEventListener("resize", () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(checkColumn2Overflow, 100); // Only run the function every 100ms minimum
});
