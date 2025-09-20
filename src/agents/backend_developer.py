# Contenido para: src/agents/backend_developer.py

from src.model import creative_llm # <-- CAMBIO AQUÍ
from src.tools import save_code_to_file

def backend_developer_node(state: dict) -> dict:
    print("---AGENTE: DESARROLLADOR BACKEND---")
    plan = state.get("dev_plan")
    if not plan or not plan.get("backend_task"):
        return {}

    tech = plan.get("backend_tech", "lenguaje solicitado") # <-- CAMBIO AQUÍ
    task = plan.get("backend_task")
    feedback = state.get("review_feedback")

    prompt_additions = ""
    if feedback:
        # Si hay feedback, incluimos el código existente para que el LLM lo modifique.
        existing_backend_code = state.get("backend_code", "")
        prompt_additions = f"""
        **Feedback de la Revisión Anterior (Debes Corregirlo):**
        ---
        {feedback}
        ---
        
        **CÓDIGO EXISTENTE (MODIFICA ESTE CÓDIGO PARA INCORPORAR LAS CORRECCIONES):**
        ```
        {existing_backend_code}
        ```
        
        Por favor, genera la versión COMPLETA y CORREGIDA del código. No solo los cambios.
        """

    prompt = f"""
    Eres un desarrollador de software senior experto en {tech}.
    Tu tarea es escribir una solución de código completa y bien documentada para la siguiente tarea.
    Asegúrate de incluir comentarios en el código para explicar la lógica y la estructura.
    Si se proporciona código existente y feedback, DEBES modificar el código existente para aplicar las correcciones.

    Tarea Asignada: "{task}"
    Contexto General del Proyecto (de la solicitud del usuario): "{state.get('user_input', '')}"
    
    Genera únicamente el código en {tech}. No añadas explicaciones fuera del código.
    {prompt_additions}
    """
    response = creative_llm.invoke(prompt)
    print(f"Código backend generado en {tech}.")
    # Limpiamos el código por si el LLM añade "markdown"
    code = response.content.strip().replace(f"```{tech.lower().split()}", "").replace("```", "").strip()
    
    # Guardar el código en un archivo Python
    save_code_to_file(code, "py")
    
    return {"backend_code": code, "last_code_generated": "backend"}
