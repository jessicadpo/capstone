const topBar = document.getElementById('top-bar');
const searchBar = document.querySelector('#top-bar #search-bar');  // Only applies to the search bar in top bar (not homepage search bar)
const closeSearchBarButton = document.getElementById('close-search-bar-button');
const openSearchBarButton = document.getElementById('open-search-bar-button');

const tooltips = document.querySelectorAll(".tooltip");
const dropdowns = document.querySelectorAll('.dropdown');
const footer = document.getElementById('footer');


const searchDropdownButtonSpan = document.getElementById("search-dropdown-button-text");
const searchDropdownItems = document.querySelectorAll(".search-dropdown-item");
const searchFormSelect = document.getElementById('search-type-select');


const triStateCheckboxContainer = document.querySelectorAll('.tri-state-checkbox-container');
const checkboxStates = ['no', 'yes', 'null'];

/*--------------------------------------------------------------------------------------------------------------------*/
/* RESPONSIVE STYLING */
function preventDropdownPageOverflow(dropdownOptions) {
    dropdownOptions.style.height = "auto"; // Reset to default so always occupy max available height

    // Prevent dropdown menus from overflowing beyond page footer
    if (dropdownOptions.getBoundingClientRect().bottom > footer.getBoundingClientRect().bottom) {
        const height = footer.getBoundingClientRect().bottom - dropdownOptions.getBoundingClientRect().top;
        dropdownOptions.style.height = String(height) + "px";
    }
}

function openSearchBar() {
    if (window.innerWidth <= 500) {
        searchBar.style.width = "100%"; // Make sure width is at 100%
        topBar.style.overflow = "hidden";
        requestAnimationFrame(() => { // Ensure height change is only rendered AFTER display grid has completed execution
            requestAnimationFrame(() => {
                topBar.style.height = String(100 + searchBar.clientHeight) + "px";
                setTimeout(() => {
                    topBar.style.overflow = "visible";
                }, 200); // 200ms == 0.2s (same time as height transition set in global.css)
            });
        });
    } else {
        searchBar.style.width = "0px"; // Make sure width is at 0px
        topBar.style.overflow = "visible";
        topBar.style.height = "fit-content";
        requestAnimationFrame(() => { // Ensure width change is only rendered AFTER display flex has completed execution
            requestAnimationFrame(() => {
                searchBar.style.width = "100%";
            });
        });
    }
}

function closeSearchBar() {
    topBar.style.height = "100px";

    if (window.innerWidth < 750 && window.innerWidth > 500) {
        searchBar.style.width = "0px";
    } else if (window.innerWidth <= 500) {
        topBar.style.overflow = "hidden";
    }

    setTimeout(() => {
      searchBar.classList.remove("open");
      searchBar.style.display = null;
      searchBar.style.width = null;
      topBar.style.overflow = "visible";
    }, 200); // 200ms == 0.2s (same time as width transition set in global.css)
}

function toggleSearchBar() {
    if (searchBar.classList.contains("open")) {
        searchBar.classList.remove("open");
        closeSearchBar();
    } else {
        searchBar.classList.add("open");
        openSearchBar();
    }
}

// TOOLTIPS - PREVENT OVERFLOWING FROM VIEWPORT WIDTH-WISE
function preventTooltipViewportOverflow() {
    const viewportWidth = window.innerWidth;
    if (tooltips != null && tooltips.length > 0) {
        tooltips.forEach(tooltip => {
            const tooltipBubble = tooltip.querySelector('.tooltip-bubble');
            const bubbleContent = tooltip.querySelector('.bubble-content');
            const bubbleTailOutline = tooltip.querySelector('.bubble-tail-outline');

            const tooltipMaxPossibleWidth = bubbleContent.getBoundingClientRect().width + Math.max(bubbleTailOutline.getBoundingClientRect().width, bubbleTailOutline.getBoundingClientRect().height);
            const tooltipIconRightCoordinate = tooltip.querySelector('i').getBoundingClientRect().right;
            const tooltipIconLeftCoordinate = tooltip.querySelector('i').getBoundingClientRect().left;
            /* NOTE: Calling .getBoundingClientRect() every time due to weird JavaScript issues
            * (i.e., getBoundingClientRect().right value is not the same if stored in a const vs. if called) */

            // Switch to bubble-on-top if bubbleContent overflows from viewport
            if (tooltipBubble.classList.contains("bubble-on-right")
            && bubbleContent.getBoundingClientRect().right >= viewportWidth) {
                tooltipBubble.classList.remove("bubble-on-right");
                tooltipBubble.classList.add("bubble-on-top");
                tooltipBubble.classList.add("originally-bubble-on-right");
            }
            else if (tooltipBubble.classList.contains("bubble-on-left")
            && bubbleContent.getBoundingClientRect().left < 0) {
                tooltipBubble.classList.remove("bubble-on-left");
                tooltipBubble.classList.add("bubble-on-top");
                tooltipBubble.classList.add("originally-bubble-on-left");
            }
            // Switch back to bubble-on-right/bubble-on-left if resize back to ok width
            else if (tooltipBubble.classList.contains("originally-bubble-on-right")
            && tooltipIconRightCoordinate + 6 + tooltipMaxPossibleWidth < viewportWidth) {
                tooltipBubble.classList.remove("bubble-on-top");
                tooltipBubble.classList.remove("bubble-on-bottom");
                tooltipBubble.classList.remove("originally-bubble-on-right");
                tooltipBubble.classList.add("bubble-on-right");
                bubbleContent.style.removeProperty('left');
                return;
            }
            else if (tooltipBubble.classList.contains("originally-bubble-on-left")
            && tooltipIconLeftCoordinate - 6 - tooltipMaxPossibleWidth >= 0) {
                tooltipBubble.classList.remove("bubble-on-top");
                tooltipBubble.classList.remove("bubble-on-bottom");
                tooltipBubble.classList.remove("originally-bubble-on-left");
                tooltipBubble.classList.add("bubble-on-left");
                bubbleContent.style.removeProperty('left');
                return;
            }

            // newLeftCoordinate == x coordinate of bubble-content's left edge on screen IF CORRECT FOR OVERFLOW
            // newRightCoordinate == x coordinate of bubble-content's right edge on screen IF CORRECT FOR OVERFLOW
            const leftOverflow = 0 - bubbleContent.getBoundingClientRect().left;
            const rightOverflow = bubbleContent.getBoundingClientRect().right - viewportWidth;
            var newLeftCoordinate = bubbleContent.getBoundingClientRect().left + leftOverflow;
            var newRightCoordinate = bubbleContent.getBoundingClientRect().right - (rightOverflow - 1); // 1px margin of error

            const currentLeftStyle = isNaN(parseInt(bubbleContent.style.left)) ? 0 : parseInt(bubbleContent.style.left);

            /* NOTE:
            * Decreasing bubbleContent.style.left --> shifts towards the left.
            * Increasing bubbleContent.style-left --> shifts towards the right. */

            // Adjust position to prevent overflow on left side of viewport
            // The "- 10" ensures a minimum space of 10px between edge of bubbleContent and edge of bubbleTailOutline
            if (leftOverflow >= 0 && newLeftCoordinate < bubbleTailOutline.getBoundingClientRect().left - 10) {
                bubbleContent.style.left = String(currentLeftStyle + leftOverflow) + "px";
            }

            // Adjust position to prevent overflow on right side of viewport
            // The "+ 10" ensures a minimum space of 10px between edge of bubbleContent and edge of bubbleTailOutline
            if (rightOverflow >= 0 && newRightCoordinate > bubbleTailOutline.getBoundingClientRect().right + 10) {
                bubbleContent.style.left = String(currentLeftStyle - rightOverflow - 1) + "px";
            }

            // Adjust position as close to original position as possible if no longer overflowing
            // FIXME: (??) Not working if spamming resize too fast
            const originalCenterCoordinate = bubbleTailOutline.getBoundingClientRect().x + (bubbleTailOutline.getBoundingClientRect().width / 2);
            const maxLeftCoordinate = originalCenterCoordinate - (bubbleContent.getBoundingClientRect().width / 2);
            const minRightCoordinate = originalCenterCoordinate + (bubbleContent.getBoundingClientRect().width / 2);

            var currentCenterCoordinate = bubbleContent.getBoundingClientRect().x + (bubbleContent.getBoundingClientRect().width / 2);

            if (leftOverflow < 0 && currentCenterCoordinate > originalCenterCoordinate) {
                if (newLeftCoordinate > maxLeftCoordinate) {
                    bubbleContent.style.left = String(currentLeftStyle + leftOverflow) + "px";
                }
            }
            else if (rightOverflow < 0 && currentCenterCoordinate < originalCenterCoordinate) {
                if (newRightCoordinate < minRightCoordinate) {
                    bubbleContent.style.left = String(currentLeftStyle - rightOverflow - 1) + "px";
                }
            }
        });
    }
}

// Triggers after window has finished loading (i.e., all CSS and JavaScript has already been applied)
preventTooltipViewportOverflow(); // Need to call function twice like this for best results
window.addEventListener("load", preventTooltipViewportOverflow);

// Triggers when window is resized
window.addEventListener("resize", preventTooltipViewportOverflow);

window.addEventListener("resize", function() {
    var openedDropdowns = document.querySelectorAll('.dropdown-options.show');
    openedDropdowns.forEach(openedDropdown => {
        preventDropdownPageOverflow(openedDropdown);
    });
});

/*--------------------------------------------------------------------------------------------------------------------*/
/* TRI-STATE CHECKBOXES (BASIC) BEHAVIOUR */
function setTriStateCheckboxState(newState, checkbox, select, label) {
    // Use checkbox.value to store the state of the checkbox
    checkbox.value = newState;

    switch(newState) {
        case checkboxStates[0]: // No
            checkbox.indeterminate = true;
            select.value = 0;
            label.style.fontWeight = 400;
            break;
        case checkboxStates[1]: // Yes
            checkbox.checked = true;
            checkbox.indeterminate = false;
            select.value = 1;
            label.style.fontWeight = 400; // bold
            break;
        default: // Null
            checkbox.checked = false;
            checkbox.indeterminate = false;
            select.value = -1;
            label.style.fontWeight = 300;  // Normal / Not bold
            break;
     }
}

function setInitialTriStateValue(checkbox, select, label) {
    switch(select.value) {
    case "0":  // Checkbox.value = No (indeterminate), Select.value = 0, Label = bold
        setTriStateCheckboxState(checkboxStates[0], checkbox, select, label);
        break;
    case "1": // Checkbox.value = Yes (checked), Select.value = 1, Label = bold
        setTriStateCheckboxState(checkboxStates[1], checkbox, select, label);
        break;
    default: // Checkbox.value = Null (unchecked), Select.value = -1, Label = Normal
        setTriStateCheckboxState(checkboxStates[2], checkbox, select, label);
        break;
    }
}

function cycleTriStateValues(checkbox, select, label) {
    /* Cycle through states BACKWARDS because we want "yes" option to be associated with number 1 (i.e., true) &&
    * "no" to be associated with number 0 (i.e., false)
    * --> "yes" option at index [1] && "no" option at index [0]
    * --> "null" option has to be at index [2] as a result
    * BUT, we also want "yes" option to be after "null" when clicking --> so cycle checkboxStates backwards */

    // Get index of the next state
    // If nextStateIndex == -1 --> loop back to [2]
    const currentStateIndex = checkboxStates.indexOf(checkbox.value);
    const nextStateIndex = (currentStateIndex - 1) < 0 ? 2 : currentStateIndex - 1;
    setTriStateCheckboxState(checkboxStates[nextStateIndex], checkbox, select, label);
}

/*--------------------------------------------------------------------------------------------------------------------*/
/* DROPDOWN MENU CLOSING BEHAVIOUR */

// TODO: Replace with "focus out" event for every dropdown-button???
// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.dropdown-button') && !event.target.matches('.dropdown-button *')) {
        var dropdowns = document.getElementsByClassName("dropdown-options");
        var i;
        for (i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}

/*--------------------------------------------------------------------------------------------------------------------*/
// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function() {
    if (openSearchBarButton != null) {
        // Set openSearchBarButton behaviour (responsive styling)
        openSearchBarButton.addEventListener("click", toggleSearchBar); // will also close search bar if clicked again
    }

    if (closeSearchBarButton != null) {
        // Set closeSearchBarButton behaviour (responsive styling)
        closeSearchBarButton.addEventListener("click", closeSearchBar);
    }

    // Set dropdown menu behaviour for all dropdown menus on page
    // When the user clicks on the button, toggle between hiding and showing the dropdown content
    dropdowns.forEach(dropdown => {
        dropdownButtons = dropdown.querySelectorAll('.dropdown-button');

        dropdownButtons.forEach(dropdownButton => {
            dropdownButton.addEventListener("click", function() {
                dropdownOptions = dropdown.querySelector('.dropdown-options');
                dropdownOptions.classList.toggle('show');
                preventDropdownPageOverflow(dropdownOptions);
            });
        });
    });

    // Set custom behaviour for search dropdown:
    // - Update the text inside the dropdown menu button to the selected item
    // - Set the hidden Select element (from Django form) to the selected value
    // - Doing it this way because Select HTML elements can't be formatted/styled properly
    searchDropdownItems.forEach(item => {
        item.addEventListener("click", function(event) {
            event.preventDefault(); // Prevent page from jumping
            searchDropdownButtonSpan.textContent = this.textContent; // Change the button text to the clicked item's text
            const selectedValue = this.getAttribute('data-value');
            searchFormSelect.value = selectedValue;
        });
    });

    // Set tri-state checkboxes (for all pages, if they have any)
    triStateCheckboxContainer.forEach(container => {
        const checkbox = container.querySelector('input[type="checkbox"]');
        const select = container.querySelector('select');
        const label = container.querySelector('label');
        
        // Set values of every checkbox in a tri-state-checkbox-container based on the initial value of <select>
        setInitialTriStateValue(checkbox, select, label);
        

        // Set click behaviour (cycling through the 3 checkboxStates)
        checkbox.addEventListener('click', function(event) {
            event.stopPropagation();
            cycleTriStateValues(checkbox, select, label);
        });
        container.addEventListener('click', function(event) {
            event.preventDefault();
            cycleTriStateValues(checkbox, select, label);
        });
    });
});
