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
});

/* TODO
const number_inputs = document.querySelectorAll('.page-number-input');

/*--------------------------------------------------------------------------------------------------------------------

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function () {
    number_inputs.forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, ''); // Allow only positive numbers
        });

        input.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevent form submission
                let pageNumber = parseInt(this.value);
                const maxPageNumber = parseInt(this.getAttribute('max'));

                // Ensure the page number is valid
                if (isNaN(pageNumber)) {
                    alert('Please enter a valid page number.');
                    return;
                } else if (pageNumber < 1) {
                    pageNumber = 1;
                } else if (pageNumber > maxPageNumber) {
                    pageNumber = maxPageNumber
                }

                const currentURL = window.location.href; // Get the current URL in full
                const url_sections = currentURL.split('/');
                if (url_sections.length >= 5) {  // Update the page number in the URL
                    url_sections[4] = pageNumber;
                }
                const newURL = url_sections.join('/'); // Construct the new URL

                window.location.assign(newURL); // Navigate to the new URL (& keep the current page in browser history)
            }
        });
    });
});
*/