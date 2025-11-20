// Contenido para: static/js/modules/websocketHandler.js

import { addMessage } from './ui.js';
import { addToHistory } from './chatState.js';

function handleAgentMessage(nodeName, nodeOutput) {
    // Map node names to CSS agent keys
    const agentMap = {
        'supervisor': 'supervisor',
        'conversational_agent': 'conversational',
        'multimodal_analyzer': 'multimodal',
        'ui_ux_designer': 'ui_ux',
        'planner': 'planner',
        'develop_frontend': 'frontend',
        'develop_backend': 'backend',
        'database_architech': 'database',
        'quality_auditor': 'auditor'
    };

    const agentKey = agentMap[nodeName] || 'supervisor';


    if (nodeName !== 'conversational_agent' && nodeName !== 'supervisor') {
        addMessage(`<i>Procesando...</i>`, 'agent-status', { agent: agentKey });
    }

    if (!nodeOutput) return;

    // Handle specific outputs
    if (nodeName === 'conversational_agent' && nodeOutput.final_response) {
        const botResponse = marked.parse(nodeOutput.final_response);
        addMessage(botResponse, 'bot', { agent: agentKey });
        addToHistory("Bot", nodeOutput.final_response);
    }

    if (nodeOutput.ui_ux_spec) {
        addMessage(marked.parse(nodeOutput.ui_ux_spec), 'bot', { agent: agentKey });
        addToHistory("Bot", nodeOutput.ui_ux_spec);
    }

    if (nodeOutput.analysis_result) {
        addMessage(marked.parse(nodeOutput.analysis_result), 'bot', { agent: agentKey });
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

        addMessage(planHtml, 'bot', { agent: agentKey });

        const planTextParts = ["Plan de Desarrollo:"];
        if (plan.plan_type) planTextParts.push(`Tipo=${plan.plan_type}`);
        if (plan.frontend_task) planTextParts.push(`Tarea Frontend=${plan.frontend_task}`);
        if (plan.backend_task) planTextParts.push(`Tarea Backend=${plan.backend_task}`);
    }

    if (nodeName === 'develop_frontend' && nodeOutput.frontend_code) {
        for (const [lang, code] of Object.entries(nodeOutput.frontend_code)) {
            if (code) addMessage(code, 'bot', { isCode: true, lang, agent: agentKey });
        }
    }

    if (nodeName === 'database_architech' && nodeOutput.db_schema) {
        for (const [lang, code] of Object.entries(nodeOutput.db_schema)) {
            if (code) addMessage(code, 'bot', { isCode: true, lang, agent: agentKey });
        }
    }

    if (nodeName === 'develop_backend' && nodeOutput.backend_code) {
        for (const [lang, code] of Object.entries(nodeOutput.backend_code)) {
            if (code) addMessage(code, 'bot', { isCode: true, lang, agent: agentKey });
        }
    }

    if (nodeName === 'quality_auditor' && nodeOutput.feedback) {
        const prefix = nodeOutput.code_approved ? "Auditoría Aprobada" : "Feedback del Auditor";
        const feedbackMessage = `**${prefix}:** ${nodeOutput.feedback}`;
        addMessage(feedbackMessage, 'bot', { agent: agentKey });
        addToHistory("Bot", feedbackMessage);
    }
}

export function initWebSocket(callbacks) {
    const socket = new WebSocket(`ws://${window.location.host}/ws`);

    socket.onopen = () => {
        console.log("WebSocket conectado.");
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        addMessage("Error de conexión. Por favor, refresca la página.", "bot");
    };

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
            addToHistory("Bot", eventData.content);
            return;
        }

        const nodeName = Object.keys(eventData)[0];
        if (nodeName) {
            handleAgentMessage(nodeName, eventData[nodeName]);
        }
    };

    socket.onclose = () => {
        console.log("WebSocket desconectado.");
    };

    return socket;
}