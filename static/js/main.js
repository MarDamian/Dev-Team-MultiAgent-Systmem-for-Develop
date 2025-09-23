// Contenido final para: static/js/main.js

import { initTheme } from './modules/theme.js';
import { initFileHandler } from './modules/fileHandler.js';
import { initWebSocket } from './modules/websocketHandler.js';
import { initFormHandler } from './modules/formHandler.js';

// Este evento asegura que todo el HTML está listo antes de ejecutar el script.
document.addEventListener("DOMContentLoaded", () => {
    
    // Paso de depuración: Abre la consola del navegador (F12) y busca este mensaje.
    // Si no aparece, hay un problema fundamental con la carga del script.
    console.log("DOM cargado. Inicializando aplicación...");

    // 1. Inicializa los módulos que no dependen de otros.
    initTheme();
    initFileHandler();

    // 2. Prepara un objeto para que los módulos se comuniquen entre sí.
    //    Esto nos permite manejar callbacks de forma limpia.
    const appCallbacks = {};

    // 3. Inicializa la conexión WebSocket. Le pasamos el objeto de callbacks
    //    para que pueda llamar a funciones que se definirán más tarde (como onDone).
    const socket = initWebSocket({
        onDone: () => {
            // Cuando el WebSocket reciba un evento 'done', llamará a esta función.
            // Esta, a su vez, llamará a la función que el formHandler nos haya dado.
            if (appCallbacks.onDone) {
                appCallbacks.onDone();
            }
        }
    });

    // 4. Inicializa el manejador del formulario. Necesita el objeto 'socket' para enviar mensajes.
    //    A su vez, nos devuelve las funciones que otros módulos (como el WebSocket) necesitan llamar.
    const formHandler = initFormHandler(socket);
    
    // 5. Guardamos la función onDone del formHandler en nuestro objeto de callbacks
    //    para que el WebSocket pueda encontrarla y llamarla.
    appCallbacks.onDone = formHandler.onDone;
});