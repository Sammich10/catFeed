var base_url = window.location.origin;

// DOM is fully loaded and parsed. Execute functions to initialize DOM elements
document.addEventListener('DOMContentLoaded', function() {
    initializeIndexPage();
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

function initializeIndexPage() {
    // Get the tab navigation and content elements
    const tabNav = document.querySelector('.tab-nav-link');
    // Add event listener to the tab navigation
    tabNav.addEventListener('click', (e) => {
        // Get the target tab
        const targetTab = e.target.getAttribute('href');
        const allTabsContent = document.querySelectorAll('.tab-content');
        const allTabs = document.querySelectorAll('.tab-nav');
        // Remove the active class from all tab panes
        allTabsContent.forEach((allTabsContent) => {
            allTabsContent.classList.remove('active');
        });
        allTabs.forEach((allTabs) => {
            allTabs.classList.remove('active');
        })
        console.log("targetTab: " + targetTab);
        // Add the active class to the target tab pane
        const targetTabPane = document.querySelectorAll(targetTab);
        if(targetTabPane == null){
            console.log("Target tab " + targetTab + " not found")
            return
        }
        targetTabPane[0].classList.add('active');
        // Set the parent container of the link (tab nav) to active
        tabNav.parentElement.classList.add('active');
    });
    // Remove the active class from all tab navs
    for (let i = 0; i < tabNav.length; i++) {
        tabNav[i].classList.remove('active');
    }
    for (let i = 0; i < tabContent.length; i++) {
        tabContent[i].classList.remove('active');
    }
    // Add the active class to the first tab
    tabNav1 = document.querySelector('.tabStatusNav');
    tabContent1 = document.querySelector('.tabStatusContent');
    tabNav1.classList.add('active');
    tabContent1.classList.add('active');
}