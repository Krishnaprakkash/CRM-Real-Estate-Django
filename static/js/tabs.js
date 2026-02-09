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