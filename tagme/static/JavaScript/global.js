const topBar = document.getElementById('top-bar');
const searchBar = document.querySelector('#top-bar #search-bar');  // Only applies to the search bar in top bar (not homepage search bar)
const closeSearchBarButton = document.getElementById('close-search-bar-button');
const openSearchBarButton = document.getElementById('open-search-bar-button');

const mainContent = document.getElementById('main-content');
const footer = document.getElementById('footer');
const sidebarOverlay = document.querySelector('.sidebar-overlay');

const tooltips = document.querySelectorAll(".tooltip");
const dropdowns = document.querySelectorAll('.dropdown');
const seeMoreButtons = document.querySelectorAll(".see-more-button");

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

            // DO NOT PROCEED IF TOOLTIP BUBBLE IS NOT "ON TOP" OR "ON BOTTOM"
            if (!tooltipBubble.classList.contains('bubble-on-top') && !tooltipBubble.classList.contains('bubble-on-bottom')) {
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

function preventResponsiveGridOverflow(responsiveGrid) {
    if (!responsiveGrid.classList.contains('responsive-grid')) {
        return null;
    }

    setMinResponsiveGridButtonWidth(responsiveGrid);

    // Calculate best possible grid layout
    // Number of columns == However many buttons (when at minButtonWidth) can fit in 1 row
    // Number of rows == However many are necessary based on the number of children inside responsiveGrid && number of columns
    const minButtonWidth = parseFloat(responsiveGrid.dataset.minButtonWidth);
    const childrenCount = Array.from(responsiveGrid.children).filter(child => {
                            return getComputedStyle(child).display != "none";
                        }).length;
    const columnGap = parseFloat(getComputedStyle(responsiveGrid).columnGap);

    // Cannot have more buttonsPerRow than actual buttons in responsiveGrid.
    // + 1 so that the first loop of do-while loop uses the correct buttonsPerRow.
    var buttonsPerRow = Math.min(childrenCount, Math.floor(responsiveGrid.clientWidth / minButtonWidth)) + 1;
    var totalColumnGap = 0;
    var minOccupiedSpace = 0;

    do {
        buttonsPerRow -= 1;
        totalColumnGap = columnGap * (buttonsPerRow - 1);
        minOccupiedSpace = (minButtonWidth * buttonsPerRow) + totalColumnGap;
    } while (responsiveGrid.clientWidth < minOccupiedSpace);

    const rowCount = Math.ceil(childrenCount / buttonsPerRow);
    const columnCount = buttonsPerRow;

    responsiveGrid.style.gridTemplateColumns = "repeat(" + columnCount + ", auto)";
    responsiveGrid.style.gridTemplateRows = "repeat(" + rowCount + ", auto)";

    // Add new classes to responsiveGrid to allow for custom styling in CSS when number of rows/columns increases
    if (rowCount > 1) {
        responsiveGrid.classList.add("multi-row");
    } else {
        responsiveGrid.classList.remove("multi-row");
    }
    if (columnCount > 1) {
        responsiveGrid.classList.add("multi-column");
    } else {
        responsiveGrid.classList.remove('multi-column');
    }
}

function setMinResponsiveGridButtonWidth(responsiveGrid) {
    // Get the width of the biggest modal-footer-button when width: fit-content && everything in 1 row
    // Store that width in a data-min-button-width attribute (in responsiveGrid)
    if (!responsiveGrid.hasAttribute("data-min-button-width")) { // Only calculate this once per responsiveGrid
        responsiveGrid.classList.remove('responsive-grid'); // Temporarily remove responsive-grid class
        const responsiveGridButtons = responsiveGrid.querySelectorAll('button');
        var fitButtonWidth = 0;
        var maxFitButtonWidth = 0;

        responsiveGridButtons.forEach(responsiveGridButton => {
            // Ensure button's width & min-width are fit-content
            responsiveGridButton.style.width = "fit-content";
            responsiveGridButton.style.minWidth = "fit-content";

            fitButtonWidth = parseFloat(getComputedStyle(responsiveGridButton).width);
            maxFitButtonWidth = fitButtonWidth > maxFitButtonWidth ? fitButtonWidth : maxFitButtonWidth;

            // Return to original styling
            responsiveGridButton.style.width = '';
            responsiveGridButton.style.minWidth = '';
        });

        // Set the minWidth of every responsiveGridButton as the minButtonWidth
        // IMPORTANT for being able to correctly detect when responsiveGrid.scrollWidth > responsiveGrid.clientWidth
        responsiveGridButtons.forEach(responsiveGridButton => {
            responsiveGridButton.style.minWidth = maxFitButtonWidth + "px";
        })

        responsiveGrid.setAttribute("data-min-button-width", maxFitButtonWidth + "px");
        responsiveGrid.classList.add('responsive-grid'); // Return to responsive-grid
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

/*--------------------------------------------------------------------------------------------------------------------*/
/* SIDEBARS (DISABLING / ENABLING INTERACTION) */
function openSidebar(sidebar, fromRight) {
    if (fromRight) {
        sidebar.style.right = "0%";
    } else {
        sidebar.style.left = "0%";
    }

    sidebarOverlay.classList.add('active');
    document.documentElement.style.overflowY = "hidden"; // Disable scrolling on the main content
    topBar.setAttribute('inert', ''); // Disable keyboard interaction
    footer.setAttribute('inert', '');

    if (mainContent.contains(sidebar)) {
        const toDisable = mainContent.querySelectorAll(":not(#" + sidebar.id + "):not(#" + sidebar.id + " *)");
        toDisable.forEach(element => {
            element.setAttribute('inert', '');
        })
    } else {
        mainContent.setAttribute('inert', '');
    }
}

function closeSidebar(sidebar, toRight) {
    if (toRight) {
        sidebar.style.right = "-100%";
    } else {
        sidebar.style.left = "-100%";
    }

    sidebarOverlay.classList.remove('active');
    document.documentElement.style.overflowY = ''; // Re-enable scrolling on the main content
    topBar.removeAttribute('inert');
    footer.removeAttribute('inert');

    if (mainContent.contains(sidebar)) {
        const toDisable = mainContent.querySelectorAll(":not(#" + sidebar.id + ")");
        toDisable.forEach(element => {
            element.removeAttribute('inert');
        })
    } else {
        mainContent.removeAttribute('inert');
    }
}

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
/* SEE MORE / SEE LESS BEHAVIOUR */

function toggleSeeMore(seeMoreButton) {
    const seeMoreContent = seeMoreButton.closest('.see-more-container').querySelector('.see-more-content');

    // Adjust ALL ancestor see-more-containers
    let seeMoreContainers = [];
    let currentAncestorElement = seeMoreButton.parentElement;
    while (currentAncestorElement) {
        if (currentAncestorElement.classList.contains('see-more-container')) {
            seeMoreContainers.push(currentAncestorElement);
        }
        currentAncestorElement = currentAncestorElement.parentElement;
    }

    if (seeMoreContent.classList.contains('collapsed')) { // If seeMoreContent is collapsed --> Expand --> button should say "See less"
        seeMoreContent.classList.remove('collapsed');
        seeMoreContent.classList.add('expanded'); // Need this for checkNeedSeeMoreButton

        seeMoreContent.style.maxHeight = "fit-content";
        seeMoreContent.style.height = "fit-content";
        seeMoreContainers.forEach(seeMoreContainer => {
            seeMoreContainer.style.maxHeight = "fit-content";
        });

        const expandedText = seeMoreButton.getAttribute('data-expanded-text') != null ? seeMoreButton.getAttribute('data-expanded-text') : "See less";
        seeMoreButton.innerHTML = expandedText + ' <i class="fa fa-angle-up" aria-hidden="true"></i>';
    }
    else { // If seeMoreContent is expanded --> Collapse --> Button should say "See more"
        seeMoreContent.classList.add('collapsed'); // Only apply gradient if button says "Read More"
        seeMoreContent.classList.remove("expanded");

        seeMoreContent.style.maxHeight = '';
        seeMoreContent.style.height = '';
        seeMoreContainers.forEach(seeMoreContainer => {
            seeMoreContainer.style.maxHeight = '';
        });

        const collapsedText = seeMoreButton.getAttribute('data-collapsed-text') != null ? seeMoreButton.getAttribute('data-collapsed-text') : "See more";
        seeMoreButton.innerHTML = collapsedText + ' <i class="fa fa-angle-down" aria-hidden="true"></i>';
    }
}

function checkNeedSeeMoreButtons(expandedText) {
    seeMoreButtons.forEach(seeMoreButton => {
        const seeMoreContainer = seeMoreButton.closest('.see-more-container');
        const seeMoreContent = seeMoreContainer.querySelector('.see-more-content');

        // Save seeMoreContainer's original maxHeight for future reference
        if (seeMoreContainer.getAttribute('data-og-max-height') == null) {
            seeMoreContainer.setAttribute('data-og-max-height', getComputedStyle(seeMoreContainer).getPropertyValue("max-height"));
        }

        const originalMaxHeight = parseFloat(seeMoreContainer.getAttribute('data-og-max-height'));

        if (seeMoreContent.scrollHeight > originalMaxHeight && !seeMoreContent.classList.contains("expanded")) {
            seeMoreButton.style.display = "block";
            seeMoreContent.classList.remove("collapsed"); // Ensures collapsed styling is applied by toggleSeeMore()
            toggleSeeMore(seeMoreButton);
        } else if (seeMoreContent.scrollHeight < originalMaxHeight) {
            seeMoreButton.style.display = "none";
            seeMoreContent.classList.remove("collapsed"); // Remove gradient
            seeMoreContent.classList.remove('expanded'); // Reset if resized while in expanded set
        }
    });
}


/*--------------------------------------------------------------------------------------------------------------------*/
/* CAROUSELS / SLIDESHOWS */

function activateCarouselBehaviour(carousel) {
    // TODO: Looping carousels (?? need?)

    // Ensure carousel element has class "carousel"
    carousel.classList.add('carousel');

    const carouselStrip = carousel.querySelector('.carousel-strip');
    if (carouselStrip == null) {
        throw new Error('Carousel must have a child element with "carousel-strip" class.')
    }

    // Carousel-strip's should be == its left + right padding (if it has any)
    const carouselStripHorizontalPadding = parseFloat(getComputedStyle(carouselStrip).paddingRight) + parseFloat(getComputedStyle(carouselStrip).paddingLeft);
    carouselStrip.style.gap = carouselStripHorizontalPadding + "px";

    // If no slide currently active --> set the first .slide-card as the active slide
    // Else --> Move carousel-strip to active slide
    if (carousel.querySelector('.slide-card.active') === null) {
        carousel.querySelector('.slide-card:first-of-type').classList.add('active');
    } else {
        const currentSlideNumber = parseInt(carousel.querySelector('.slide-card.active').getAttribute('data-slide-number'));
        const translateXValue = (currentSlideNumber * 100) + "%";

        // Temporarily disable transition animation for transforms
        carouselStrip.style.transition = 'none';
        carouselStrip.style.transform = "translateX(-" + translateXValue + ")";

        // Re-enable transition animation
        requestAnimationFrame(() => { // Ensure re-enable transition AFTER transform style has been applied
            requestAnimationFrame(() => {
                carouselStrip.style.transition = '';
            });
        });
    }

    // Set .slide-controls behaviour
    carousel.querySelector('.prev-slide-button').addEventListener("click", goToPrevSlide);
    carousel.querySelector('.next-slide-button').addEventListener("click", goToNextSlide);

    // Assign data-slide-number to every .slide-card
    var slideNumber = 0;
    carousel.querySelectorAll(".slide-card").forEach(slideCard => {
        slideCard.setAttribute("data-slide-number", slideNumber);
        slideNumber++;
    });

    toggleSlideControls(carousel); // Figure out which .slide-controls should be displayed/visible
}

function deactivateCarouselBehaviour(carousel) {
    const carouselStrip = carousel.querySelector('.carousel-strip');

    carousel.classList.remove('carousel');

    // carouselStrip --> Return to original gap + Undo any translateX
    carouselStrip.style.gap = '';
    carouselStrip.style.transform = '';

    // All .slide-card elements return to visibility: whatever it's set at in CSS
    carousel.querySelectorAll(".slide-card").forEach(slideCard => {
        slideCard.style.visibility = '';
    });

    // All .slide-control buttons return to display: none
    // Remove eventListeners from all .slide-controls (are re-added if re-activate carousel)
    const prevSlideButton = carousel.querySelector('.prev-slide-button');
    const nextSlideButton = carousel.querySelector('.next-slide-button');
    prevSlideButton.style.display = ''; // Return to whatever it's set at in CSS (probably "none")
    nextSlideButton.style.display = ''; // Return to whatever it's set at in CSS (probably "none")
    prevSlideButton.removeEventListener('click', goToPrevSlide);
    nextSlideButton.removeEventListener('click', goToNextSlide);
}

function toggleSlideControls(carousel) {
    // Figure out which .slide-controls should be displayed/visible
    const currentSlide = carousel.querySelector('.slide-card.active');
    const currentSlideNumber = currentSlide.getAttribute('data-slide-number');
    const totalSlideCount = carousel.querySelectorAll('.slide-card').length;

    const prevSlideButton = carousel.querySelector('.prev-slide-button');
    const nextSlideButton = carousel.querySelector('.next-slide-button');

    prevSlideButton.style.display = parseInt(currentSlideNumber) === 0 ? "none" : "flex";
    nextSlideButton.style.display = parseInt(currentSlideNumber) === totalSlideCount - 1 ? "none" : "flex";
}

function goToPrevSlide(event) {
    const carousel = event.currentTarget.closest('.carousel');
    const carouselStrip = carousel.querySelector('.carousel-strip');

    prepTransition(carousel);

    const currentSlide = carouselStrip.querySelector('.slide-card.active');
    const prevSlideNumber = parseInt(currentSlide.getAttribute('data-slide-number')) - 1;
    const prevSlide = carouselStrip.querySelector('.slide-card[data-slide-number="' + prevSlideNumber + '"]');
    const translateXValue = (prevSlideNumber * 100) + "%";

    carouselStrip.style.transform = "translateX(" + translateXValue + ")";
    currentSlide.classList.remove('active');
    prevSlide.classList.add('active');

    toggleSlideControls(carousel);
    undoTransitionPrep(carousel);
}

function goToNextSlide(event) {
    const carousel = event.currentTarget.closest('.carousel');
    const carouselStrip = carousel.querySelector('.carousel-strip');

    prepTransition(carousel);

    const currentSlide = carouselStrip.querySelector('.slide-card.active');
    const nextSlideNumber = parseInt(currentSlide.getAttribute('data-slide-number')) + 1;
    const nextSlide = carouselStrip.querySelector('.slide-card[data-slide-number="' + nextSlideNumber + '"]');
    const translateXValue = (nextSlideNumber * 100) + "%";

    carouselStrip.style.transform = "translateX(-" + translateXValue + ")";
    currentSlide.classList.remove('active');
    nextSlide.classList.add('active');

    toggleSlideControls(carousel);
    undoTransitionPrep(carousel);
}

function prepTransition(carousel) {
    // Close any open tooltips before transition (i.e., set visibility to "hidden")
    // Set overflow to "hidden" just before & during transitions
    // Set visibility of all slides to "visible" just before transition
    const carouselTooltips = carousel.querySelectorAll('.tooltip-bubble');
    if (carouselTooltips != null) {
        carouselTooltips.forEach(tooltipBubble => {
            tooltipBubble.style.visibility = "hidden";
        });
    }
    carousel.style.overflow = "hidden";
    carousel.querySelectorAll('.slide-card').forEach(slideCard => {
        slideCard.style.visibility = "visible";
    });
}

function undoTransitionPrep(carousel) {
    // Set visibility of all inactive slides to "hidden" AFTER transition is done
    // Set overflow back to "visible" after transition (allows tooltips to overflow)
    // Remove visibility styling on tooltips after transition (disables tooltip behaviour otherwise)
    setTimeout(() => {
        carousel.querySelectorAll('.slide-card:not(.active)').forEach(inactiveSlideCard => {
            inactiveSlideCard.style.visibility = "hidden";
        });
        carousel.style.overflow = "visible";
        const carouselTooltips = carousel.querySelectorAll('.tooltip-bubble');
        if (carouselTooltips != null) {
            carouselTooltips.forEach(tooltipBubble => {
                tooltipBubble.style.visibility = "";
            });
        }
    }, 500); // 500ms == 0.5s (same time as transition)
}

/*--------------------------------------------------------------------------------------------------------------------*/
// Triggers after window has finished loading (i.e., all CSS and JavaScript has already been applied)
preventTooltipViewportOverflow(); // Need to call function twice like this for best results
window.addEventListener("load", preventTooltipViewportOverflow);
window.addEventListener("load", checkNeedSeeMoreButtons);

// Triggers when window is resized
window.addEventListener("resize", checkNeedSeeMoreButtons);
window.addEventListener("resize", preventTooltipViewportOverflow);
window.addEventListener("resize", function() {
    var openedDropdowns = document.querySelectorAll('.dropdown-options.show');
    openedDropdowns.forEach(openedDropdown => {
        preventDropdownPageOverflow(openedDropdown);
    });
});

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

    // Set behaviour of "See More" buttons
    seeMoreButtons.forEach(seeMoreButton => {
        seeMoreButton.addEventListener('click', function () {
            toggleSeeMore(seeMoreButton);
        });
    });

    // Set tooltip behaviour (responsive)
    tooltips.forEach(tooltip => {
        const tooltipIcon = tooltip.querySelector("i");
        tooltipIcon.addEventListener('click', preventTooltipViewportOverflow);
        tooltipIcon.addEventListener('focus', preventTooltipViewportOverflow);
        tooltipIcon.addEventListener('mouseover', preventTooltipViewportOverflow);
    });

    // Set dropdown menu behaviour for all dropdown menus on page
    // When the user clicks on the button, toggle between hiding and showing the dropdown content
    dropdowns.forEach(dropdown => {
        dropdownButtons = dropdown.querySelectorAll('.dropdown-button');

        dropdownButtons.forEach(dropdownButton => {
            // Opening behaviour
            dropdownButton.addEventListener("click", function() {
                dropdownOptions = dropdown.querySelector('.dropdown-options');
                dropdownOptions.classList.toggle('show');
                preventDropdownPageOverflow(dropdownOptions);
            });

            // Closing behaviour
            dropdownButton.addEventListener("blur", function(event) {
                // Do not close if clicked inside .dropdown-options
                var clickedTarget = event.explicitOriginalTarget;
                if (clickedTarget.nodeType != 1) { /* If clickedTarget is an attribute or text node (for example) */
                    clickedTarget = clickedTarget.parentElement;
                }

                if (clickedTarget == null || clickedTarget.closest('.dropdown-options') == null) {
                    dropdownOptions = dropdown.querySelector('.dropdown-options');
                    dropdownOptions.classList.remove('show');
                }
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
            this.parentElement.classList.remove('show');
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
