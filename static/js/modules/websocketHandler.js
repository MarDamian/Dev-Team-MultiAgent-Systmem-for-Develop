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

    if (!nodeOutput) return;

    // ============================================
    // CONVERSATIONAL AGENT - Respuesta final
    // ============================================
    if (nodeName === 'conversational_agent' && nodeOutput.final_response) {
        const botResponse = marked.parse(nodeOutput.final_response);
        addMessage(botResponse, 'bot', { agent: agentKey });
        addToHistory("Bot", nodeOutput.final_response);
        return;
    }

    // ============================================
    // PLANNER - Plan de desarrollo + Contratos
    // ============================================
    if (nodeName === 'planner' && nodeOutput.dev_plan) {
        const plan = nodeOutput.dev_plan;

        // Construir mensaje completo del planner en una sola vez
        let plannerMessage = `<h4>📋 Proyecto Creado</h4>`;

        // Información del proyecto
        if (nodeOutput.project_id) {
            plannerMessage += `<p><strong>ID:</strong> <code>${nodeOutput.project_id}</code></p>`;
        }
        if (plan.project_name) {
            plannerMessage += `<p><strong>Nombre:</strong> ${plan.project_name}</p>`;
        }
        if (plan.plan_type) {
            plannerMessage += `<p><strong>Tipo:</strong> ${plan.plan_type}</p>`;
        }

        // Plan de desarrollo - AHORA CON MARKDOWN PARSING
        plannerMessage += `<h4>📝 Plan de Desarrollo</h4>`;
        if (plan.frontend_task) {
            plannerMessage += `<div style="margin-bottom: 15px;">
                <strong>🎨 Frontend:</strong><br>${marked.parse(plan.frontend_task)}
                ${plan.frontend_tech ? `<em>Tecnología: ${plan.frontend_tech}</em>` : ''}
            </div>`;
        }
        if (plan.backend_task) {
            plannerMessage += `<div style="margin-bottom: 15px;">
                <strong>⚙️ Backend:</strong><br>${marked.parse(plan.backend_task)}
                ${plan.backend_tech ? `<em>Tecnología: ${plan.backend_tech}</em>` : ''}
            </div>`;
        }
        if (plan.db_task) {
            plannerMessage += `<div style="margin-bottom: 15px;">
                <strong>🗄️ Base de Datos:</strong><br>${marked.parse(plan.db_task)}
                ${plan.db_tech ? `<em>Tecnología: ${plan.db_tech}</em>` : ''}
            </div>`;
        }

        // Contratos de API
        if (nodeOutput.api_contracts && nodeOutput.api_contracts.length > 0) {
            plannerMessage += `<h4>🔗 Contratos de API (${nodeOutput.api_contracts.length})</h4><ul>`;
            nodeOutput.api_contracts.forEach(contract => {
                plannerMessage += `<li><code>${contract.method} ${contract.endpoint}</code> - ${contract.description}</li>`;
            });
            plannerMessage += `</ul>`;
        }

        // Modelos de datos
        if (nodeOutput.data_contracts && nodeOutput.data_contracts.length > 0) {
            plannerMessage += `<h4>📊 Modelos de Datos (${nodeOutput.data_contracts.length})</h4><ul>`;
            nodeOutput.data_contracts.forEach(model => {
                plannerMessage += `<li><strong>${model.model_name}</strong> - ${model.description}</li>`;
            });
            plannerMessage += `</ul>`;
        }

        // Enviar todo en un solo mensaje
        addMessage(plannerMessage, 'bot', { agent: agentKey });
        return;
    }

    // ============================================
    // MULTIMODAL ANALYZER - Análisis
    // ============================================
    if (nodeName === 'multimodal_analyzer' && nodeOutput.analysis_result) {
        addMessage(`<h4>🔍 Análisis Multimodal</h4>${marked.parse(nodeOutput.analysis_result)}`, 'bot', { agent: agentKey });
        addToHistory("Bot", nodeOutput.analysis_result);
        return;
    }

    // ============================================
    // UI/UX DESIGNER - Especificación
    // ============================================
    if (nodeName === 'ui_ux_designer' && nodeOutput.ui_ux_spec) {
        addMessage(`<h4>🎨 Diseño UI/UX</h4>${marked.parse(nodeOutput.ui_ux_spec)}`, 'bot', { agent: agentKey });
        addToHistory("Bot", nodeOutput.ui_ux_spec);
        return;
    }

    // ============================================
    // BACKEND DEVELOPER - Código generado
    // ============================================
    if (nodeName === 'develop_backend' && nodeOutput.backend_code) {
        const fileCount = Object.keys(nodeOutput.backend_code).length;

        // Construir mensaje completo en una sola vez
        let backendMessage = `<h4>⚙️ Backend Generado (${fileCount} archivos)</h4><ul>`;
        for (const filename of Object.keys(nodeOutput.backend_code)) {
            backendMessage += `<li><code>${filename}</code></li>`;
        }
        backendMessage += '</ul>';

        // Enviar todo en un solo mensaje
        addMessage(backendMessage, 'bot', { agent: agentKey });
        return;
    }

    // ============================================
    // FRONTEND DEVELOPER - Código generado
    // ============================================
    if (nodeName === 'develop_frontend' && nodeOutput.frontend_code) {
        const fileCount = Object.keys(nodeOutput.frontend_code).length;

        // Construir mensaje completo en una sola vez
        let frontendMessage = `<h4>🎨 Frontend Generado (${fileCount} archivos)</h4><ul>`;
        for (const filename of Object.keys(nodeOutput.frontend_code)) {
            frontendMessage += `<li><code>${filename}</code></li>`;
        }
        frontendMessage += '</ul>';

        // Enviar todo en un solo mensaje
        addMessage(frontendMessage, 'bot', { agent: agentKey });
        return;
    }

    // ============================================
    // DATABASE ARCHITECT - Esquema generado
    // ============================================
    if (nodeName === 'database_architech' && nodeOutput.db_schema) {
        const fileCount = Object.keys(nodeOutput.db_schema).length;

        // Construir mensaje completo en una sola vez
        let databaseMessage = `<h4>🗄️ Base de Datos Generada (${fileCount} archivos)</h4><ul>`;
        for (const filename of Object.keys(nodeOutput.db_schema)) {
            databaseMessage += `<li><code>${filename}</code></li>`;
        }
        databaseMessage += '</ul>';

        // Enviar todo en un solo mensaje
        addMessage(databaseMessage, 'bot', { agent: agentKey });
        return;
    }

    // ============================================
    // QUALITY AUDITOR - Feedback
    // ============================================
    if (nodeName === 'quality_auditor' && nodeOutput.feedback) {
        const isApproved = nodeOutput.code_approved;
        const icon = isApproved ? '✅' : '⚠️';
        const title = isApproved ? 'Código Aprobado' : 'Revisión Requerida';

        const feedbackHtml = `<h4>${icon} ${title}</h4><p>${marked.parse(nodeOutput.feedback)}</p>`;
        addMessage(feedbackHtml, 'bot', { agent: agentKey });
        addToHistory("Bot", `${title}: ${nodeOutput.feedback}`);
        return;
    }
}

export function initWebSocket(callbacks) {
    const socket = new WebSocket(`ws://${window.location.host}/ws`);

    // Variable para rastrear si se generó código
    let codeGenerated = false;

    socket.onopen = () => {
        console.log("WebSocket conectado.");
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        addMessage("❌ Error de conexión. Por favor, refresca la página.", "bot");
    };

    socket.onmessage = (event) => {
        const eventData = JSON.parse(event.data);
        console.log("Mensaje recibido del servidor:", eventData);

        if (eventData.error) {
            addMessage(`❌ Error del servidor: ${eventData.error}`, 'bot');
            callbacks.onDone();
            return;
        }
        if (eventData.type === "done") {
            // Mensaje final de completado
            // Solo mostrar mensaje de completado si se generó código
            if (codeGenerated) {
                addMessage("✅ <strong>Tarea completada</strong>. Revisa los archivos generados en la carpeta <code>outputs/</code>.", 'bot');
            }
            callbacks.onDone();
            // Resetear el flag para la próxima tarea
            codeGenerated = false;
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
            // Detectar si se generó código (backend, frontend, o database)
            const nodeOutput = eventData[nodeName];
            if (nodeName === 'develop_backend' && nodeOutput.backend_code) {
                codeGenerated = true;
            }
            if (nodeName === 'develop_frontend' && nodeOutput.frontend_code) {
                codeGenerated = true;
            }
            if (nodeName === 'database_architech' && nodeOutput.db_schema) {
                codeGenerated = true;
            }

            handleAgentMessage(nodeName, nodeOutput);
        }
    };

    socket.onclose = () => {
        console.log("WebSocket desconectado.");
    };

    return socket;
}