// Contenido para: static/js/modules/formHandler.js

import { addMessage, selectors } from './ui.js';
import { getSelectedFiles, clearSelectedFiles } from './fileHandler.js';
// <-- CAMBIO CLAVE: Importar el estado del chat y la función para añadir al historial
import { chat_history, addToHistory } from './chatState.js';

let isThinking = false;

async function uploadFiles() {
    // ... (El código de esta función no cambia) ...
    const files = getSelectedFiles();
    if (files.length === 0) return [];
    const formData = new FormData();
    files.forEach(file => formData.append("files", file));
    try {
        const response = await fetch("/upload", { method: "POST", body: formData });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "Error al subir archivos.");
        addMessage(`<i>Archivos subidos: ${result.filenames.join(", ")}</i>`, 'agent-status');
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

        addMessage(message, "user");
        // <-- CAMBIO CLAVE: Actualiza el historial con el mensaje del usuario
        addToHistory("Usuario", message); 
        
        selectors.messageInput.value = "";
        selectors.messageInput.disabled = true;
        isThinking = true;
        addMessage("<i>DevTeam-Bot está pensando...</i>", 'agent-status');

        const uploadedFileNames = await uploadFiles();

        if (uploadedFileNames === null) {
            isThinking = false;
            selectors.messageInput.disabled = false;
            return;
        }
        
        // <-- CAMBIO CLAVE: El payload ahora incluye el historial completo
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
            selectors.messageInput.disabled = false;
            selectors.messageInput.focus();
            clearSelectedFiles();
        }
    };
}