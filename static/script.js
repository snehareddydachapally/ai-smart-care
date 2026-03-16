document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("disclaimerModal");

    // show disclaimer
    modal.style.display = "block";

    // auto close after 4 seconds
    setTimeout(function(){

        modal.style.display = "none";

        // redirect to home page
        window.location.href = "/";

    },4000);

});