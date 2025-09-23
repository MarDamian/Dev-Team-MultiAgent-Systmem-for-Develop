// Contenido para: static/js/modules/chatState.js

// Este módulo simple mantiene el estado de la conversación en el frontend.
export let chat_history = [];

/**
 * Inicializa el historial con el saludo del bot.
 * Se llama una vez cuando la aplicación se carga.
 */
export function initializeHistory() {
    // Asegurarse de que el historial esté vacío antes de inicializar
    if (chat_history.length === 0) {
        const initialBotMessage = "¡Hola! Soy DevTeam-Bot. ¿En qué puedo ayudarte hoy?";
        chat_history.push(`Bot: ${initialBotMessage}`);
    }
}

/**
 * Añade una nueva entrada al historial de la conversación.
 * @param {string} role - 'Usuario' o 'Bot'.
 * @param {string} message - El contenido del mensaje.
 */
export function addToHistory(role, message) {
    // Evitar añadir mensajes de estado o vacíos al historial conversacional
    if (message && message.trim().length > 0) {
        chat_history.push(`${role}: ${message}`);
    }
}