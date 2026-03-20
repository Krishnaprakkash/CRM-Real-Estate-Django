// ===== TAB SWITCHING FUNCTIONALITY =====

function switchTab(evt, tabName) {
    var i, tabcontent, tablinks, statsGroups;

    // Hide all tab content
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Hide all stats groups
    statsGroups = document.getElementsByClassName('stats-group');
    for (i = 0; i < statsGroups.length; i++) {
        statsGroups[i].style.display = 'none';
    }

    // Remove active class from all tab links
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }

    // Show selected tab content
    var contentElement = document.getElementById(tabName);
    if (contentElement && contentElement.classList.contains('tabcontent')) {
        contentElement.style.display = 'block';
    }

    // Show corresponding stats group (with 'stats-' prefix)
    var statsElement = document.getElementById('stats-' + tabName);
    if (statsElement && statsElement.classList.contains('stats-group')) {
        statsElement.style.display = 'flex';
    }

    evt.currentTarget.classList.add("active");
}

// Show first tab by default on page load
document.addEventListener('DOMContentLoaded', function () {
    const firstTab = document.querySelector('.tablinks');
    if (firstTab) {
        firstTab.click();
    }
});

// ===== LISTING DETAIL TAB COLORING =====
// Simple inline styling approach - direct DOM manipulation
document.addEventListener('DOMContentLoaded', function() {
    // Get all tab links
    const tabs = document.querySelectorAll('.stage-progress-nav .nav-link');
    
    if (tabs.length === 0) {
        console.log('No stage tabs found');
        return;
    }
    
    console.log('Found', tabs.length, 'tabs');
    
    // Simple stage detection based on existing active tab
    let currentTabIndex = -1;
    
    // Find which tab is currently active (has the active class)
    tabs.forEach((tab, index) => {
        if (tab.classList.contains('active')) {
            currentTabIndex = index;
            console.log('Found active tab at index:', index, tab.textContent.trim());
        }
    });
    
    // If no active tab found, default to first tab
    if (currentTabIndex === -1) {
        currentTabIndex = 0;
        console.log('No active tab found, defaulting to first tab');
    }
    
    // Apply colors to each tab
    tabs.forEach((tab, index) => {
        if (index < currentTabIndex) {
            // Completed stages - Green
            tab.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
            tab.style.color = 'white';
            tab.style.borderColor = '#28a745';
        } else if (index === currentTabIndex) {
            // Current stage - Yellow
            tab.style.background = 'linear-gradient(135deg, #ffc107 0%, #ff9800 100%)';
            tab.style.color = '#000';
            tab.style.borderColor = '#ffc107';
        } else {
            // Future stages - White
            tab.style.background = 'white';
            tab.style.color = '#6c757d';
            tab.style.borderColor = '#dee2e6';
        }
        
        // Add hover effects
        tab.addEventListener('mouseenter', function() {
            if (index === currentTabIndex) {
                tab.style.transform = 'translateY(-2px)';
                tab.style.boxShadow = '0 5px 15px rgba(255, 193, 7, 0.3)';
            } else if (index > currentTabIndex) {
                tab.style.background = '#f8f9fa';
                tab.style.color = '#1e3c72';
                tab.style.borderColor = '#1e3c72';
                tab.style.transform = 'translateY(-2px)';
            }
        });
        
        tab.addEventListener('mouseleave', function() {
            // Reset to base style
            if (index < currentTabIndex) {
                tab.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                tab.style.color = 'white';
                tab.style.borderColor = '#28a745';
            } else if (index === currentTabIndex) {
                tab.style.background = 'linear-gradient(135deg, #ffc107 0%, #ff9800 100%)';
                tab.style.color = '#000';
                tab.style.borderColor = '#ffc107';
            } else {
                tab.style.background = 'white';
                tab.style.color = '#6c757d';
                tab.style.borderColor = '#dee2e6';
            }
            tab.style.transform = 'translateY(0)';
            tab.style.boxShadow = 'none';
        });
    });
});
