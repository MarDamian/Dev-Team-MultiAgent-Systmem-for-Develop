import { addMessage, selectors, showLoading, hideLoading } from './ui.js';
import { getSelectedFiles, clearSelectedFiles } from './fileHandler.js';
import { chat_history, addToHistory } from './chatState.js';

let isThinking = false;

async function uploadFiles(files) {
    if (files.length === 0) return [];
    const formData = new FormData();
    files.forEach(file => formData.append("files", file));
    try {
        const response = await fetch("/upload", { method: "POST", body: formData });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "Error al subir archivos.");
        return result.filenames;
    } catch (error) {
        addMessage(`<i>Error de red al subir: ${error.message}</i>`, 'agent-status');
        return null;
    }
}

export function initFormHandler(socket) {
    const messageForm = document.getElementById("message-form");

    messageForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = selectors.messageInput.value;
        if ((!message.trim() && getSelectedFiles().length === 0) || isThinking) return;

        const files = getSelectedFiles();
        let displayMessage = message;

        if (files.length > 0) {
            displayMessage += '<div class="chat-media-container">';
            files.forEach(file => {
                const fileUrl = URL.createObjectURL(file);
                const fileType = file.type || "";
                const fileName = file.name.toLowerCase();

                if (fileType.startsWith('image/') || /\.(jpg|jpeg|png|gif|webp)$/i.test(fileName)) {
                    displayMessage += `<img src="${fileUrl}" class="chat-image-preview" alt="${file.name}">`;
                } else if (fileType.startsWith('audio/') || /\.(mp3|wav|ogg)$/i.test(fileName)) {
                    displayMessage += `<audio controls src="${fileUrl}" class="chat-audio-preview"></audio>`;
                } else if (fileType.startsWith('video/') || /\.(mp4|webm|ogg)$/i.test(fileName)) {
                    displayMessage += `<video controls src="${fileUrl}" class="chat-video-preview"></video>`;
                } else {
                    displayMessage += `<div class="file-attachment-tag">📎 ${file.name}</div>`;
                }
            });
            displayMessage += '</div>';
        }

        addMessage(displayMessage, "user");
        addToHistory("Usuario", message);

        // Clear files immediately from UI
        clearSelectedFiles();

        selectors.messageInput.value = "";
        selectors.messageInput.disabled = true;
        isThinking = true;
        showLoading();

        const uploadedFileNames = await uploadFiles(files);

        if (uploadedFileNames === null) {
            isThinking = false;
            hideLoading();
            selectors.messageInput.disabled = false;
            return;
        }

        const payload = {
            user_input: message,
            file_names: uploadedFileNames,
            chat_history: chat_history
        };
        console.log("Enviando payload con historial al WebSocket:", payload);
        socket.send(JSON.stringify(payload));
    });

    return {
        onDone: () => {
            isThinking = false;
            hideLoading();
            selectors.messageInput.disabled = false;
            selectors.messageInput.focus();
        }
    };
}