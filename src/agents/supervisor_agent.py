# Contenido para: src/agents/supervisor_agent.py

from src.model import analytical_llm
from src.tools.file_analyzer import prepare_multimodal_input
from src.tools.generate_hyperlink import generate_local_html_hyperlink, create_hyperlink_message
from langchain_core.messages import HumanMessage
import json
import os
import re

# --- Lista de Nodos Disponibles para el Supervisor ---
# Define los nodos a los que el supervisor puede enrutar las tareas.
# '__end__' es una palabra clave especial en LangGraph para terminar el flujo.
AVAILABLE_NODES = [
    "conversational_agent",
    "multimodal_analyzer",
    "ui_ux_designer",
    "planner",
    "develop_backend",
    "develop_frontend",
    "review_code",
    "execute_code",
    "__end__"
]

def supervisor_node(state: dict) -> dict:
    """
    Este es el supervisor orquestador. Analiza el estado completo de la tarea
    y decide qué especialista debe actuar a continuación. Su lógica ahora está
    implementada principalmente en código para mayor robustez y mantenibilidad.
    """
    print("---AGENTE: SUPERVISOR ORQUESTADOR---")

    user_input = state.get("user_input", "")
    file_paths = state.get("file_paths", [])
    has_files = bool(file_paths)
    has_spec = "ui_ux_spec" in state and state["ui_ux_spec"] is not None
    has_plan = "dev_plan" in state and state["dev_plan"] is not None
    has_code = ("frontend_code" in state and state["frontend_code"]) or ("backend_code" in state and state["backend_code"])
    has_feedback = "review_feedback" in state and state["review_feedback"] is not None
    code_approved = state.get("code_approved", False)
    task_complete = state.get("task_complete", False)

    # --- Lógica de Enrutamiento Basada en Código (Más Robusta) ---
    decision = ""

    # 1. Lógica de finalización (prioridad máxima)
    if code_approved:
        print("Tarea finalizada (código aprobado).")
        final_response_message = state.get("final_response", "Tarea completada.")
        if os.path.exists("outputs/index.html"):
            hyperlink = generate_local_html_hyperlink("outputs/index.html")
            final_response_message += create_hyperlink_message(hyperlink)
            print(f"Hipervínculo generado: {hyperlink}")
        
        return {
            "routing_decision": "__end__",
            "final_response": final_response_message,
            "task_complete": None,
            "code_approved": None
        }

    if task_complete:
        print("Tarea de un solo paso completa. Finalizando flujo.")
        # La respuesta real fue generada y enviada por el nodo anterior.
        # El único trabajo de este nodo es terminar el grafo.
        # Devolver un diccionario sin `final_response` previene la duplicación en el frontend.
        return {
            "routing_decision": "__end__",
            "task_complete": None,
            "code_approved": None
        }

    # 2. Lógica de enrutamiento basada en el estado (reglas explícitas)
    # TODO: Mejorar la lógica para diferenciar entre frontend y backend.
    if has_feedback:
        decision = "develop_frontend" # Asume frontend por ahora
    elif has_code:
        decision = "review_code"
    elif has_plan:
        decision = "develop_frontend" # Asume frontend por ahora
    elif has_spec:
        decision = "planner"
    
    # 3. Si ninguna regla explícita coincide, usar el LLM para casos ambiguos.
    if not decision:
        print("No se encontró una regla de enrutamiento explícita. Consultando al LLM.")
        prompt = f"""
        Eres un enrutador lógico. Tu única tarea es decidir el siguiente paso en un flujo de trabajo.
        Responde ÚNICAMENTE con el nombre del nodo de la lista. No des explicaciones.

        Petición del usuario: "{user_input}"
        ¿Hay archivos adjuntos?: {has_files}

        REGLAS DE ENRUTAMIENTO:
        - Si el usuario pide "implementar", "crear", "desarrollar" o similar, enruta a `ui_ux_designer`.
        - Si el usuario pide "analizar", "resumir", "describir" o similar, enruta a `multimodal_analyzer`.
        - Para cualquier otra situación que implique una conversación, enruta a `conversational_agent`.
        - Si no estás seguro, enruta a `conversational_agent`.

        Basado en las reglas y la petición, ¿cuál es el siguiente nodo?
        """
        
        message = HumanMessage(content=prompt)
        response = analytical_llm.invoke([message])
        
        # --- Análisis Robusto de la Respuesta del LLM ---
        # Busca cualquiera de los nodos disponibles en la respuesta del LLM.
        # Esto es más resistente a respuestas con texto adicional.
        node_pattern = re.compile(r'\b(' + '|'.join(re.escape(node) for node in AVAILABLE_NODES) + r')\b')
        match = node_pattern.search(response.content)
        
        if match:
            decision = match.group(1)
        else:
            print(f"ADVERTENCIA: El LLM dio una respuesta no concluyente ('{response.content}'). Usando 'conversational_agent' como fallback.")
            decision = "conversational_agent"

    # --- Validación Final ---
    if decision not in AVAILABLE_NODES:
        print(f"ADVERTENCIA: Decisión inválida ('{decision}'). Forzando a '__end__'.")
        decision = "__end__"
    
    print(f"Decisión del Supervisor: Enviar a '{decision}'")
    
    return {"routing_decision": decision}
