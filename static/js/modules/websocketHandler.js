// Contenido para: static/js/modules/websocketHandler.js

import { addMessage } from './ui.js';
// <-- CAMBIO CLAVE: Importar la función para añadir al historial
import { addToHistory } from './chatState.js';

function handleAgentMessage(nodeName, nodeOutput) {
    const friendlyNodeName = nodeName.replace(/_/g, ' ').replace('agent', '').trim().toUpperCase();
    if (friendlyNodeName && !["SUPERVISOR", "CONVERSATIONAL", "MULTIMODAL ANALYZER"].includes(friendlyNodeName)) {
        addMessage(`<i>Paso: ${friendlyNodeName}</i>`, 'agent-status');
    }

    if (!nodeOutput) return;

    if (nodeName === 'conversational_agent' && nodeOutput.final_response) {
        const botResponse = marked.parse(nodeOutput.final_response);
        addMessage(botResponse, 'bot');
        addToHistory("Bot", nodeOutput.final_response); 
    }
    if (nodeOutput.ui_ux_spec) {
        addMessage(marked.parse(nodeOutput.ui_ux_spec), 'bot');
        addToHistory("Bot", nodeOutput.ui_ux_spec);
    }
    if (nodeOutput.analysis_result) {
        addMessage(marked.parse(nodeOutput.analysis_result), 'bot');
        addToHistory("Bot", nodeOutput.analysis_result); 
    }
    if (nodeOutput.dev_plan) {
        const plan = nodeOutput.dev_plan;
        let planHtml = "<h4>Plan de Desarrollo</h4><ul>" +
            (plan.plan_type ? `<li><strong>Tipo:</strong> ${plan.plan_type}</li>` : '') +
            (plan.frontend_task ? `<li><strong>Tarea Frontend:</strong> ${plan.frontend_task}</li>` : '') +
            (plan.backend_task ? `<li><strong>Tarea Backend:</strong> ${plan.backend_task}</li>` : '') + 
            (plan.db_task ? `<li><strong>Tarea base de Datos:</strong> ${plan.db_task}</li>` : '') + 
            "</ul>";

        addMessage(planHtml, 'bot');

        const planTextParts = ["Plan de Desarrollo:"];
        if (plan.plan_type) planTextParts.push(`Tipo=${plan.plan_type}`);
        if (plan.frontend_task) planTextParts.push(`Tarea Frontend=${plan.frontend_task}`);
        if (plan.backend_task) planTextParts.push(`Tarea Backend=${plan.backend_task}`); 

    }
    if (nodeName === 'develop_frontend' && nodeOutput.frontend_code) {
        for (const [lang, code] of Object.entries(nodeOutput.frontend_code)) {
            if (code) addMessage(code, 'bot', { isCode: true, lang });
        }
    }
    if (nodeName === 'database_architech' && nodeOutput.db_schema) {
        for (const [lang, code] of Object.entries(nodeOutput.db_schema)) {
            if (code) addMessage(code, 'bot', { isCode: true, lang });
        }
    }
    if (nodeName === 'develop_backend' && nodeOutput.backend_code) {
        for (const [lang, code] of Object.entries(nodeOutput.backend_code)) {
            if (code) addMessage(code, 'bot', { isCode: true, lang });
        }
    }
    if (nodeName === 'quality_auditor' && nodeOutput.feedback) {
        const prefix = nodeOutput.code_approved ? "Auditoría" : "Feedback del Auditor";
        const feedbackMessage = `**${prefix}:** ${nodeOutput.feedback}`;
        addMessage(feedbackMessage, 'bot');
        addToHistory("Bot", feedbackMessage); // <-- CAMBIO CLAVE
    }
}

export function initWebSocket(callbacks) {
    // ... (El código de esta función no cambia) ...
    const socket = new WebSocket(`ws://${window.location.host}/ws`);
    socket.onerror = () => addMessage("Error de conexión. Por favor, refresca la página.", "bot");

    socket.onmessage = (event) => {
        const eventData = JSON.parse(event.data);
        console.log("Mensaje recibido del servidor:", eventData);

        if (eventData.error) {
            addMessage(`Error del servidor: ${eventData.error}`, 'agent-status');
            callbacks.onDone();
            return;
        }
        if (eventData.type === "done") {
            callbacks.onDone();
            return;
        }
        if (eventData.type === "final_response") {
            const finalMessage = marked.parse(eventData.content);
            addMessage(finalMessage, 'bot');
            addToHistory("Bot", eventData.content); // <-- CAMBIO CLAVE
            return;
        }

        const nodeName = Object.keys(eventData)[0];
        if (nodeName) {
            handleAgentMessage(nodeName, eventData[nodeName]);
        }
    };
    return socket;
}