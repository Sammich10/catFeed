var base_url = window.location.origin;
const default_tab = '.tabStatusNav';
const default_tab_content = '.tabStatusContent';
const feed_timeout = 5000;


// DOM is fully loaded and parsed. Execute functions to initialize DOM elements
document.addEventListener('DOMContentLoaded', async function() {
    initializeIndexPage();
    const reading = await getReading();
    updateFoodRemaining(reading);
    const last_feed = await getLastFeed();
    if (last_feed == ""){
        updateLastFeed("N/A");
    }else{
        updateLastFeed(convertTime(last_feed[0]) + " " + last_feed[1]);
    }
    // update slider value based on the default slider value
    const feed_slider_value = document.getElementById("feed-slider").value;
    document.getElementById("feed-size-text").innerHTML = sizeNumToString(parseInt(feed_slider_value));
});

/**
 * getReading() - Fetches the current food level from the server
 * and returns it as a string in 24hr format (HH:MM)
 * @return {string} The current food level
 */
async function getReading(){
    const url = base_url + "/api/getDistance"
    const response = await fetch(url)
    const json = await response.json()
    var tstring = json['distance'];
    console.log("Updating food remaining: " + tstring + "%");
    return tstring;
}

/**
 * getLastFeed() - Fetches the last feed time from the server
 * and returns it as a string in 24hr format (HH:MM)
 * @return {string} The last feed time
 */
async function getLastFeed(){
    const url = base_url + "/api/getLastFeed"
    const response = await fetch(url)
    const json = await response.json()
    var last_feed = json['last_feed'];
    console.log("Updating last feed: " + last_feed);
    return last_feed;
}

/**
 * Fetches the scheduled feed times from the server and returns them as a JSON object.
 * @return {Promise<Object>} A JSON object containing the scheduled feed times.
 */
async function getFeedTimes()
{
    const url = base_url + "/api/getFeedTimes"
    const response = await fetch(url)
    const json = await response.json()
    var times = json['feed_times'];
    return times;
}

/**
 * Updates the food remaining display on the page with the given reading.
 * @param {String} reading The string representation of the food remaining, as a percentage.
 */
function updateFoodRemaining(reading){
    var tstring = reading;
    text = document.getElementById("foodremainingpercent").innerHTML = " " + tstring + "%";
    var percent = parseInt(tstring);
    updateGradient(percent);
}

/**
 * Updates the gradient effect on the food remaining status bar with the given percentage.
 * @param {Number} percent The percentage of food remaining.
 */
function updateGradient(percent) {
    const gradientElement = document.getElementById('status-food-remaining');
    gradientElement.style.setProperty('--percent', `${percent}%`);
}

/**
 * Updates the last feed time display on the page with the given reading.
 * @param {String} reading The string representation of the last feed time.
 */
function updateLastFeed(reading){
    var tstring = reading;
    text = document.getElementById("last-feed-time").innerHTML = tstring;
}

/**
 * Fetches the feed logs from the server and returns them as a JSON object.
 * @return {Promise<Object>} A JSON object containing the feed logs.
 */
async function getFeedLogs()
{
    const url = base_url + "/api/getFeedingTimes"
    const response = await fetch(url)
    const json = await response.json()
    return json
}

/**
 * Initialize the index page by adding event listeners to the tab navigation and
 * loading the default tab.
 */
function initializeIndexPage() {
    // Get the tab navigation and content elements
    const tabNav = document.querySelectorAll('.tab-nav-link');
    const tabContent = document.querySelectorAll('.tab-content');
    // Add event listener to the tab navigation
    for (let i = 0; i < tabNav.length; i++) {
        // Add event listener to the tab navigation
        tabNav[i].addEventListener('click', (e) => {
            // Get a list of all the tab navigation elements
            const allTabs = document.querySelectorAll('.tab-nav');
            // Remove the active class from all tab navigation elements
            allTabs.forEach((allTabs) => {
                allTabs.classList.remove('active');
            })
            // Set the parent container of the link (tab nav) to active immediately
            tabNav[i].parentElement.classList.add('active');
            // Get the target tab
            const targetTab = e.target.getAttribute('href');
            console.log("targetTab: " + targetTab);
            // Verify that the target tab exists in the document
            const targetTabPane = document.querySelector(targetTab);
            if(targetTabPane == null){
                console.log("Target tab " + targetTab + " not found")
                return
            }
            // Get the current active tab
            const activeTab = document.querySelector(".tab-content.active");
            if(activeTab == null){
                console.log("activeTab is null")
                return
            }else if(activeTab == targetTabPane){
                console.log("activeTab == targetTabPane")
                return
            }
            // Start the tab transition animation for the active tab to disappear
            activeTab.classList.remove('active');
            activeTab.classList.add('hidden');
            // Get the tab transition animation time
            const tabTransitionTime = getComputedStyle(activeTab).getPropertyValue('--tab-transition_time');
            const timeValue = parseFloat(tabTransitionTime.replace("s", "")) * 1000;
            // Show the target tab pane
            setTimeout(() => {
                // Remove the display: none from the target tab pane to reveal it in the document
                targetTabPane.style.removeProperty('display');
                // Hide the active tab pane in the document
                activeTab.style.display = 'none';
                setTimeout(() => {
                    // Add the active class to the target tab pane
                    targetTabPane.classList.add('active');
                    // Remove the hidden class from the target tab pane to start the animation
                    targetTabPane.classList.remove('hidden');
                    loadPaneContent(targetTabPane);
                }, timeValue);
            }, timeValue);
        });
    }
    /**
     * Loads the content of the pane based on the pane being loaded
     * @param {HTMLElement} targetTabPane - The target tab pane element
     */
    function loadPaneContent(targetTabPane) {
        // Based on the pane being loaded, load the content of the pane
        switch (targetTabPane.id) {
            case "tabSchedule":
                displayFeedTimes();
                break;
            case "tabLogs":
                displayFeedLogs();
                break;
        }
    }
    // Add event listener to the feed slider on the feeder status tab
    const feed_slider = document.getElementById("feed-slider");
    feed_slider.addEventListener('input', (e) => {
        // Update the feed size text when the slider is changed
        const feedSizeText = document.getElementById("feed-size-text");
        const sliderSetting = e.target.value;
        switch(sliderSetting){
            case "1":
                feedSizeText.innerHTML = "Very Small";
                break;
            case "2":
                feedSizeText.innerHTML = "Small";
                break;
            case "3":
                feedSizeText.innerHTML = "Average";
                break;
            case "4":
                feedSizeText.innerHTML = "Large";
                break;
            case "5":
                feedSizeText.innerHTML = "Very Large";
                break;
        }
    })

    // Remove the active class from all tab navs
    for (let i = 0; i < tabNav.length; i++) {
        tabNav[i].classList.remove('active');
    }
    for (let i = 0; i < tabContent.length; i++) {
        tabContent[i].classList.add('hidden');
        tabContent[i].style.display = 'none';
    }
    // Enable and display the default tab
    const defaultTab = document.querySelector(default_tab);
    const defaultTabContent = document.querySelector(default_tab_content);
    defaultTab.classList.add('active');
    defaultTabContent.classList.remove('hidden');
    defaultTabContent.classList.add('active');
    defaultTabContent.style.removeProperty('display');
}

/**
 * Updates the food remaining status bar.
 * 
 * This function is called when the user clicks on the "Update" button in the feeder status section.
 * It makes the button unclickable, reduces the opacity, and updates the text to "Updating..."
 * It then calls getReading() to get the current reading from the feeder, and updates the food remaining text with the new reading.
 * After the update, it enables the button and sets the opacity back to 1.
 */
async function updateReading()
{
    // Get the clickable div by ID
    const statusBar = document.getElementById("status-food-remaining");
    const statusBarText = document.getElementById("foodremaining");
    document.getElementById("foodremainingpercent").innerHTML = "";
    // Make the div unclickable
    statusBar.classList.add('disabled');
    // Reduce the opacity
    statusBar.style.opacity = "0.8";
    // Update the text
    statusBarText.innerHTML = "Updating...";
    updateGradient(100);
    const transitionTime = getComputedStyle(statusBar).getPropertyValue('--update-reading-transition_time');
    const timeValue = parseFloat(transitionTime.replace("s", "")) * 1000;
    setTimeout(async () => {
        // Enable the button
        statusBar.classList.remove('disabled');
        statusBar.style.opacity = "1";
        statusBarText.innerHTML = "Food remaining:";
        const reading = await getReading();
        updateFoodRemaining(reading);
    },timeValue);
}

/**
 * Trigger a manual feed.
 * 
 * This function is called when the user clicks on the "Feed" button in the feeder status section.
 * It makes the button unclickable, reduces the opacity, and updates the text to "Feeding..."
 * It then calls the /api/manualFeed endpoint with the slider value as the size of the feed.
 * If the response is successful (200), it waits for the feed timeout to pass, then
 * enables the button, sets the opacity back to 1, and updates the food remaining text.
 */
async function feed()
{
    // Get the button
    const feedButton = document.getElementById("feed-button");
    // Change the button text
    feedButton.innerHTML = "Feeding...";
    // Disable the button
    feedButton.classList.add('disabled');
    // Reduce the opacity
    feedButton.style.opacity = "0.8";
    const sliderSetting = parseInt(document.getElementById("feed-slider").value);
    const url = base_url + "/api/manualFeed"
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'size': sliderSetting
        })
    });
    if (response.status === 200) {
        setTimeout(() => {
            // Change the button text
            feedButton.innerHTML = "Feed";
            // Enable the button
            feedButton.classList.remove('disabled');
            // Reduce the opacity
            feedButton.style.opacity = "1";
            updateReading();
        }, feed_timeout);
    }
}

/**
 * This function is called when the user clicks on the "Fetch" button in the schedule feeds section.
 * It clears the schedule feeds list children, and then fetches the feed times from the server.
 * It then creates a list item for each feed time, with a button to remove the feed time.
 * When the button is clicked, it calls the removeTime function to delete the feed time, and then removes the list item from the schedule feeds list.
 */
async function displayFeedTimes()
{
    const scheduleFeedsList = document.getElementById("schedule-feeds-list");
    // Clear the schedule feeds list children
    while (scheduleFeedsList.firstChild) {
        scheduleFeedsList.removeChild(scheduleFeedsList.firstChild);
    }
    const feedTimes = await getFeedTimes();
    feedTimes.forEach((entry) => {
        const row = document.createElement('li');
        const timeCell = document.createElement('div');
        const typeCell = document.createElement('div');
        const sizeCell = document.createElement('div');
        const buttonCell = document.createElement('div');
        const button = document.createElement('button');
        // Convert the time from 24 hr to 12 hr format
        const time12hr = convertTime(entry[0]);
        timeCell.textContent = time12hr;
        const typeString = typeNumToString(entry[1]);
        typeCell.textContent = typeString;
        const sizeString = sizeNumToString(entry[2]);
        sizeCell.textContent = sizeString;
        button.classList.add('remove-feed-button');
        buttonCell.appendChild(button);
        row.appendChild(timeCell);
        row.appendChild(typeCell);
        row.appendChild(sizeCell);
        row.appendChild(buttonCell);
        scheduleFeedsList.appendChild(row);
        // add event listener to the button
        button.addEventListener('click', (e) => {
            removeTime(time, e);
            scheduleFeedsList.removeChild(row);
        });
  });

  /**
   * Sends a POST request to the server to delete a feed time. The request body
   * is a JSON object with a single key-value pair, where the key is "time" and
   * the value is the time of the feed to be deleted. If the response status is
   * 200, an alert box is displayed with a success message. Otherwise, an alert
   * box is displayed with an error message.
   * @param {string} time - the time of the feed to be deleted, in 24-hour format
   * @param {Element} el - the element that triggered the deletion
   */
  async function removeTime(time, el) {
    const url = base_url + "/api/deleteFeedTime"
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'time': time
        })
    });
    if (response.status === 200) {
        alert("Removed time: " + convertTime(time));
    }else{
        alert("Error: " + response.statusText);
    }
  }

}
/**
 * Converts a time in 24 hour format (HH:MM) to 12 hour format (HH:MM AM/PM)
 * @param {string} time - Time in 24 hour format
 * @returns {string} - Time in 12 hour format
 */
function convertTime(time) {
  const [hours, minutes] = time.split(':').map(Number);
  if (hours == null || minutes == null) {
    throw new Error('Invalid time format');
  }
  const ampm = hours < 12 ? 'AM' : 'PM';
  const newHours = hours % 12 === 0 ? 12 : hours % 12;
  return `${newHours}:${minutes.toString().padStart(2, '0')} ${ampm}`;
}

/**
 * Converts a type number to a string
 * @param {number} type - type number
 * @returns {string} - type string
 */
function typeNumToString(type) {
    switch (type) {
        case 0:
            return "Indefinite";
        case 1:
            return "One-Time";
        default:
            return "Unknown";
    }
}

/**
 * Converts a size number to a string
 * @param {number} size - Size number
 * @returns {string} - Size string
 */
function sizeNumToString(size) {
    switch (size) {
        case 1:
            return "X-Small";
        case 2:
            return "Small";
        case 3:
            return "Average";
        case 4:
            return "Large";
        case 5:
            return "X-Large";
        default:
            return "Unknown";
    }
}

/**
 * Populates the feed log table with the latest feed times.
 * @async
 * @function
 * @returns {Promise<void>}
 */
async function displayFeedLogs()
{
    const feedLogList = document.getElementById("feed-log-list");
    // Clear the schedule feeds list children
    while (feedLogList.firstChild) {
        feedLogList.removeChild(feedLogList.firstChild);
    }
    const feedLogs = await getFeedLogs();
    const entries = feedLogs['feeding_times'];
    console.log(feedLogs);
    for(let i = 0; i < entries.length; i++) {
        const row = document.createElement('li');
        const dateCell = document.createElement('div');
        dateCell.textContent = entries[i][0];
        const timeCell = document.createElement('div');
        timeCell.textContent = convertTime(entries[i][1]);
        const typeCell = document.createElement('div');
        typeCell.textContent = typeNumToString(entries[i][2]);
        const sizeCell = document.createElement('div');
        sizeCell.textContent = sizeNumToString(entries[i][3]);
        row.appendChild(timeCell);
        row.appendChild(dateCell);
        row.appendChild(typeCell);
        row.appendChild(sizeCell);
        feedLogList.prepend(row);
    }
}

/**
 * Sends a POST request to the server to add a feed time. The request body
 * is a JSON object with two key-value pairs, where the keys are "time" and
 * "type", and the values are the time of the feed to be added (in 24-hour
 * format) and the type of the feed (either "indefinite" or "onetime"),
 * respectively. If the response status is 200, the feed times list is
 * updated. Otherwise, an alert box is displayed with an error message.
 */
async function addFeedTime() {
    // get the time from the input
    const time = document.getElementById("schedule-feeds-time-input").value;
    const feedType = document.getElementById("feed-type").value;
    var type = 0;
    switch(feedType) {
        case "indefinite":
            type = 0;
            break;
        case "onetime":
            type = 1;
            break;
        default:
            alert("Error: Invalid feed type");
            return;
    }
    const feedSize = document.getElementById("feed-size").value;
    var size = 0;
    switch(feedSize) {
        case "1":
            size = 1;
            break;
        case "2":
            size = 2;
            break;
        case "3":
            size = 3;
            break;
        case "4":
            size = 4;
            break;
        case "5":
            size = 5;
            break;
        default:
            alert("Error: Invalid feed size");
            return;
    }
    const url = base_url + "/api/addFeedTime"
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'time': time,
            'type': type,
            'size': size
        })
    });
    if (response.status === 200) {
        displayFeedTimes();
    }else{
        alert("Error: " + response.statusText);
    }
}


  