var base_url = window.location.origin;

// DOM is fully loaded and parsed. Execute functions to initialize DOM elements
document.addEventListener('DOMContentLoaded', function() {
    getReading();
});

function getReading(){
    const url = base_url + "/api/getDistance"
    fetch(url)
    .then(response=> response.json())
    .then(json => {
        var tstring = json[0]
        console.log(json)
        console.log(tstring)
        text = document.getElementById("foodremaining").innerHTML;
        // find the colon at the end of the string
        colon = text.indexOf(":");
        // append the reading to the string
        text = text.substring(0,colon) +" " + tstring;
        document.getElementById("foodremaining").innerHTML = text;
    })
}