document.addEventListener('DOMContentLoaded', () => {
    // Dropdown for "Nuevo" button
    const newButton = document.getElementById('newButton');
    const newDropdown = document.getElementById('newDropdown');

    newButton.addEventListener('click', (event) => {
        newDropdown.classList.toggle('show');
        event.stopPropagation(); // Prevent document click from closing immediately
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (event) => {
        if (!newDropdown.contains(event.target) && !newButton.contains(event.target)) {
            newDropdown.classList.remove('show');
        }
    });

    // Active state for navigation items
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (event) => {
            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));
            // Add active class to the clicked item
            item.classList.add('active');
            // Prevent default link behavior for demonstration
            event.preventDefault();
        });
    });

    // View toggle for files (Grid/List)
    const viewToggleButtons = document.querySelectorAll('.view-toggle-button');
    const filesContainer = document.getElementById('filesContainer');

    viewToggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all view buttons
            viewToggleButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to the clicked button
            button.classList.add('active');

            const viewType = button.dataset.view; // 'grid' or 'list'

            // Update files container class
            if (viewType === 'grid') {
                filesContainer.classList.remove('list-view');
                filesContainer.classList.add('grid-view');
            } else if (viewType === 'list') {
                filesContainer.classList.remove('grid-view');
                filesContainer.classList.add('list-view');
            }
        });
    });

    // Placeholder for dynamic content loading or interaction logic
    console.log("UI loaded and interactive elements initialized.");
});