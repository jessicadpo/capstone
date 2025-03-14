var originalDecision;
var reportedItemID;

function stringToBoolean(string) {
    // Convert strings to boolean (because Python true is "True" not "true")
    return (string === "True");
}

function getMostRecentPrevReport(decisionToFind) {
    if (decisionToFind == "item_whitelist" || decisionToFind == "item_blacklist") {
        return window.otherTagReports.find(report => report.decision === decisionToFind && report.item_id === reportedItemID);
    }
    return window.otherTagReports.find(report => report.decision === decisionToFind);
}

function validateDecision(event) {
    const newDecision = document.getElementById('id_decision').value;
    if (newDecision === originalDecision) {
        return; // Do nothing if decision wasn't altered
    }

    // Convert strings to boolean
    var any_item_in_blacklist = stringToBoolean(window.reportedTag.has_any_item_in_blacklist);
    var any_item_in_whitelist = stringToBoolean(window.reportTag.has_any_item_in_whitelist);
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
            } else {
                // TODO: Figure out if this new decision would change Tag's attributes


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
