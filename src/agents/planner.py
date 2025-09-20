# Contenido para: src/agents/planner.py

import json
from src.model import analytical_llm

def planner_node(state: dict) -> dict:
    print("---AGENTE: PLANIFICADOR DE PROYECTO---")

    # --- Lógica de Selección de Contexto ---
    # El planificador ahora es más inteligente. Prioriza la especificación de UI/UX si existe,
    # de lo contrario, utiliza la solicitud original del usuario.
    if state.get("ui_ux_spec"):
        context_source = "Especificación Técnica de UI/UX"
        context_content = state["ui_ux_spec"]
    else:
        context_source = "Solicitud Original del Usuario"
        context_content = state["user_input"]

    prompt = f"""
    Eres un jefe de proyecto técnico. Tu tarea es crear un plan de desarrollo detallado basado en la siguiente información.

    **{context_source}:**
    ---
    {context_content}
    ---

    Tu plan debe indicar qué se necesita y las tecnologías a usar.

    **IMPORTANTE:** Tu salida debe ser un objeto JSON con la siguiente estructura y NADA MÁS:
    - `plan_type`: "frontend", "backend", "both" o "none".
    - `frontend_task`: (string | null) Una descripción clara y concisa de la tarea para el desarrollador frontend.
    - `frontend_tech`: (string | null) La tecnología específica para el frontend (ej. "HTML, CSS y JavaScript").
    - `backend_task`: (string | null) Una descripción clara de la tarea para el desarrollador backend.
    - `backend_tech`: (string | null) La tecnología específica para el backend (ej. "Python con Flask").

    **REGLA CRÍTICA:** Adhiérete ESTRICTAMENTE a las tecnologías solicitadas en la petición del usuario. Si el usuario pide "HTML, CSS y JS", el campo `frontend_tech` debe ser exactamente ese. No sugieras frameworks, librerías o herramientas de construcción a menos que se pidan explícitamente.
    """
    
    response = analytical_llm.invoke(prompt)
    
    try:
        # Limpiar la respuesta para asegurar que sea un JSON válido
        json_response = response.content.strip().replace("```json", "").replace("```", "").strip()
        plan = json.loads(json_response)
        print(f"Plan de desarrollo generado: {plan}")
        return {"dev_plan": plan}
    except json.JSONDecodeError:
        print("Error: El planificador no devolvió un JSON válido.")
        # Devolvemos un plan vacío para evitar que el grafo se rompa
        return {"dev_plan": {"plan_type": "none"}}
