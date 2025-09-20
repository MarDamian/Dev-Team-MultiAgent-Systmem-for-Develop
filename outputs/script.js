document.addEventListener('DOMContentLoaded', () => {
    // Hamburger Menu Toggle
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const mainNav = document.querySelector('.main-nav');

    // Create an overlay div for when the mobile menu is open
    const navOverlay = document.createElement('div');
    navOverlay.classList.add('main-nav-overlay');
    document.body.appendChild(navOverlay);

    hamburgerMenu.addEventListener('click', () => {
        mainNav.classList.toggle('active');
        navOverlay.classList.toggle('active');
        // Toggle body scroll to prevent scrolling when menu is open
        document.body.classList.toggle('no-scroll');
    });

    // Close menu when clicking outside (on overlay)
    navOverlay.addEventListener('click', () => {
        mainNav.classList.remove('active');
        navOverlay.classList.remove('active');
        document.body.classList.remove('no-scroll');
    });

    // Close menu when a navigation link or the mobile CTA button is clicked
    mainNav.querySelectorAll('a, .cta-button.mobile-only').forEach(item => {
        item.addEventListener('click', () => {
            if (mainNav.classList.contains('active')) {
                mainNav.classList.remove('active');
                navOverlay.classList.remove('active');
                document.body.classList.remove('no-scroll');
            }
        });
    });

    // Tab Control
    const tabItems = document.querySelectorAll('.tab-item');
    tabItems.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove 'active' class from all tabs
            tabItems.forEach(item => item.classList.remove('active'));
            // Add 'active' class to the clicked tab
            tab.classList.add('active');
            // In a real application, you would also update the content based on the clicked tab's data-tab attribute
            // const tabContentId = tab.dataset.tab;
            // console.log(`Switching to tab: ${tabContentId}`);
        });
    });
});