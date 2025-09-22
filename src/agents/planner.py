import json
from src.model import analytical_llm
from src.rag_retriever import retrieve_context

def planner_node(state: dict) -> dict:
    print("---AGENTE: PLANIFICADOR DE PROYECTO---")

    if state.get("ui_ux_spec"):
        context_source = "Especificación Técnica de UI/UX"
        context_content = state["ui_ux_spec"]
    else:
        context_source = "Solicitud Original del Usuario"
        context_content = state["user_input"]

    # --- Recuperación de Contexto con RAG ---
    # Llama a la función del otro archivo. No sabe ni le importa cómo funciona por dentro.
    retrieved_info = retrieve_context(context_content)

    prompt = f"""
    Eres un jefe de proyecto técnico. Tu tarea es crear un plan de desarrollo detallado basado en la siguiente información.

    **Contexto Relevante de la Base de Conocimientos:**
    ---
    {retrieved_info}
    ---

    **{context_source}:**
    ---
    {context_content}
    ---

    Basado en el contexto y la solicitud, tu plan debe indicar qué se necesita y las tecnologías a usar,
    tambien aclara de forma resumida que vas a aplicar segun tu Base de Conocimiento.

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
        json_response = response.content.strip().replace("```json", "").replace("```", "").strip()
        plan = json.loads(json_response)
        print(f"Plan de desarrollo generado: {plan}")
        return {"dev_plan": plan}
    except json.JSONDecodeError:
        print("Error: El planificador no devolvió un JSON válido.")
        return {"dev_plan": {"plan_type": "none"}}

