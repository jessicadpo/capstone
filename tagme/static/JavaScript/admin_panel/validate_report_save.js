var originalDecision;
var reportedItemID;

function stringToBoolean(string) {
    // Convert strings to boolean (because Python true is "True" not "true")
    return (string === "True");
}

function getMostRecentPrevReport(decisionToFind) {
    // Returns null if no report found
    if (decisionToFind === "global") {
        return window.otherTagReports.find(report => report.decision.includes(decisionToFind)) || null;
    }
    else if (decisionToFind === "item") {
        return window.otherTagReports.find(report => report.decision.includes(decisionToFind) && report.item_id === reportedItemID) || null;
    }
    else if (decisionToFind == "item_whitelist" || decisionToFind == "item_blacklist") {
        return window.otherTagReports.find(report => report.decision === decisionToFind && report.item_id === reportedItemID) || null;
    }
    // If decisionToFind === "global_blacklist" or "global_whitelist"
    return window.otherTagReports.find(report => report.decision === decisionToFind) || null;
}

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
                warningMessage += "- \"" + data.reported_tag + "\" will be moved to the global whitelist.\n";
            }
        }

        // If tag will be removed from global_whitelist by this new decision
        if (data.tag_changes.gw_changed && !data.new_tag.gw) {
            showWarning = true;
            warningMessage += "- \"" + data.reported_tag + "\" will be removed from the global whitelist.\n";
            if (data.new_tag.gb) {
                warningMessage += "- \"" + data.reported_tag + "\" will be moved to the global blacklist.\n";
            }
        }

        // If tag will be removed from item's blacklist
        if (data.tag_changes.ib_changed && !data.new_tag.ib) {
            showWarning = true;
            if (data.new_tag.iw) {
                warningMessage += "- \"" + data.reported_tag + "\" will be moved to this item's whitelisted tags.\n";
            } else {
                warningMessage += "- \"" + data.reported_tag + "\" will be removed from this item's blacklisted tags.\n";
            }
        }

        // If tag will be removed from item's whitelist
        if (data.tag_changes.iw_changed && !data.new_tag.iw) {
            showWarning = true;
            if (data.new_tag.ib) {
                warningMessage += "- \"" + data.reported_tag + "\" will be moved to this item's blacklisted tags.\n";
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

/*
function validateDecision(event) {
    const originalDecisionAction = originalDecision.includes("black") ? "black" : "white";

    const newDecision = document.getElementById('id_decision').value;
    if (newDecision === originalDecision) {
        return; // Do nothing if decision wasn't altered
    }

    // Convert strings to boolean
    var any_item_in_blacklist = stringToBoolean(window.reportedTag.has_any_item_in_blacklist);
    var any_item_in_whitelist = stringToBoolean(window.reportedTag.has_any_item_in_whitelist);
    var this_item_in_blacklist = stringToBoolean(window.reportedTag.has_item_in_item_blacklist);
    var this_item_in_whitelist = stringToBoolean(window.reportedTag.has_item_in_item_whitelist);
    var globally_blacklisted = stringToBoolean(window.reportedTag.global_blacklist);
    var globally_whitelisted = stringToBoolean(window.reportedTag.global_whitelist);

    // Check if need to show warning message && (if yes) what message should be
    var showWarning = false;
    var warningMessage = "WARNING:\n";

    switch(newDecision) {
        case "global_blacklist":
            if (any_item_in_whitelist) {
                showWarning = true;
                warningMessage += "- This tag was previously whitelisted for some items (see reports #x).\n"; // TODO: All relevant reports
            }
            if (globally_whitelisted) {
                showWarning = true;
                var prevReport = getMostRecentPrevReport("global_whitelist");
                warningMessage += "- This tag was previously whitelisted globally (see report #" + prevReport.report_id + ").\n";
            }
            break;
        case "item_blacklist":
            if (this_item_in_whitelist) {
                showWarning = true;
                var prevReport = getMostRecentPrevReport("item_whitelist");
                warningMessage += "- This tag was previously whitelisted for this item (see report #" + prevReport.report_id + ").\n";
            }
            if (globally_whitelisted) {
                showWarning = true;
                var prevReport = getMostRecentPrevReport("global_whitelist");
                warningMessage += "- This tag was previously whitelisted globally (see report #" + prevReport.report_id + ").\n";
            }
            break;
        case "global_whitelist":
            if (any_item_in_blacklist) {
                showWarning = true;
                warningMessage += "- This tag was previously blacklisted for some items (see reports #x).\n"; // TODO: All relevant reports
            }
            if (globally_blacklisted) {
                showWarning = true;
                var prevReport = getMostRecentPrevReport("global_blacklist");
                warningMessage += "- This tag was previously blacklisted globally (see report #" + prevReport.report_id + ").\n";
            }
            break;
        case "item_whitelist":
            if (this_item_in_blacklist) {
                showWarning = true;
                var prevReport = getMostRecentPrevReport("item_blacklist");
                warningMessage += "- This tag was previously blacklisted for this item (see report #" + prevReport.report_id + ").\n";
            }
            if (globally_blacklisted) {
                showWarning = true;
                var prevReport = getMostRecentPrevReport("global_blacklist");
                warningMessage += "- This tag was previously blacklisted globally (see report #" + prevReport.report_id + ").\n";
            }
            break;
        default: // Ignore report or null (---------)
            if (originalDecision === "ignore_report" || originalDecision === null) {
              return;
            }
    }

    if (originalDecision.includes("global") && !newDecision.includes("global")) {
        var prevReport = getMostRecentPrevReport("global");
        if (prevReport === null) { // If there's no other "global"-type decision for this tag
            showWarning = true;
            warningMessage += "- \"" + window.reportedTag.tag + "\" will be removed from the global " + originalDecisionAction + "list.\n";
        } else if (prevReport.decision != originalDecision) { // If the most recent "global"-type decision is different
            showWarning = true;
            var prevDecisionAction = prevReport.decision.includes("black") ? "black" : "white";
            warningMessage += "- \"" + window.reportedTag.tag + "\" will be moved to the global " + prevDecisionAction + "list.\n";
        }
    } else if (originalDecision.includes("item") && !newDecision.includes("item")) {
        var prevReport = getMostRecentPrevReport("item");
        if (prevReport === null) {
            showWarning = true;
            warningMessage += "- \"" + window.reportedTag.tag + "\" will be removed from this item's " + originalDecisionAction + "listed tags.\n";
        } else if (prevReport.decision != originalDecision) {
            showWarning = true;
            var prevDecisionAction = prevReport.decision.includes("black") ? "black" : "white";
            warningMessage += "- \"" + window.reportedTag.tag + "\" will be moved to this item's " + prevDecisionAction
                            + "listed tags (see report #" + prevReport.report_id + ").\n";
        }
    }

    warningMessage += "Are you sure you want to override this/these decision(s)?";

    // Show warning message
    if (showWarning) {
        const confirmed = confirm(warningMessage);
        if (!confirmed) { // Prevent save if admin user cancels
            event.preventDefault();
        }
    }
}
*/

document.addEventListener('DOMContentLoaded', function () {
    reportedItemID = document.getElementById('id_item_id').value;
    originalDecision = document.getElementById('id_decision').value;

    const saveButton = document.querySelector('input[name="_save"]');
    const saveAddAnotherButton = document.querySelector('input[name="_addanother"]');
    const saveContinueButton = document.querySelector('input[name="_continue"]');

    saveButton.addEventListener('click', validateDecision);
    saveAddAnotherButton.addEventListener('click', validateDecision);
    saveContinueButton.addEventListener('click', validateDecision);
});
