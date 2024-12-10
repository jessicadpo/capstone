const currentProgressBar = document.getElementById('current-progress-bar');
const startTickNumberSpan = document.querySelector('#start-tickmark span')
const middleTickNumberSpan = document.querySelector('#middle-tickmark span');
const endTickNumberSpan = document.querySelector('#end-tickmark span');
const earnedTitles = document.querySelectorAll('#earned-titles-content .reward-title');
const dropzones = document.querySelectorAll('.dropzone');

function setCurrentProgressBarWidth() {
    const currentProgressPoints = parseInt(middleTickNumberSpan.textContent);
    const pointsGoal = parseInt(endTickNumberSpan.textContent);

    let progress_percentage = Math.round((currentProgressPoints / pointsGoal) * 100);
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
        middleTickNumberSpan.style.right = (overlapAmount + 5).toString() + "px";
    }
}

function makeEarnedTitlesDraggable() {
    earnedTitles.forEach(earnedTitle => {
        earnedTitle.setAttribute('draggable', 'true');

        // Set drag behaviour (style dropzones)
        earnedTitle.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData("text/plain", e.target.textContent); // Pass the textContent of the title being dragged
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

            const titleText = e.dataTransfer.getData("text/plain");

            // TODO: submit equip form
        });
    });
}


// When the user clicks on the button, toggle between hiding and showing the dropdown content
function openEquipDropdown(editButton) {
    editButton.parentElement.querySelector(".dropdown-options").classList.toggle("show");

}



// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function() {
    setCurrentProgressBarWidth();
    preventTickmarkOverlap();
    makeEarnedTitlesDraggable();
})
