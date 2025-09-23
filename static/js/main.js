// Contenido para: static/js/main.js

import { initTheme } from './modules/theme.js';
import { initFileHandler } from './modules/fileHandler.js';
import { initWebSocket } from './modules/websocketHandler.js';
import { initFormHandler } from './modules/formHandler.js';
import { initializeHistory } from './modules/chatState.js'; // <-- CAMBIO CLAVE: Importar el inicializador

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM cargado. Inicializando aplicación...");
    
    // <-- CAMBIO CLAVE: Inicializa el historial del chat al cargar la página
    initializeHistory();

    // 1. Configura funcionalidades que no dependen de otras
    initTheme();
    initFileHandler();

    // 2. Crea un objeto para manejar los callbacks entre módulos
    const appCallbacks = {};

    // 3. Inicializa el WebSocket y le pasamos el objeto de callbacks
    const socket = initWebSocket({
        onDone: () => {
            if (appCallbacks.onDone) {
                appCallbacks.onDone();
            }
        }
    });

    // 4. Inicializa el manejador del formulario, que necesita el socket.
    const formHandler = initFormHandler(socket);
    appCallbacks.onDone = formHandler.onDone;
});