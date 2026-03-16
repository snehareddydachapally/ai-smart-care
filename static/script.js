document.addEventListener("DOMContentLoaded", function () {

```
const modal = document.getElementById("disclaimerModal");
const checkbox = document.getElementById("agreeCheck");
const button = document.querySelector(".accept-btn");

// Hide popup if already accepted
if (localStorage.getItem("disclaimerAccepted") === "true") {
    if(modal){
        modal.style.display = "none";
    }
}

// Disable button initially
if(button){
    button.disabled = true;
}

// Enable button when checkbox checked
if(checkbox){
    checkbox.addEventListener("change", function () {
        button.disabled = !this.checked;
    });
}
```

});

// When user clicks I Understand
function closeDisclaimer() {

```
localStorage.setItem("disclaimerAccepted", "true");

const modal = document.getElementById("disclaimerModal");

if(modal){
    modal.style.display = "none";
}

// redirect to login page
window.location.href = "/login";
```

}

//////////////////////////
// VIDEO CONSULTATION JS
//////////////////////////

let localStream;

async function startCall(){

```
const status = document.getElementById("callStatus");

try{

    localStream = await navigator.mediaDevices.getUserMedia({
        video:true,
        audio:true
    });

    const localVideo = document.getElementById("localVideo");

    if(localVideo){
        localVideo.srcObject = localStream;
    }

    if(status){
        status.innerText = "Status: Call Started";
    }

}catch(error){

    alert("Camera access denied or not available.");

    console.error(error);

}
```

}

function endCall(){

```
const status = document.getElementById("callStatus");

if(localStream){

    localStream.getTracks().forEach(track => track.stop());

}

const localVideo = document.getElementById("localVideo");

if(localVideo){
    localVideo.srcObject = null;
}

if(status){
    status.innerText = "Status: Call Ended";
}
```

}
