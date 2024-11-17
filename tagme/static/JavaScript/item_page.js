const column2MainContent = document.getElementById('column2-main-content');
const readMoreButton = document.getElementById('column2-read-more-button');

const topBar = document.getElementById('top-bar');
const mainContent = document.getElementById('main-content');
const footer = document.getElementById('footer');

const openSidebarButtons = document.querySelectorAll('.open-sidebar-button');
const closeSidebarButton = document.getElementById('close-sidebar-button');
const sidebar = document.getElementById('tag-sidebar');
const overlay = document.getElementById('overlay');

function checkOverflow(container) {
    return container.scrollHeight > container.clientHeight || container.scrollWidth > container.clientWidth;
}

// Set max-height of column2-main-content based on height of Read More button
function setMaxHeight() {
    const column2MainContent = document.getElementById('column2-main-content');
    const readMoreButton = document.getElementById('column2-read-more-button');
    const readMoreButtonHeight = readMoreButton.offsetHeight;
    const maxHeight = 510 - readMoreButtonHeight; // Set the max-height of div1 to 510px minus the sibling's height
    column2MainContent.style.maxHeight = maxHeight + 'px';
}

function openSidebar() {
    sidebar.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // Disable scrolling on the main content
    topBar.setAttribute('inert', ''); // Disable mouse & keyboard interaction
    mainContent.setAttribute('inert', '');
    footer.setAttribute('inert', '');
}

function closeSidebar() {
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
    document.body.style.overflow = ''; // Re-enable scrolling on the main content
    topBar.removeAttribute('inert');
    mainContent.removeAttribute('inert');
    footer.removeAttribute('inert');
}

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function () {

    // Determine if "Read More" button should be displayed or not
    if (checkOverflow(column2MainContent)) {
        readMoreButton.style.display = 'inline-block';
        column2MainContent.classList.add('reading-less'); // Only apply gradient if "Read More" button is shown in the first place
    } else {
        readMoreButton.style.display = 'none';
    }

    // Set behaviour of "Read More" button
    readMoreButton.addEventListener('click', function () {
        // Toggle gradient fade on column2-main-content
        column2MainContent.classList.toggle("reading-less");

        // Change height of entire item-info-section & column2-main-content divs
        const entireSection = this.parentNode.parentNode;
        column2MainContent.style.maxHeight = column2MainContent.style.maxHeight === 'none' ? setMaxHeight() : 'none';
        entireSection.style.maxHeight = entireSection.style.maxHeight === 'fit-content' ? '55vh' : 'fit-content';
        this.innerHTML = entireSection.style.maxHeight === 'fit-content' ? 'Read less <i class="fa fa-angle-up" aria-hidden="true"></i>' : 'Read more <i class="fa fa-angle-down" aria-hidden="true"></i>';
    });

    // Set href of "Back to Search Results" link
    const backLink = document.getElementById('back-link');
    backLink.href = document.referrer;

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Open/Close sidebar behaviour
    openSidebarButtons.forEach(openSidebarButton => {
        openSidebarButton.addEventListener('click', openSidebar);
    });
    closeSidebarButton.addEventListener('click', closeSidebar);
    overlay.addEventListener('click', closeSidebar);

});

window.onload = setMaxHeight;
