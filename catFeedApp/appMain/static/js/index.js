var base_url = window.location.origin;

function getReading(){
    const url = base_url + "/api/readDistance"
    fetch(url)
    .then(response=> response.json())
    .then(json => {
        var tstring = json[0]
        document.getElementById("foodremaining").innerHTML = tstring
    })
}