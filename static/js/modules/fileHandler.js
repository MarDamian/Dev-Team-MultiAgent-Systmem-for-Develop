import { selectors } from './ui.js';

let selectedFiles = [];

export function getSelectedFiles() {
    return selectedFiles;
}

export function clearSelectedFiles() {
    selectedFiles = [];
    document.getElementById("file-input").value = '';
    updateFileList();
}

export function initFileHandler() {
    const uploadButton = document.getElementById("upload-button");
    const fileInput = document.getElementById("file-input");

    uploadButton.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
        selectedFiles = Array.from(fileInput.files);
        updateFileList();
    });

    selectors.fileListDiv.addEventListener("click", (event) => {
        if (event.target.classList.contains("remove-file")) {
            const index = parseInt(event.target.dataset.index, 10);
            selectedFiles.splice(index, 1);
            updateFileList();
        }
    });
}

function updateFileList() {
    selectors.fileListDiv.innerHTML = "";
    if (selectedFiles.length > 0) {
        selectors.fileListDiv.innerHTML = "<strong>Archivos adjuntos:</strong> ";
        selectedFiles.forEach((file, index) => {
            const fileTag = document.createElement("span");
            fileTag.classList.add("file-tag");
            fileTag.innerHTML = `${file.name} <span class="remove-file" data-index="${index}">x</span>`;
            selectors.fileListDiv.appendChild(fileTag);
        });
    }
}