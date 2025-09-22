document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');

    const resizeHandleClasses = [
        'top-left', 'top-center', 'top-right',
        'middle-left', 'middle-right',
        'bottom-left', 'bottom-center', 'bottom-right'
    ];

    function createResizeHandles(cardElement) {
        resizeHandleClasses.forEach(className => {
            const handle = document.createElement('div');
            handle.classList.add('resize-handle', className);
            cardElement.appendChild(handle);
        });
    }

    function removeResizeHandles(cardElement) {
        const handles = cardElement.querySelectorAll('.resize-handle');
        handles.forEach(handle => handle.remove());
    }

    cards.forEach(card => {
        // Initialize selected cards with handles if they have the 'selected' class
        if (card.classList.contains('selected')) {
            createResizeHandles(card);
        }

        card.addEventListener('click', (event) => {
            // Prevent toggling if click originated from action button or resize handle
            if (event.target.closest('.action-button') || event.target.closest('.resize-handle')) {
                return;
            }

            card.classList.toggle('selected');

            if (card.classList.contains('selected')) {
                createResizeHandles(card);
            } else {
                removeResizeHandles(card);
            }
        });
    });

    // Optional: Add basic drag functionality for annotations
    const annotations = document.querySelectorAll('.annotation');
    annotations.forEach(annotation => {
        let isDragging = false;
        let offsetX, offsetY;

        annotation.addEventListener('mousedown', (e) => {
            isDragging = true;
            offsetX = e.clientX - annotation.getBoundingClientRect().left;
            offsetY = e.clientY - annotation.getBoundingClientRect().top;
            annotation.style.cursor = 'grabbing';
            annotation.style.zIndex = '100'; // Bring to front
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            // Ensure annotation stays within canvas boundaries (optional, for more robust drag)
            const canvas = annotation.closest('.canvas');
            const canvasRect = canvas.getBoundingClientRect();
            const annotationRect = annotation.getBoundingClientRect();

            let newLeft = e.clientX - offsetX;
            let newTop = e.clientY - offsetY;

            // Clamp left
            newLeft = Math.max(canvasRect.left, newLeft);
            newLeft = Math.min(canvasRect.right - annotationRect.width, newLeft);
            // Clamp top
            newTop = Math.max(canvasRect.top, newTop);
            newTop = Math.min(canvasRect.bottom - annotationRect.height, newTop);

            annotation.style.left = `${newLeft - canvasRect.left}px`;
            annotation.style.top = `${newTop - canvasRect.top}px`;
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
            annotation.style.cursor = 'grab';
            annotation.style.zIndex = '5'; // Reset z-index
        });

        annotation.style.cursor = 'grab'; // Set initial cursor
    });
});