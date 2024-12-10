const newRewardOverlay = document.getElementById('new-reward-overlay');
const newRewardModal = document.getElementById('new-reward-modal');
const newReward = document.querySelectorAll('#new-reward-modal .reward-title span');
const skipEquipButton = document.getElementById('skip-equip-button');
const yesEquipButton = document.getElementById('yes-equip-button');
const fireworks = document.querySelectorAll('.firework');

const equipTitleForm = document.getElementById('equip-title-form');
const titleToEquipFormField = document.getElementById('title-to-equip-input');
const equipPositionFormField = document.getElementById('equip-position-input');

function openNewRewardModal() {
    newRewardOverlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // Disable scrolling on the main content

    // Make modal (& overlay) fade in on open
    newRewardModal.style.opacity = 0;
    newRewardModal.style.visibility = 'visible';
    newRewardModal.showModal();
    setTimeout(() => {
        newRewardOverlay.style.opacity = 0.75;
        newRewardModal.style.opacity = 1;
    }, 0);

    playFireworks();
}

function closeNewRewardModal() {
    newRewardModal.close();
    document.body.style.overflow = ''; // Re-enable scrolling on the main content
    newRewardOverlay.classList.remove('active');
}

function checkIfNewReward() {
    if (newReward.length > 0) {
        openNewRewardModal();
    }
}

function playFireworks() {
    // Wait for fade-in animation to be done
    setTimeout(() => {
        fireworks.forEach(firework => {
            firework.classList.remove('invisible');
            firework.classList.add('playing');
        });
    }, 1000);

    // Stop fireworks after 6 seconds (3 x 2s animation)
    setTimeout(() => {
        fireworks.forEach(firework => {
            firework.classList.remove('playing');
            firework.classList.add('invisible');
        });
    }, 7000);
}

function equipTitle() {
        // Auto-enter title to equip in hidden form field
    titleToEquipFormField.value = newReward.textContent;

}

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' || event.keyCode === 27) {
        closenewRewardModal();
    }
});

// Triggers after DOM content is finished loading
document.addEventListener("DOMContentLoaded", function() {
    // Set close modal button behaviour
    skipEquipButton.addEventListener('click', closeNewRewardModal);

    // Set "Yes" (Equip) button behaviour
    yesEquipButton.addEventListener('click', function() {
        event.preventDefault();

        // Fill hidden form fields with new title to equip
        titleToEquipFormField.value = newReward.textContent;
        equipPositionFormField.value = "1"; // Always equip new rewards as Title #1 TODO: Change?

        equipTitleForm.submit();
        closeNewRewardModal();
    });

    // Check if New Rewards modal should be shown when page loads (i.e., when page reloads after saving/unpinning tags)
    checkIfNewReward();
});