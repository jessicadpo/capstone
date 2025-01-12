const prevPageButtons = document.querySelectorAll('.prev-page-button');
const nextPageButtons = document.querySelectorAll('.next-page-button');

// If both pagination_top and pagination_top used in the same page, page will have duplicate fields
// for storing this info, thus why we're using classes/querySelectorAll instead of ids/getElementById
const page_url = document.querySelectorAll('.page-url')[0].value;
var currentPageNumber = parseInt(document.querySelectorAll('.current-page-number')[0].value);
var lastPageNumber = parseInt(document.querySelectorAll('.last-page-number')[0].value);


function fetchPage(pageNumberToFetch) {
    // Send AJAX request to get next page of comments (without reloading the page)
    fetch(page_url + "?page=" + pageNumberToFetch, {
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
        } else if (data.url_name === 'pinned_items') { // TODO: Also call if search_results page?
            setPinItemButtonBehaviour(); // defined in tag_modal.js
        }
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
