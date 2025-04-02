const searchSidebar = document.getElementById('search-sidebar');
const openSearchSidebarButton = document.getElementById('open-search-sidebar-button');
const closeSearchSidebarButton = document.getElementById('close-search-sidebar-button');

function openSearchSidebar() {
    openSidebar(searchSidebar, false); // defined in global.js
}


function closeSearchSidebar() {
    closeSidebar(searchSidebar, false); // see global.js
}

/*--------------------------------------------------------------------------------------------------------------------*/
document.addEventListener('keydown', function(event) {
    if ((event.key === 'Escape' || event.keyCode === 27) && searchSidebar.classList.contains("open")) {
        closeSearchSidebar();
    }
});

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function () {
    openSearchSidebarButton.addEventListener("click", openSearchSidebar);
    sidebarOverlay.addEventListener("click", closeSearchSidebar); // sidebarOverlay defined in global.js
    closeSearchSidebarButton.addEventListener("click", closeSearchSidebar);

    // Set the value in the search dropdown menu to the most recent type of search performed
    const currentGetParams = new URLSearchParams(window.location.search);
    const searchType = currentGetParams.get("search_type");
    searchDropdownButtonSpan.textContent = searchType; // searchDropdownButtonSpan initialized in global.js
    searchFormSelect.value = searchType; // searchFormSelect initialized in global.js
});
