document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    const contentSections = document.querySelectorAll('.content-section');
    const searchInput = document.getElementById('search-input');
    const newButton = document.getElementById('new-button');
    const newDropdown = document.getElementById('new-dropdown');
    const computersAlertBanner = document.getElementById('computers-alert-banner');
    const closeAlertButton = computersAlertBanner ? computersAlertBanner.querySelector('.close-alert-button') : null;

    // Function to update content based on navigation
    function updateContent(contentId) {
        // Deactivate all content sections
        contentSections.forEach(section => {
            section.classList.remove('active');
        });

        // Activate the selected content section
        const targetContent = document.getElementById(`${contentId}-content`);
        if (targetContent) {
            targetContent.classList.add('active');
        }

        // Update search input placeholder
        let placeholderText = "Buscar en Drive";
        switch (contentId) {
            case 'home':
                placeholderText = "Buscar en Drive";
                break;
            case 'my-drive':
                placeholderText = "Buscar en Mi unidad";
                break;
            case 'computers':
                placeholderText = "Buscar en Ordenadores";
                break;
            case 'shared-with-me':
                placeholderText = "Buscar en Compartido conmigo";
                break;
            case 'recent':
                placeholderText = "Buscar en Reciente";
                break;
            case 'starred':
                placeholderText = "Buscar en Destacados";
                break;
            case 'trash':
                placeholderText = "Buscar en Papelera";
                break;
        }
        searchInput.placeholder = placeholderText;
    }

    // Navigation links click handler
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent default link behavior
            
            // Remove 'active' class from all nav links
            navLinks.forEach(nav => nav.classList.remove('active'));
            
            // Add 'active' class to the clicked link
            link.classList.add('active');
            
            // Update the main content area
            updateContent(link.dataset.content);
        });
    });

    // "Nuevo" button dropdown toggle
    if (newButton && newDropdown) {
        newButton.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent document click from closing immediately
            newDropdown.classList.toggle('show');
            newButton.classList.toggle('active'); // Add active state to button
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!newButton.contains(e.target) && !newDropdown.contains(e.target)) {
                newDropdown.classList.remove('show');
                newButton.classList.remove('active'); // Remove active state from button
            }
        });
    }

    // Alert Banner close functionality
    if (closeAlertButton && computersAlertBanner) {
        closeAlertButton.addEventListener('click', () => {
            computersAlertBanner.style.display = 'none';
        });
    }

    // Initial content load (Página principal)
    // This ensures 'home' content is displayed and its nav link is active on page load.
    const initialActiveLink = document.querySelector('.nav-link.active');
    if (initialActiveLink) {
        updateContent(initialActiveLink.dataset.content);
    } else {
        // Fallback if no link has 'active' class initially
        updateContent('home');
    }
});