const currentPageHeader = document.getElementById('current-page-header');
const openUserSidenavButton = document.getElementById('open-user-sidenav-button');
const sidenavLinksBlock = document.getElementById('user-sidenav-links');

function getCurrentPageLink() {
    const pageName = document.querySelector('meta[name="page-name"]').content;
    var currentPageLink;

    switch(pageName) {
        case "user_profile":
            return document.getElementById('my-profile-sidenav-link');
        case "pinned_items":
            return document.getElementById('pinned-items-sidenav-link');
        case "account_settings":
            return document.getElementById('account-settings-sidenav-link');
        default:
            return null;
    }

    currentPageLink.classList.add('active');
}

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function() {
    currentPageLink = getCurrentPageLink();

    // Add "active" class to currentPageLink (applies ".active" CSS ONLY for viewports with landscape orientations)
    currentPageLink.classList.add('active');

    // Insert contents of currentPageLink into currentPageHeader
    // REMINDER: currentPageHeader is only visible for viewports with small widths (e.g., portrait orientation, mobile, etc.)
    currentPageHeader.insertAdjacentHTML('afterbegin', currentPageLink.innerHTML);

    // Set openUserSidenavButton behaviour (accordion)
    openUserSidenavButton.addEventListener("click", function() {
        if (sidenavLinksBlock.style.maxHeight) {
            sidenavLinksBlock.style.maxHeight = null;
        } else {
            sidenavLinksBlock.style.maxHeight = sidenavLinksBlock.scrollHeight + "px";
        }
    });
});
