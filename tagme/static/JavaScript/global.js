// When the user clicks on the button, toggle between hiding and showing the dropdown content
function openSearchDropdown() {
  document.getElementById("search-dropdown-options").classList.toggle("show");
}

function openAccountDropdown() {
  document.getElementById("account-dropdown-options").classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropdown-button')) {
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

// Update the text inside the dropdown menu button to the selected item
// Set the hidden Select element (from Django form) to the selected value
// Doing it this way because Select HTML elements can't be formatted/styled properly
const dropdownButton = document.getElementById("search-dropdown-button");
const dropdownItems = document.querySelectorAll(".search-dropdown-item");
dropdownItems.forEach(item => {
    item.addEventListener("click", function(event) {
        event.preventDefault(); // Prevent page from jumping
        dropdownButton.textContent = this.textContent; // Change the button text to the clicked item's text
        const selectedValue = this.getAttribute('data-value');
        document.getElementById('search-type-select').value = selectedValue;
    });
});
