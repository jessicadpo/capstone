const openFilterMenuButton = document.getElementById('open-filter-menu-button');
const closeFilterMenuButton = document.getElementById('close-filter-menu-button');
const filterSidebar = document.getElementById('filter-sidebar');
const sortFilterForm = document.getElementById('filter-menu');
const applySortFilterButtons = document.querySelectorAll('#filter-menu input[type="submit"]');

const sortBySelect = document.getElementById('sort-order-select');
const yourContributionsTriStateContainers = document.querySelectorAll('#your-contributions-section .tri-state-checkbox-container');

const frequentLabels = document.querySelectorAll('#frequent-tags-section .tri-state-checkbox-container label');

const tagsToIncludeContainer = document.getElementById('tags-to-include-container');
const tagsToExcludeContainer = document.getElementById('tags-to-exclude-container');

const tagsToIncludeTextarea = document.getElementById('include-tags-textarea');
const tagsToExcludeTextarea = document.getElementById('exclude-tags-textarea');

function convertLabelsToStringArray(labelList) {
    // Use the value of the data-tag-text attribute if the label has one.
    // Otherwise just use the label's textContent
    return Array.from(labelList, label => label.getAttribute('data-tag-text') ? label.getAttribute('data-tag-text').trim() : label.textContent.trim());
}

function isFrequentTag(tagText) {
    // Returns true if tagText is one of the 5 most frequent tags. False if not.
    const frequentTags = convertLabelsToStringArray(frequentLabels);
    if (frequentTags.includes(tagText)) {
        return true;
    }
    return false;
}

/*--------------------------------------------------------------------------------------------------------------------*/
/* CREATING / REMOVING TRI-STATE CHECKBOXES */

function createRemoveFilterButton(filterTagValue) {
    const removeFilterButton = document.createElement("BUTTON");
    removeFilterButton.type = "button"; // Button does not reset the form when clicked
    removeFilterButton.classList.add("remove-filter-button");
    removeFilterButton.setAttribute('aria-label', "Remove filter for \"" + filterTagValue + "\" tag");
    removeFilterButton.textContent = "Remove filter";

    removeFilterButton.addEventListener('click', function() {
        const triStateContainer = removeFilterButton.closest('.tri-state-checkbox-container');
        removeTriStateFilter(triStateContainer);
    });

    return removeFilterButton;
}

function filterIsAlreadyAdded(filterTagValue, toInclude) {
    filterTagValue = filterTagValue.toLocaleLowerCase(); // Makes check case-insensitive
    const existingFilters = toInclude ? document.querySelectorAll('#tags-to-include-container label') : document.querySelectorAll('#tags-to-exclude-container label');
    // Can't use forEach (forEach cannot be interrupted by a return statement)
    for (let i = 0; i < existingFilters.length; i++) {
        existingFilter = existingFilters[i].textContent.toLocaleLowerCase(); // Makes check case-insensitive
        if (existingFilter.localeCompare(filterTagValue) === 0) {
            return true;
        }
    }
    return false;
}

function addTriStateFilter(filterTagValue, toInclude) {
    /* Do NOT add tag filter if:
    *    - input is empty OR
    *    - tag filter has already been added by user OR
    *    - tag is in Frequent Tags section
    *
    *  If tag is in Frequent Tags section:
    *    - Set the tag in Frequent Tags to include/exclude */
    if (isFrequentTag(filterTagValue)) {
        const query = '#frequent-tags-section .tri-state-checkbox-container:has(label[data-tag-text="' + filterTagValue + '"])';
        const frequentTriStateCheckboxContainer = document.querySelector(query);

        const checkbox = frequentTriStateCheckboxContainer.querySelector('input[type="checkbox"]');
        const select = frequentTriStateCheckboxContainer.querySelector('select');
        const label = frequentTriStateCheckboxContainer.querySelector('label');

        if (toInclude) {
             setTriStateCheckboxState(checkboxStates[1], checkbox, select, label); /* Defined in global.js */
        } else {
             setTriStateCheckboxState(checkboxStates[0], checkbox, select, label); /* Defined in global.js */
        }
        return false; // Checkbox already added to Frequent tags, technically
    }
    else if (filterTagValue.trim() !== '' && !filterIsAlreadyAdded(filterTagValue, toInclude)) {
        const triStateTemplate = document.getElementById('tri-state-checkbox-template');
        const triStateCheckboxContainer = triStateTemplate.content.children[0].cloneNode(true);

        const checkbox = triStateCheckboxContainer.querySelector('input[type="checkbox"]');
        const select = triStateCheckboxContainer.querySelector('select');
        const label = triStateCheckboxContainer.querySelector('label');
        const removeButton = createRemoveFilterButton(filterTagValue);

        label.textContent = filterTagValue; // Insert user input into triStateCheckboxContainer's <label> element
        label.style.fontWeight = 400;
        triStateCheckboxContainer.appendChild(removeButton); // Add "Remove filter" button to triStateCheckboxContainer

        // Add tri-state checkbox container to tags-to-include/exclude-container
        // && Set state of checkbox to include / exclude
        if (toInclude) {
            checkbox.checked = true;
            checkbox.disabled = true;
            select.value = 1;
            tagsToIncludeContainer.appendChild(triStateCheckboxContainer);

            // If tag is already in Tags to Exclude --> remove from Tags to Exclude
            if (filterIsAlreadyAdded(filterTagValue, false)) {
                const toRemove = Array.from(tagsToExcludeContainer.children).find(oppositeTriStateCheckboxContainer => {
                    const label = oppositeTriStateCheckboxContainer.querySelector('label');
                    return label && label.textContent === filterTagValue;
                });
                removeTriStateFilter(toRemove);
            }
        } else {
            checkbox.indeterminate = true;
            checkbox.disabled = true;
            select.value = 0;
            tagsToExcludeContainer.appendChild(triStateCheckboxContainer);

            // If tag is already in Tags to Include --> remove from Tags to Include
            if (filterIsAlreadyAdded(filterTagValue, true)) {
                const toRemove = Array.from(tagsToIncludeContainer.children).find(oppositeTriStateCheckboxContainer => {
                    const label = oppositeTriStateCheckboxContainer.querySelector('label');
                    return label && label.textContent === filterTagValue;
                });
                removeTriStateFilter(toRemove);
            }
        }
        return true; // tri-state checkbox container was successfully added
    }
    return false;
}


function removeTriStateFilter(toRemove) {
    if (toRemove) {
        toRemove.remove();
    }
}

/*--------------------------------------------------------------------------------------------------------------------*/
/* SETTING TRISTATE TAG FILTERS BASED ON DATA INSIDE TEXTAREAS (TO BE CALLED ON PAGE LOAD ONLY) */
function setTagFilterStates(filteredTags, areIncluded) {
    filteredTags.forEach(filteredTag => {
        addTriStateFilter(filteredTag, areIncluded);
    });
}

/*--------------------------------------------------------------------------------------------------------------------*/
/* SAVING TAGS TO INCLUDE/EXCLUDE BEFORE SORT-FILTER FORM SUBMISSION */

function getTagsToFilter(toInclude) {
    // Get all tags to include/exclude in an array of strings
    if (toInclude) {
        const frequentTagSelectsInclude = Array.from(document.querySelectorAll("#frequent-tags-section select")).filter(select => select.value === "1");
        const frequentIncludeLabels = frequentTagSelectsInclude
                                    .map(select => select.nextElementSibling)
                                    .filter(labelSibling => labelSibling && labelSibling.tagName === 'LABEL');
        const frequentTagsToInclude = convertLabelsToStringArray(frequentIncludeLabels);
        const additionalTagsToInclude = convertLabelsToStringArray(document.querySelectorAll("#tags-to-include-container .tri-state-checkbox-container label"));
        const allTagsToInclude = [...frequentTagsToInclude, ...additionalTagsToInclude];
        return allTagsToInclude;
    } else { // Get tags to exclude
        const frequentTagSelectsExclude = Array.from(document.querySelectorAll("#frequent-tags-section select")).filter(select => select.value === "0");
        const frequentExcludeLabels = frequentTagSelectsExclude
                                    .map(select => select.nextElementSibling)
                                    .filter(labelSibling => labelSibling && labelSibling.tagName === 'LABEL');
        const frequentTagsToExclude = convertLabelsToStringArray(frequentExcludeLabels);
        const additionalTagsToExclude = convertLabelsToStringArray(document.querySelectorAll("#tags-to-exclude-container .tri-state-checkbox-container label"));
        const allTagsToExclude = [...frequentTagsToExclude, ...additionalTagsToExclude];
        return allTagsToExclude;
    }
}

function copyTagsToFilterToTextarea(tagsToFilter, textarea) {
    textarea.value = ''; // Clear the textarea's contents

    tagsToFilter.forEach(tag => {
        // Do not add if textArea already contains the tag
        if (!textarea.value.includes(tag)) {
            textarea.value += tag + '\\n';
        }
    });
}

/*--------------------------------------------------------------------------------------------------------------------*/
// FILTER MENU SIDEBAR (RESPONSIVE)
function openFilterMenu() {
    openSidebar(filterSidebar, true); // see global.js
    document.getElementById('user-account-sidenav').setAttribute('inert', '');

    // Move the tooltips in sync with scrolling
    document.querySelector('#filter-menu').addEventListener('scroll', () => {
        const headingContainers = document.querySelectorAll('.heading-container:has(.tooltip)');
        headingContainers.forEach(headingContainer => {
            const tooltip = headingContainer.querySelector('.tooltip');
            tooltip.style.top = headingContainer.getBoundingClientRect().top + "px";
        });
    });
}

function closeFilterMenu() {
    document.getElementById('user-account-sidenav').removeAttribute('inert');
    closeSidebar(filterSidebar, true); // see global.js
}

/*--------------------------------------------------------------------------------------------------------------------*/
// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function () {
    // Set open & close filter menu behavior
    openFilterMenuButton.addEventListener("click", openFilterMenu);
    sidebarOverlay.addEventListener("click", closeFilterMenu); // sidebarOverlay defined in global.js
    closeFilterMenuButton.addEventListener("click", function(event) {
        event.preventDefault(); // Prevent filter form submission (default behaviour)
        closeFilterMenu();
    });

    // Add tristate checkboxes for every filtered tag (listed in the textareas) && set the state
    // If a frequent tag --> just set the state
    setTagFilterStates(tagsToIncludeTextarea.value.split('\\n'), true);
    setTagFilterStates(tagsToExcludeTextarea.value.split('\\n'), false);

    // Only "Enter" keypress when focused on a submit input should submit SortFilter form
    sortFilterForm.addEventListener('keydown', function(event) {
        if (event.key === "Enter" && event.target.type !== "submit") {
            event.preventDefault();

            if (event.target.type === "checkbox") {
                const checkbox = event.target;
                const select = event.target.nextElementSibling;
                const label = event.target.nextElementSibling.nextElementSibling;
                cycleTriStateValues(checkbox, select, label); // Defined in global.js
            }

            // If entering a tag to filter in "Tags to Include" or "Tags to Exclude" text inputs
            if (event.target.type === 'text') {
                const filterTagValue = event.target.value;
                const toInclude = event.target.id === 'additional-include-input' ? true : false;
                addTriStateFilter(filterTagValue, toInclude);
                event.target.value = ''; // Clear text field
            }
        }
    });

    // Set "Apply Sort & Filter(s)" behaviour
    applySortFilterButtons.forEach(applySortFilterButton => {
        applySortFilterButton.addEventListener('click', (event) => {
            event.preventDefault();
            copyTagsToFilterToTextarea(getTagsToFilter(true), tagsToIncludeTextarea);
            copyTagsToFilterToTextarea(getTagsToFilter(false), tagsToExcludeTextarea);
            sortFilterForm.submit();
        });
    });
});