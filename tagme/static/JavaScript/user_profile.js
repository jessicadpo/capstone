const currentProgressBar = document.getElementById('current-progress-bar');
const startTickNumberSpan = document.querySelector('#start-tickmark span')
const middleTickNumberSpan = document.querySelector('#middle-tickmark span');
const endTickNumberSpan = document.querySelector('#end-tickmark span');
const earnedTitles = document.querySelectorAll('#earned-titles-content .reward-title');
const dropzones = document.querySelectorAll('.dropzone');

const equippedSlot1 = document.getElementById("equipped-title-1");
const equippedSlot2 = document.getElementById("equipped-title-2");
const dropdownItemsSlot1 = document.querySelectorAll("#equipped-title-1 ~ .dropdown-options > *");
const dropdownItemsSlot2 = document.querySelectorAll("#equipped-title-2 ~ .dropdown-options > *");

const equipForm = document.getElementById("equip-form");
const titleToEquipFormField = document.getElementById('title-to-equip-input');
const equipSlotFormField = document.getElementById('equip-slot-input');

/*--------------------------------------------------------------------------------------------------------------------*/
/* PROGRESS SECTION */
function setCurrentProgressBarWidth() {
    const currentProgressPoints = parseInt(middleTickNumberSpan.textContent);
    const pointsGoal = parseInt(endTickNumberSpan.textContent);

    let progress_percentage = Math.round((currentProgressPoints / pointsGoal) * 100);
    if (progress_percentage > 100) {
        progress_percentage = 100;
    }
    currentProgressBar.style.width = progress_percentage.toString() + "%";
}

function preventTickmarkOverlap() {
    const startTick = startTickNumberSpan.getBoundingClientRect();
    const middleTick = middleTickNumberSpan.getBoundingClientRect();
    const endTick = endTickNumberSpan.getBoundingClientRect();

    /* Check if start & middle tickmark numbers overlap */
    if (startTick.left < middleTick.right && startTick.right > middleTick.left) {
        /* Reposition middleTickNumberSpan more towards the right */
        const overlapAmount = startTick.right - middleTick.left;
        middleTickNumberSpan.style.left = (overlapAmount + 5).toString() + "px";
    }

    /* Check if middle & end tickmark numbers overlap */
    if (middleTick.left < endTick.right && middleTick.right > endTick.left) {
        /* Reposition middleTickNumberSpan more towards the left */
        const overlapAmount = middleTick.right - endTick.left;
        middleTickNumberSpan.style.right = (overlapAmount + 10).toString() + "px";
    }
}

/*--------------------------------------------------------------------------------------------------------------------*/
/* EQUIPPED TITLES SECTION */

function updateEquippedTitle(toEquip, equipSlotNumber) {
    if (equipSlotNumber === 1) {
        toUnequip = document.querySelector("#equipped-title-1 > div");
        equippedSlot1.replaceChild(toEquip, toUnequip);

        // Fill hidden form fields with new title to equip
        titleToEquipFormField.value = toEquip.querySelector("span").textContent;
        equipSlotFormField.value = "1";
    }
    else if (equipSlotNumber === 2) {
        toUnequip = document.querySelector("#equipped-title-2 > div");
        equippedSlot2.replaceChild(toEquip, toUnequip);

        // Fill hidden form fields with new title to equip
        titleToEquipFormField.value = toEquip.querySelector("span").textContent;
        equipSlotFormField.value = "2";
    }

    equipForm.submit();
}

/*--------------------------------------------------------------------------------------------------------------------*/
/* EARNED TITLES SECTION */

function makeEarnedTitlesDraggable() {
    earnedTitles.forEach(earnedTitle => {
        earnedTitle.setAttribute('draggable', 'true');

        // Set drag behaviour (style dropzones)
        earnedTitle.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData("text/plain", e.target.outerHTML); // Pass the textContent of the title being dragged
        });
    });

    // Drag over event (allow dropping)
    dropzones.forEach(dropzone => {
        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault(); // Prevent default to allow dropping
            dropzone.classList.add("hovered");
        });

        // Drag leave event
        dropzone.addEventListener("dragleave", () => {
            dropzone.classList.remove("hovered");
        });

        // Drop event
        dropzone.addEventListener("drop", (e) => {
            e.preventDefault(); // Prevent browser default handling
            dropzone.classList.remove("hovered");

            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = e.dataTransfer.getData("text/plain");
            const earnedTitleClone = tempDiv.firstElementChild;
            earnedTitleClone.removeAttribute('draggable');

            // Figure out if this is dropzone for equipSlot1 or equipSlot2
            if (dropzone.id === 'equipped-title-1') {
                updateEquippedTitle(earnedTitleClone, 1);
            } else if (dropzone.id === 'equipped-title-2') {
                updateEquippedTitle(earnedTitleClone, 2);
            }
        });
    });
}


// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function() {
    if (currentProgressBar != null) {
        setCurrentProgressBarWidth();
        preventTickmarkOverlap();
    }

    makeEarnedTitlesDraggable();

    // Update the text inside the (relevant) equip slot to the selected dropdown option
    dropdownItemsSlot1.forEach(item => {
        item.addEventListener("click", function(event) {
            event.preventDefault(); // Prevent page from jumping
            const selectedTitleClone = this.cloneNode(true);
            selectedTitleClone.setAttribute('tabindex', '-1');
            updateEquippedTitle(selectedTitleClone, 1);  // Change the equipped div with the clicked div
            this.parentElement.classList.remove('show');
        });

        item.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                item.click();
            }
        });
    });

    dropdownItemsSlot2.forEach(item => {
        item.addEventListener("click", function(event) {
            event.preventDefault(); // Prevent page from jumping
            const selectedTitleClone = item.cloneNode(true);
            selectedTitleClone.setAttribute('tabindex', '-1');
            updateEquippedTitle(selectedTitleClone, 2);  // Change the equipped div with the clicked div
            item.parentElement.classList.remove('show');
        });

        item.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                item.click();
            }
        });
    });

});
