const dropdownButton = document.getElementById("search-dropdown-button");
const dropdownButtonSpan = document.getElementById("search-dropdown-button-text");
const dropdownItems = document.querySelectorAll(".search-dropdown-item");
const dropdownFormSelect = document.getElementById('search-type-select');
const triStateCheckboxContainer = document.querySelectorAll('.tri-state-checkbox-container');
const checkboxStates = ['no', 'yes', 'null'];

// When the user clicks on the button, toggle between hiding and showing the dropdown content
function openSearchDropdown() {
  document.getElementById("search-dropdown-options").classList.toggle("show");
}

function openAccountDropdown() {
  document.getElementById("account-dropdown-options").classList.toggle("show");
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

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function() {
    // Update the text inside the dropdown menu button to the selected item
    // Set the hidden Select element (from Django form) to the selected value
    // Doing it this way because Select HTML elements can't be formatted/styled properly
    dropdownItems.forEach(item => {
        item.addEventListener("click", function(event) {
            event.preventDefault(); // Prevent page from jumping
            dropdownButtonSpan.textContent = this.textContent; // Change the button text to the clicked item's text
            const selectedValue = this.getAttribute('data-value');
            dropdownFormSelect.value = selectedValue;
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
