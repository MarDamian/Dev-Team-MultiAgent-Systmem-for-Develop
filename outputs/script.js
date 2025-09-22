document.addEventListener('DOMContentLoaded', () => {
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const mainNav = document.querySelector('.main-nav');

    // Toggle mobile navigation
    hamburgerMenu.addEventListener('click', () => {
        document.body.classList.toggle('nav-open');
    });

    // Dropdown menu functionality
    const dropdowns = document.querySelectorAll('.has-dropdown');

    dropdowns.forEach(dropdown => {
        const dropdownToggle = dropdown.querySelector('a');
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');

        // Toggle dropdown on click
        dropdownToggle.addEventListener('click', (e) => {
            // Check if we are in a mobile view where the main nav is stacked
            // This check ensures default link behavior is prevented only when the nav is in mobile mode
            const isMobileNavOpen = document.body.classList.contains('nav-open');
            const isSmallScreen = window.innerWidth <= 992; // Use breakpoint defined in CSS

            if (isMobileNavOpen || isSmallScreen) {
                e.preventDefault(); // Prevent default link behavior for dropdowns in mobile/small screen
                
                // Close other open dropdowns
                dropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown && otherDropdown.classList.contains('active')) {
                        otherDropdown.classList.remove('active');
                    }
                });
                dropdown.classList.toggle('active');
            }
            // For desktop, hover CSS handles dropdowns, and direct links should navigate.
            // If a dropdown parent link has no href, preventDefault is always fine.
        });

        // Close dropdown if clicked outside
        document.addEventListener('click', (e) => {
            // Only close if not clicking on the dropdown itself or its toggle
            if (!dropdown.contains(e.target) && dropdown.classList.contains('active')) {
                dropdown.classList.remove('active');
            }
        });
    });

    // Segmented control functionality
    const segmentedControlOptions = document.querySelectorAll('.segmented-control__option');

    segmentedControlOptions.forEach(option => {
        option.addEventListener('click', () => {
            // Remove 'active' class from all options
            segmentedControlOptions.forEach(opt => opt.classList.remove('active'));
            // Add 'active' class to the clicked option
            option.classList.add('active');
            // In a real application, you would update content here based on data-tab attribute
            // const tabId = option.dataset.tab;
            // updateContent(tabId);
        });
    });
});