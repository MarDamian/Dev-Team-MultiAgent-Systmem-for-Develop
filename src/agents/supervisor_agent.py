# Contenido para: src/agents/supervisor_agent.py

from src.model import analytical_llm
from src.tools.generate_hyperlink import generate_local_html_hyperlink, create_hyperlink_message
from langchain_core.messages import HumanMessage
import os
import re

AVAILABLE_NODES = [
    "conversational_agent", "multimodal_analyzer", "ui_ux_designer", "planner",
    "develop_backend", "develop_frontend", "quality_auditor", "database_architech","__end__"
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
    has_analysis_result = bool(state.get("analysis_result")) 
    has_spec = bool(state.get("ui_ux_spec"))
    has_db_schema = bool(state.get("db_schema"))
    has_code = bool(state.get("frontend_code") or state.get("backend_code"))
    has_feedback = bool(state.get("review_feedback"))
    rag_status = state.get("rag_status")
    decision_route = ""

    # --- 3. ENRUTAMIENTO BASADO EN ESTADO (TAREAS EN CURSO) ---
    if has_analysis_result and not has_plan:
        decision_route = "planner"
    if rag_status == "continue":
        decision_route = "planner"
    elif has_feedback:
        if plan.get("plan_type") in ["frontend", "both"]: decision_route = "develop_frontend"
        else: decision_route = "develop_backend"
    elif has_code:
        decision_route = "quality_auditor"
    elif has_plan:
        plan_type = plan.get("plan_type")
        # --- NUEVA LÓGICA DE ENRUTAMIENTO ---
        if plan_type in ["database", "both"] and not has_db_schema:
            # Si el plan es de backend y AÚN NO tenemos un esquema de BD, vamos al arquitecto.
            decision_route = "database_architech"
        elif plan_type in ["frontend", "both"]:
            # Si es frontend (o backend con esquema ya listo), vamos al desarrollador.
            decision_route = "develop_frontend"
        elif plan_type == "backend":
            # Si es solo backend y ya tenemos el esquema, vamos al desarrollador.
            decision_route = "develop_backend"
        else:
            decision_route = "conversational_agent"
    elif has_spec:
        decision_route = "planner"

    # --- 4. ENRUTAMIENTO INICIAL BASADO EN INTENCIÓN (NUEVAS TAREAS) ---
    if not decision_route:
        #print("No se encontró una regla de enrutamiento explícita. Consultando al LLM.")
        user_input = state.get("user_input", "")
        chat_history = state.get("chat_history", [])
        
        
        prompt_route = f"""
        Eres un enrutador de tareas experto. Tu objetivo es analizar la petición del usuario y decidir el PRIMER paso correcto en un flujo de trabajo.
        Responde ÚNICAMENTE con el nombre de uno de estos nodos: {AVAILABLE_NODES}.

        **Contexto:**
        - Petición del Usuario: "{user_input}"
        - ¿Hay archivos adjuntos?: {has_files}

        **Proceso de Decisión Lógico (Paso a Paso):**
        1.  **Requisito de Análisis:** 
            - ¿Pide crear una interfaz/sitio web o diesño web a partir de un diseño visual (imagen/boceto/video)? -> `ui_ux_designer`
             ¿La petición del usuario es para una base de datos, una API , o tares del backend ? -> `multimodal_analyzer`            
        2.  **Si no se requiere análisis previo**, evalúa la intención principal de desarrollo:
            - ¿Pide explícitamente y SOLO un esquema de BD o código SQL? -> `database_architech`
            - ¿Pide una aplicación completa, API, backend, o una tarea de desarrollo compleja? -> `planner`
            - ¿Pide crear una interfaz a partir de un diseño visual (imagen/boceto)? -> `ui_ux_designer`
        3.  **Otros Casos:**
            - ¿Pide solo saber qué hay en un archivo (análisis puro, sin construcción)? -> `multimodal_analyzer`
            - ¿Es una conversación normal (saludo, pregunta)? -> `conversational_agent`

        Basado en este proceso, ¿cuál es el único nodo correcto para la petición actual?
        Nodo de destino:
        """

        message = HumanMessage(content=prompt_route)
        response = analytical_llm.invoke([message])
        llm_response_content = response.content.strip()
        print(f"Respuesta del LLM para enrutamiento: '{llm_response_content}'")
        
        # Lógica de parseo robusta para evitar errores
        decision_route = "conversational_agent" # Fallback de seguridad
        for node in AVAILABLE_NODES:
            if node in llm_response_content:
                decision_route = node
                break

    # --- 5. VALIDACIÓN FINAL ---
    if decision_route not in AVAILABLE_NODES:
        print(f"ADVERTENCIA: Decisión inválida ('{decision_route}'). Forzando a '__end__'.")
        decision_route = "__end__"
    
    print(f"Decisión del Supervisor: Enviar a '{decision_route}'")
    
    return {"routing_decision": decision_route}
    