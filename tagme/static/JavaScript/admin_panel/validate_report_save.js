var originalDecision;

function validateDecision(event) {
    event.preventDefault(); // Prevent submit and save (give enough time for AJAX request)

    const newDecision = document.getElementById('id_decision').value;
    if (newDecision === originalDecision) {
        return; // Do nothing if decision wasn't altered
    }

    var showWarning = false;
    var warningMessage = "";
    var formData = new FormData(document.querySelector("#report_form"));
    formData.append('report_id', window.location.pathname.split('/')[4]);

    // Send AJAX request for checking if the tag's list fields would change with new decision
    fetch(window.location.href, {
        method: "POST",
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);

        // If tag will be removed from global_blacklist by this new decision
        if (data.tag_changes.gb_changed && !data.new_tag.gb) {
            showWarning = true;
            warningMessage += "- \"" + data.reported_tag + "\" will be removed from the global blacklist.\n"
            if (data.new_tag.gw) {
                warningMessage += "- \"" + data.reported_tag + "\" will be moved from the global blacklist to the global whitelist.\n";
            }
        }

        // If tag will be removed from global_whitelist by this new decision
        if (data.tag_changes.gw_changed && !data.new_tag.gw) {
            showWarning = true;
            warningMessage += "- \"" + data.reported_tag + "\" will be removed from the global whitelist.\n";
            if (data.new_tag.gb) {
                warningMessage += "- \"" + data.reported_tag + "\" will be moved from the global whitelist to the global blacklist.\n";
            }
        }

        // If tag will be removed from item's blacklist
        if (data.tag_changes.ib_changed && !data.new_tag.ib) {
            showWarning = true;
            if (data.new_tag.iw) {
                warningMessage += "- \"" + data.reported_tag + "\" will be moved from this item's blacklisted tags to its whitelisted tags.\n";
            } else {
                warningMessage += "- \"" + data.reported_tag + "\" will be removed from this item's blacklisted tags.\n";
            }
        }

        // If tag will be removed from item's whitelist
        if (data.tag_changes.iw_changed && !data.new_tag.iw) {
            showWarning = true;
            if (data.new_tag.ib) {
                warningMessage += "- \"" + data.reported_tag + "\" will be moved from this item's whitelisted tags to its blacklisted tags.\n";
            } else {
                warningMessage += "- \"" + data.reported_tag + "\" will be removed from this item's whitelisted tags.\n";
            }
        }

        warningMessage += "Continue?";
        if (showWarning) {
            const confirmed = confirm(warningMessage);
            if (confirmed) {
                document.querySelector("#report_form").submit();
            }
        } else {
            document.querySelector("#report_form").submit();
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    originalDecision = document.getElementById('id_decision').value;

    const saveButton = document.querySelector('input[name="_save"]');
    const saveAddAnotherButton = document.querySelector('input[name="_addanother"]');
    const saveContinueButton = document.querySelector('input[name="_continue"]');

    saveButton.addEventListener('click', validateDecision);
    saveAddAnotherButton.addEventListener('click', validateDecision);
    saveContinueButton.addEventListener('click', validateDecision);
});
