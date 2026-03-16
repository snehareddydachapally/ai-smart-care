document.addEventListener("DOMContentLoaded", function () {

const modal = document.getElementById("disclaimerModal");

if(modal){

modal.style.display = "block";

setTimeout(function(){

modal.style.display = "none";

},3000);

}

});