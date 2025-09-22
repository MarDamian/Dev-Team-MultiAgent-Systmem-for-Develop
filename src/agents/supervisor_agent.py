from src.model import analytical_llm
from src.tools.generate_hyperlink import generate_local_html_hyperlink, create_hyperlink_message
from langchain_core.messages import HumanMessage
import os
import re

# La lista de nodos disponibles se mantiene igual.
AVAILABLE_NODES = [
    "conversational_agent",
    "multimodal_analyzer",
    "ui_ux_designer",
    "planner",
    "develop_backend",
    "develop_frontend",
    "quality_auditor",
    "__end__"
]

def supervisor_node(state: dict) -> dict:
    """
    Supervisor orquestador robustecido para manejar respuestas inesperadas del LLM
    y con lógica de enrutamiento mejorada.
    """
    print("---AGENTE: SUPERVISOR ORQUESTADOR---")

    # (La sección de recopilación de estado se mantiene igual)
    plan = state.get("dev_plan", {})
    has_plan = bool(plan)
    # ... etc ...

    # --- Todas las demás variables de estado se mantienen igual que en tu código ---
    user_input = state.get("user_input", "")
    has_files = bool(state.get("file_paths"))
    has_spec = bool(state.get("ui_ux_spec"))
    has_code = bool(state.get("frontend_code") or state.get("backend_code"))
    has_feedback = bool(state.get("review_feedback"))
    code_approved = state.get("code_approved", False)
    task_complete = state.get("task_complete", False)
    rag_status = state.get("rag_status")

    decision = ""

    # --- 1. Lógica de Finalización (Prioridad Máxima) ---
    if code_approved:
        # ... (código de finalización)
        print("Tarea finalizada (código aprobado).")
        final_response_message = "Tarea completada."
        if os.path.exists("outputs/index.html"):
            hyperlink = generate_local_html_hyperlink("outputs/index.html")
            final_response_message += create_hyperlink_message(hyperlink)
        return {"routing_decision": "__end__", "final_response": final_response_message}

    if task_complete:
        print("Tarea de un solo paso completa. Finalizando flujo.")
        return {"routing_decision": "__end__"}

    # --- 2. Lógica de Enrutamiento Basada en Estado (Reglas Explícitas) ---
    if rag_status == "continue":
        return {"routing_decision": "planner"}
    if has_feedback:
        if plan.get("plan_type") in ["frontend", "both"]: decision = "develop_frontend"
        else: decision = "develop_backend"
    elif has_code:
        decision = "quality_auditor"
    elif has_plan:
        plan_type = plan.get("plan_type")
        if plan_type in ["frontend", "both"]: decision = "develop_frontend"
        elif plan_type == "backend": decision = "develop_backend"
        else: decision = "conversational_agent"
    elif has_spec:
        decision = "planner"

    # --- 3. Enrutamiento Inicial Basado en LLM (MODIFICADO Y ROBUSTECIDO) ---
    if not decision:
        print("No se encontró una regla de enrutamiento explícita. Consultando al LLM para la tarea inicial.")
        
        prompt = f"""
        Eres un enrutador lógico experto. Tu única tarea es decidir el primer paso en un flujo de trabajo de desarrollo de software.
        Responde ÚNICAMENTE con el nombre de uno de los siguientes nodos: {AVAILABLE_NODES}. No des explicaciones.

        Petición del usuario: "{user_input}"
        ¿Hay archivos adjuntos?: {has_files}

        **REGLAS DE ENRUTAMIENTO CRÍTICAS:**
        - Para `ui_ux_designer`: Si la petición es **crear, implementar, desarrollar, codificar, o construir una interfaz** a partir de un archivo visual (imagen o video). La intención es PRODUCTIVA.
        - Para `multimodal_analyzer`: Si la petición es **analizar, describir, resumir, explicar, o decir qué hay** en un archivo. La intención es INFORMATIVA.
        - Para `conversational_agent`: Para cualquier otra cosa (preguntas, saludos, tareas no claras).

        Ejemplos:
        - "Implementa este diseño" (con imagen) -> ui_ux_designer
        - "¿Qué ves en este video?" (con video) -> multimodal_analyzer
        - "Crea una web a partir de este video" (con video) -> ui_ux_designer

        Nodo de destino:
        """
        
        message = HumanMessage(content=prompt)
        response = analytical_llm.invoke([message])
        llm_response_content = response.content.strip()

        print(f"Respuesta del LLM para enrutamiento: '{llm_response_content}'") # <-- DEBUGGING MUY ÚTIL

        # --- Lógica de parseo más robusta ---
        if llm_response_content:
            node_pattern = re.compile(r'\b(' + '|'.join(re.escape(node) for node in AVAILABLE_NODES) + r')\b')
            match = node_pattern.search(llm_response_content)
            if match:
                decision = match.group(1)
        
        # Si después de todo, la decisión sigue vacía, usamos el fallback
        if not decision:
            print(f"ADVERTENCIA: El LLM dio una respuesta no concluyente o vacía. Usando 'conversational_agent' como fallback.")
            decision = "conversational_agent"

    # --- 4. Validación Final (sin cambios, pero ahora debería funcionar) ---
    if decision not in AVAILABLE_NODES:
        print(f"ADVERTENCIA: Decisión inválida ('{decision}'). Forzando a '__end__' para evitar un error.")
        decision = "__end__"
    
    print(f"Decisión del Supervisor: Enviar a '{decision}'")
    
    return {"routing_decision": decision}