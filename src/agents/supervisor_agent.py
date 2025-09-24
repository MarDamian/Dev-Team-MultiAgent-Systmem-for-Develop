# Contenido para: src/agents/supervisor_agent.py

from src.model import analytical_llm
from src.tools.generate_hyperlink import generate_local_html_hyperlink, create_hyperlink_message
from langchain_core.messages import HumanMessage
import os
import re

AVAILABLE_NODES = [
    "conversational_agent", "multimodal_analyzer", "ui_ux_designer", "planner",
    "develop_backend", "develop_frontend", "quality_auditor", "__end__"
]

def supervisor_node(state: dict) -> dict:
    """
    Supervisor orquestador puro. Enruta la tarea basándose en el estado actual de la sesión.
    La gestión del estado entre tareas (incluido el historial) se maneja en main.py.
    """
    print("---AGENTE: SUPERVISOR ORQUESTADOR---")

    # --- 1. LÓGICA DE FINALIZACIÓN (PRIORIDAD MÁXIMA) ---
    if state.get("code_approved"):
        print("Tarea finalizada (código aprobado).")
        final_response_message = "Tarea completada."
        if os.path.exists("outputs/index.html"):
            hyperlink = generate_local_html_hyperlink("outputs/index.html")
            final_response_message += create_hyperlink_message(hyperlink)
        return {"routing_decision": "__end__", "final_response": final_response_message}

    if state.get("task_complete"):
        print("Tarea de un solo paso completa. Finalizando flujo.")
        return {"routing_decision": "__end__"}

    # --- 2. RECOPILACIÓN DE ESTADO Y ENRUTAMIENTO ---
    plan = state.get("dev_plan", {})
    has_plan = bool(plan)
    has_files = bool(state.get("file_paths"))
    has_spec = bool(state.get("ui_ux_spec"))
    has_code = bool(state.get("frontend_code") or state.get("backend_code"))
    has_feedback = bool(state.get("review_feedback"))
    rag_status = state.get("rag_status")
    decision_route = ""

    # --- 3. ENRUTAMIENTO BASADO EN ESTADO (TAREAS EN CURSO) ---
    if rag_status == "continue":
        decision_route = "planner"
    elif has_feedback:
        if plan.get("plan_type") in ["frontend", "both"]: decision_route = "develop_frontend"
        else: decision_route = "develop_backend"
    elif has_code:
        decision_route = "quality_auditor"
    elif has_plan:
        plan_type = plan.get("plan_type")
        if plan_type in ["frontend", "both"]: decision_route = "develop_frontend"
        elif plan_type == "backend": decision_route = "develop_backend"
        else: decision_route = "conversational_agent"
    elif has_spec:
        decision_route = "planner"

    # --- 4. ENRUTAMIENTO INICIAL BASADO EN INTENCIÓN (NUEVAS TAREAS) ---
    if not decision_route:
        print("No se encontró una regla de enrutamiento explícita. Consultando al LLM.")
        user_input = state.get("user_input", "")
        chat_history = state.get("chat_history", [])
        
        # <<< --- INICIO DE LA MODIFICACIÓN --- >>>
        prompt_route = f"""
        Eres un enrutador de tareas experto. Clasifica la intención del usuario y elige el siguiente nodo correcto en el flujo de trabajo.
        Responde ÚNICAMENTE con el nombre de uno de estos nodos: {AVAILABLE_NODES}.

        Historial de la Conversación Reciente:
        {chat_history[-4:]} 

        Petición Actual del Usuario: "{user_input}"
        Archivos adjuntos: {has_files}

        **Reglas de Intención y Enrutamiento:**

        1. **Intención de Desarrollo / Creación:** Si el usuario quiere crear, construir, implementar o desarrollar una aplicación, web, API, base de datos, etc.
           - Si la petición se enfoca explícitamente en lógica de backend, bases de datos, APIs, manejo de datos, servidor** (ej: "crea una base de datos para esto", "desarrolla una API con estos requisitos", "necesito el backend para esta imagen"), la tarea debe ser planificada.
             -> `planner`
           - Si el foco principal es el diseño visual o la interfaz de usuario a partir de un archivo de imagen/video/boceto adjunto (ej: "convierte este diseño en una web", "créame el HTML y CSS para esta maqueta").
             -> `ui_ux_designer`
           - Si es una petición de desarrollo general, abstracta o mixta (frontend + backend)** sin un archivo visual como punto de partida claro (ej: "créame una app de tareas", "hazme un juego de snake").
             -> `planner`

        2. **Intención de Análisis Puro:** Si el usuario solo quiere saber qué contiene un archivo (ej: "¿qué dice este audio?", "¿describe esta imagen?") SIN una solicitud explícita de construir o desarrollar algo con ello.
           - -> `multimodal_analyzer`

        3. **Intención Conversacional:** Si es un saludo, despedida, una pregunta de conocimiento general o una conversación que no encaja en las anteriores.
           - -> `conversational_agent`

           
           
        Nodo de destino:
        """
        # <<< --- FIN DE LA MODIFICACIÓN --- >>>

        message = HumanMessage(content=prompt_route)
        response = analytical_llm.invoke([message])
        llm_response_content = response.content.strip()
        print(f"Respuesta del LLM para enrutamiento: '{llm_response_content}'")

        node_pattern = re.compile(r'\b(' + '|'.join(re.escape(node) for node in AVAILABLE_NODES) + r')\b')
        match = node_pattern.search(llm_response_content)
        if match:
            decision_route = match.group(1)
        else:
            print("ADVERTENCIA: Fallback a 'conversational_agent'.")
            decision_route = "conversational_agent"

    # --- 5. VALIDACIÓN FINAL ---
    if decision_route not in AVAILABLE_NODES:
        print(f"ADVERTENCIA: Decisión inválida ('{decision_route}'). Forzando a '__end__'.")
        decision_route = "__end__"
    
    print(f"Decisión del Supervisor: Enviar a '{decision_route}'")
    
    return {"routing_decision": decision_route}