import { addMessage } from './ui.js';

function handleAgentMessage(nodeName, nodeOutput) {
    const friendlyNodeName = nodeName.replace(/_/g, ' ').replace('agent', '').trim().toUpperCase();

    if (friendlyNodeName && !["SUPERVISOR", "CONVERSATIONAL", "MULTIMODAL ANALYZER"].includes(friendlyNodeName)) {
        addMessage(`<i>Paso: ${friendlyNodeName}</i>`, 'agent-status');
    }

    if (!nodeOutput) return;

    if (nodeName === 'conversational_agent' && nodeOutput.final_response) {
        addMessage(marked.parse(nodeOutput.final_response), 'bot');
    }
    if (nodeOutput.ui_ux_spec) {
        addMessage(marked.parse(nodeOutput.ui_ux_spec), 'bot');
    }
    if (nodeOutput.dev_plan) {
        const plan = nodeOutput.dev_plan;
        let planHtml = "<h4>Plan de Desarrollo</h4><ul>";
        if (plan.plan_type) planHtml += `<li><strong>Tipo:</strong> ${plan.plan_type}</li>`;
        if (plan.frontend_task) planHtml += `<li><strong>Tarea Frontend:</strong> ${plan.frontend_task}</li>`;
        if (plan.frontend_tech) planHtml += `<li><strong>Tecnología Frontend:</strong> ${plan.frontend_tech}</li>`;
        if (plan.backend_task) planHtml += `<li><strong>Tarea Backend:</strong> ${plan.backend_task}</li>`;
        if (plan.backend_tech) planHtml += `<li><strong>Tecnología Backend:</strong> ${plan.backend_tech}</li>`;
        planHtml += "</ul>";
        addMessage(planHtml, 'bot');
    }
    if (nodeName === 'develop_frontend' && nodeOutput.frontend_code) {
        for (const [lang, code] of Object.entries(nodeOutput.frontend_code)) {
            if (code) addMessage(code, 'bot', { isCode: true, lang });
        }
    }
    if (nodeName === 'develop_backend' && nodeOutput.backend_code) {
        addMessage(nodeOutput.backend_code, 'bot', { isCode: true, lang: 'python' });
    }
    if (nodeName === 'quality_auditor' && nodeOutput.feedback) {
        const isApproved = nodeOutput.code_approved === true;
        const prefix = isApproved ? "Auditoría" : "Feedback del Auditor";
        addMessage(`**${prefix}:** ${nodeOutput.feedback}`, 'bot');
    }
}

export function initWebSocket(callbacks) {
    const socket = new WebSocket(`ws://${window.location.host}/ws`);
    socket.onerror = (error) => addMessage("Error de conexión. Por favor, refresca la página.", "bot");

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
            addMessage(marked.parse(eventData.content), 'bot');
            return;
        }

        const nodeName = Object.keys(eventData)[0];
        if (nodeName) {
            handleAgentMessage(nodeName, eventData[nodeName]);
        }
    };
    return socket;
}