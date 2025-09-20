document.addEventListener("DOMContentLoaded", () => {
    // --- Selectores de DOM y Estado de la Aplicación ---
    const chatBox = document.getElementById("chat-box");
    const messageForm = document.getElementById("message-form");
    const messageInput = document.getElementById("message-input");
    const fileInput = document.getElementById("file-input");
    const uploadButton = document.getElementById("upload-button");
    const fileListDiv = document.getElementById("file-list");
    const themeToggle = document.getElementById("theme-toggle"); // Esto ahora es el input checkbox
    let isThinking = false;
    let selectedFiles = []; // Usaremos esta variable para los archivos seleccionados temporalmente

    // --- Funciones de Tema (Modo Claro/Oscuro) ---
    function setTheme(theme) {
        document.body.classList.toggle("dark-mode", theme === "dark");
        localStorage.setItem("theme", theme);
        // Actualizar el estado del checkbox
        themeToggle.checked = (theme === "dark");
    }

    // Aplicar tema al cargar la página
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
        setTheme("dark");
    } else {
        setTheme("light");
    }

    // Event listener para el botón de alternar tema (ahora el checkbox)
    themeToggle.addEventListener("change", () => { // Usar 'change' para checkbox
        setTheme(themeToggle.checked ? "dark" : "light");
    });

    // --- Conexión WebSocket ---
    const socket = new WebSocket(`ws://${window.location.host}/ws`);

    // --- Funciones de UI ---
    function addMessage(content, type, options = {}) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", `${type}-message`);

        if (type === 'agent-status') {
            messageDiv.innerHTML = content;
        } else if (options.isCode) {
            // --- Lógica para crear bloques de código mejorados ---
            const codeContainer = document.createElement("div");
            codeContainer.className = "code-block-container";

            const header = document.createElement("div");
            header.className = "code-block-header";

            const lang = document.createElement("span");
            lang.textContent = options.lang;
            header.appendChild(lang);

            const copyButton = document.createElement("button");
            copyButton.className = "copy-button";
            copyButton.textContent = "Copiar";
            copyButton.addEventListener("click", () => {
                navigator.clipboard.writeText(content).then(() => {
                    copyButton.textContent = "¡Copiado!";
                    copyButton.classList.add("copied");
                    setTimeout(() => {
                        copyButton.textContent = "Copiar";
                        copyButton.classList.remove("copied");
                    }, 2000);
                });
            });
            header.appendChild(copyButton);
            codeContainer.appendChild(header);

            const pre = document.createElement("pre");
            const code = document.createElement("code");
            code.className = `language-${options.lang}`;
            code.textContent = content;
            pre.appendChild(code);
            codeContainer.appendChild(pre);
            
            // Usar el parser de `marked` para el resaltado de sintaxis
            const renderedHtml = marked.parse(pre.outerHTML);
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = renderedHtml;
            
            codeContainer.replaceChild(tempDiv.firstChild, pre);
            messageDiv.appendChild(codeContainer);

        } else {
            const p = document.createElement("p");
            if (type === 'bot') {
                p.innerHTML = marked.parse(content); // Renderizar Markdown para mensajes del bot
            } else {
                p.textContent = content;
            }
            messageDiv.appendChild(p);
        }
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function updateFileList() {
        fileListDiv.innerHTML = "";
        if (selectedFiles.length > 0) {
            fileListDiv.innerHTML = "<strong>Archivos adjuntos:</strong> ";
            selectedFiles.forEach((file, index) => {
                const fileTag = document.createElement("span");
                fileTag.classList.add("file-tag");
                fileTag.innerHTML = `${file.name} <span class="remove-file" data-index="${index}">x</span>`;
                fileListDiv.appendChild(fileTag);
            });
        }
        // El botón "Limpiar Archivos" ha sido eliminado, así que no hay necesidad de controlarlo aquí.
    }

    // --- Lógica de Carga de Archivos ---
    uploadButton.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", () => {
        selectedFiles = Array.from(fileInput.files); // Almacenar los archivos seleccionados
        updateFileList(); // Actualizar la lista de archivos mostrados
    });
    
    // Event listener para eliminar archivos individualmente
    fileListDiv.addEventListener("click", (event) => {
        if (event.target.classList.contains("remove-file")) {
            const index = parseInt(event.target.dataset.index);
            selectedFiles.splice(index, 1); // Eliminar el archivo del array
            // Actualizar los índices en el DOM si es necesario, o simplemente reconstruir la lista
            updateFileList(); // Reconstruir la lista para actualizar los índices y la UI
        }
    });

    // --- Lógica de WebSocket ---
    //socket.onopen = () => addMessage("Conectado a DevTeam-Bot.", "agent-status");
    socket.onerror = (error) => addMessage("Error de conexión. Por favor, refresca la página.", "bot");
    
    socket.onmessage = (event) => {
        const eventData = JSON.parse(event.data);
        console.log("Evento del servidor:", eventData);

        if (eventData.error) {
            addMessage(`Error del servidor: ${eventData.error}`, 'agent-status');
            isThinking = false; messageInput.disabled = false;
            return;
        }

        if (eventData.type === "done") {
            isThinking = false; messageInput.disabled = false; messageInput.focus();
            selectedFiles = []; // Limpiar archivos después de enviar
            fileInput.value = ''; // Limpiar el input de tipo file
            updateFileList(); // Actualizar la lista de archivos (vacía)
            return;
        }
        
        // Manejar el evento de respuesta final del servidor
        if (eventData.type === "final_response") {
            addMessage(marked.parse(eventData.content), 'bot'); // Renderizar Markdown
            return;
        }

        const nodeName = Object.keys(eventData)[0];
        if (nodeName) {
            const nodeOutput = eventData[nodeName];
            const friendlyNodeName = nodeName.replace(/_/g, ' ').replace('agent', '').trim().toUpperCase();

            // Mostrar el nombre del paso para nodos de desarrollo
            if (friendlyNodeName && !["SUPERVISOR", "CONVERSATIONAL", "MULTIMODAL ANALYZER"].includes(friendlyNodeName)) {
                 addMessage(`<i>Paso: ${friendlyNodeName}</i>`, 'agent-status');
            }

            // Lógica detallada para mostrar la salida de cada nodo
            if (nodeOutput) {
                // Salida del Diseñador UI/UX
                if (nodeOutput.ui_ux_spec) {
                    addMessage(nodeOutput.ui_ux_spec, 'bot');
                }
                // Salida del Planificador
                if (nodeOutput.dev_plan) {
                    const plan = nodeOutput.dev_plan;
                    let planHtml = "<h4>Plan de Desarrollo</h4><ul>";
                    if(plan.plan_type) planHtml += `<li><strong>Tipo:</strong> ${plan.plan_type}</li>`;
                    if(plan.frontend_task) planHtml += `<li><strong>Tarea Frontend:</strong> ${plan.frontend_task}</li>`;
                    if(plan.frontend_tech) planHtml += `<li><strong>Tecnología Frontend:</strong> ${plan.frontend_tech}</li>`;
                    if(plan.backend_task) planHtml += `<li><strong>Tarea Backend:</strong> ${plan.backend_task}</li>`;
                    if(plan.backend_tech) planHtml += `<li><strong>Tecnología Backend:</strong> ${plan.backend_tech}</li>`;
                    planHtml += "</ul>";
                    addMessage(planHtml, 'bot');
                }
                // Salida del Desarrollador Frontend
                if (nodeOutput.frontend_code && typeof nodeOutput.frontend_code === 'object') {
                    for (const [lang, code] of Object.entries(nodeOutput.frontend_code)) {
                        addMessage(code, 'bot', { isCode: true, lang: lang });
                    }
                }
                // Salida del Desarrollador Backend
                if (nodeOutput.backend_code) {
                    addMessage(nodeOutput.backend_code, 'bot', { isCode: true, lang: 'python' });
                }
                // Salida del Revisor de Código
                if (nodeOutput.review_feedback) {
                    addMessage(`**Feedback de Revisión:** ${nodeOutput.review_feedback}`, 'bot');
                } else if (nodeName === 'review_code') {
                     addMessage("**Revisión:** Código APROBADO.", 'bot');
                }
                // Salida de respuesta final genérica
                if (nodeOutput.final_response) {
                    // Esta parte ya no debería ser necesaria si el tipo "final_response" se maneja arriba
                    // Pero la mantengo por si acaso, aunque la lógica principal se mueve.
                    addMessage(nodeOutput.final_response, 'bot');
                }
            }
        }
    };

    // --- Lógica de Envío de Mensajes ---
    messageForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = messageInput.value;
        if (!message.trim() && selectedFiles.length === 0 || isThinking) return;
        
        addMessage(message, "user"); // Mostrar mensaje del usuario inmediatamente
        
        messageInput.value = "";
        messageInput.disabled = true;
        isThinking = true;
        addMessage("<i>DevTeam-Bot está pensando...</i>", 'agent-status');

        // --- Lógica de Envío Unificada (Siempre por WebSocket) ---
        let uploadedFileNames = [];

        // 1. Si hay archivos, súbelos primero por HTTP.
        if (selectedFiles.length > 0) {
            const formData = new FormData();
            selectedFiles.forEach(file => formData.append("files", file));
            
            try {
                const response = await fetch("/upload", {
                    method: "POST",
                    body: formData,
                });
                const result = await response.json();
                if (!response.ok) {
                    throw new Error(result.error || "Error al subir archivos.");
                }
                uploadedFileNames = result.filenames;
                addMessage(`<i>Archivos subidos: ${uploadedFileNames.join(", ")}</i>`, 'agent-status');
            } catch (error) {
                addMessage(`<i>Error de red: ${error.message}</i>`, 'agent-status');
                isThinking = false;
                messageInput.disabled = false;
                return; // Detener si la subida falla
            }
        }

        // 2. Envía el mensaje y los nombres de archivo por WebSocket.
        const payload = {
            user_input: message,
            file_names: uploadedFileNames,
        };
        console.log("Enviando payload al WebSocket:", payload);
        socket.send(JSON.stringify(payload));
    });
});
