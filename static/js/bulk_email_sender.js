// bulk_email_sender.js
document.addEventListener("DOMContentLoaded", function () {
    var emailOption = document.getElementById("email_option");
    var commaSeparatedGroup = document.getElementById("comma_separated_group");
    var csvFileGroup = document.getElementById("csv_file_group");

    function toggleEmailOption() {
        if (emailOption.value === "comma_separated") {
            commaSeparatedGroup.style.display = "block";
            csvFileGroup.style.display = "none";
        } else if (emailOption.value === "csv_file") {
            commaSeparatedGroup.style.display = "none";
            csvFileGroup.style.display = "block";
        }
    }

    toggleEmailOption();
    emailOption.addEventListener("change", toggleEmailOption);
});
