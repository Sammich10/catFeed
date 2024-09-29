document.addEventListener('DOMContentLoaded', async function() {
    // Define defaults
    const default_tab = '.tabLoginNav';
    const default_tab_content = '.tabLoginContent';
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
                }, timeValue);
            }, timeValue);
        });
    }
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
});
