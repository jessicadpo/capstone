function validateDecision(event) {
    if (window.identicalReports) {
        const currentDecision = document.getElementById('id_decision').value;

        let conflictingPrevReport = window.identicalReports.find(report => report.decision !== currentDecision);

        if (conflictingPrevReport) {
            // Show warning popup message (ask for confirmation)
            const confirmed = confirm("WARNING: Decision \"" + conflictingPrevReport.decision + "\" has already been " +
                                    "made for the same tag and item in a previous report (report_id=" + conflictingPrevReport.report_id + "). " +
                                    "Are you sure you want to override this decision?");

            if (!confirmed) { // Prevent save if admin user cancels
                event.preventDefault();
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const saveButton = document.querySelector('input[name="_save"]');
    const saveAddAnotherButton = document.querySelector('input[name="_addanother"]');
    const saveContinueButton = document.querySelector('input[name="_continue"]');

    saveButton.addEventListener('click', validateDecision);
    saveAddAnotherButton.addEventListener('click', validateDecision);
    saveContinueButton.addEventListener('click', validateDecision);
});
