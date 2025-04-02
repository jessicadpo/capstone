const prevPageButtons = document.querySelectorAll('.prev-page-button');
const nextPageButtons = document.querySelectorAll('.next-page-button');

// If both pagination_top and pagination_bottom used in the same page, page will have duplicate fields
// for storing this info, thus why we're using classes/querySelectorAll instead of ids/getElementById
var page_url = null;
var currentPageNumber = null;
var lastPageNumber = null;

if (document.querySelectorAll('.page-url').length > 0) {
    page_url = document.querySelectorAll('.page-url')[0].value; // FIXME: Error on item pages? ([0] is undefined)
    currentPageNumber = parseInt(document.querySelectorAll('.current-page-number')[0].value);
    lastPageNumber = parseInt(document.querySelectorAll('.last-page-number')[0].value);
}

function setResponsiveBottomPaginationBehaviour() {
    // Need to query the document because elements reset when change pages
    const paginationFooter = document.getElementById('pagination-footer');
    const bottomPaginationRangeText = document.querySelector('#pagination-footer > p');
    const bottomPaginationControls = document.getElementById('bottom-page-controls');

    // Do not continue if page doesn't have a pagination-footer
    if (paginationFooter === null) {
        return;
    }

    // Remove go-to-page-buttons & replace with number input only if bottom-page-controls would overflow from screen
    const goToPageButtons = bottomPaginationControls.querySelectorAll(".go-to-page-button");
    const nextPageNumberForm = document.querySelector('.next-page-input-form');
    const prevPageNumberForm = document.querySelector('.prev-page-input-form');
    const nextInputIsVisible = nextPageNumberForm.classList.contains("invisible") ? false : true;
    const prevInputIsVisible = prevPageNumberForm.classList.contains("invisible") ? false : true;

    if (bottomPaginationControls.scrollWidth > bottomPaginationControls.clientWidth) {
        goToPageButtons.forEach(goToPageButton => {
            goToPageButton.style.display = "none";
        });

        const currentPageNumber = document.querySelector('.current-page-number').value;

        prevPageNumberForm.classList.add("invisible");
        nextPageNumberForm.classList.remove("invisible");
        nextPageNumberForm.querySelector('input').placeholder = currentPageNumber;
    } else {
        const clone = bottomPaginationControls.cloneNode(true);
        clone.style.position = "absolute";
        clone.querySelectorAll("*").forEach(child => {
            child.style.display = "block";
        })

        document.body.appendChild(clone);
        const minWidth = clone.scrollWidth;
        document.body.removeChild(clone);

        if (paginationFooter.scrollWidth > minWidth) {
            goToPageButtons.forEach(goToPageButton => {
                goToPageButton.style.display = "block";
            });

            nextPageNumberForm.querySelector('input').placeholder = '';
            if (nextInputIsVisible) {
                nextPageNumberForm.classList.remove("invisible");
            }
            if (prevInputIsVisible) {
                prevPageNumberForm.classList.remove("invisible");
            }
        }
    }

    // Move the pagination range text above controls if overflow
    if (bottomPaginationRangeText.scrollWidth > bottomPaginationRangeText.clientWidth) {
        paginationFooter.classList.add('two-line');
    } else {
        const columnWidths = getComputedStyle(paginationFooter).gridTemplateColumns.split(' ');
        if (bottomPaginationRangeText.scrollWidth < parseFloat(columnWidths[0])) {
            paginationFooter.classList.remove('two-line');
        }
    }
}

function fetchPage(pageNumberToFetch) {
    // Send AJAX request to get next page of comments (without reloading the page)
    const currentGetParams = new URLSearchParams(window.location.search);
    currentGetParams.set("page", pageNumberToFetch);
    paginationQuery = "?" + currentGetParams.toString();

    fetch(page_url + paginationQuery, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update the content with the paginated content's HTML
        document.querySelectorAll('.paginated-content')[0].outerHTML = data.html;
        currentPageNumber = pageNumberToFetch;
        setPaginationFormBehaviour();

        if (data.url_name === 'item_page') {
            setCommentsBehaviour(); // defined in user_comment.js
        } else if (data.url_name === 'pinned_items') {
            setPinItemButtonBehaviour(); // defined in tag_modal.js
            setResponsiveBottomPaginationBehaviour();
            document.getElementById('open-filter-menu-button').addEventListener("click", openFilterMenu);
        } else if (data.url_name === 'search_results') {
            setPinItemButtonBehaviour(); // defined in tag_modal.js
            setResponsiveBottomPaginationBehaviour();
            document.getElementById('open-search-sidebar-button').addEventListener("click", openSearchSidebar);
        }

        // Update URL
        const newURL = page_url + paginationQuery;
        history.pushState({ path: newURL}, "", newURL);
    });
}

function goToPreviousPage() {
    /* Decrease page number by 1, unless user is already on first page */
    if (currentPageNumber > 1) {
      var pageNumberToFetch = currentPageNumber - 1;
      fetchPage(pageNumberToFetch);
    }
}

function goToNextPage() {
    /* Increase page number by 1, unless user is already on last page */
    if (currentPageNumber < lastPageNumber) {
      var pageNumberToFetch = currentPageNumber + 1;
      fetchPage(pageNumberToFetch);
    }
}

function setPaginationFormBehaviour() {
    const paginationForms = document.querySelectorAll('.pagination-form');
    paginationForms.forEach(paginationForm => {
        paginationForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const goToPageNumber = paginationForm.querySelector('input').value;
            fetchPage(goToPageNumber);
        });
    });
}

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function () {
    // Prev & Next button behaviour set in HTML via onclick attribute
    setPaginationFormBehaviour();
});

// Triggers after window has finished loading (i.e., all CSS and JavaScript has already been applied)
window.addEventListener("load", setResponsiveBottomPaginationBehaviour);

// Triggers when window is resized
window.addEventListener("resize", setResponsiveBottomPaginationBehaviour);
