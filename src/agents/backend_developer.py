# Contenido para: src/agents/backend_developer.py

from src.model import creative_llm

from src.tools.code_extractor import extract_and_save_code 
import os 
def backend_developer_node(state: dict) -> dict:
    print("---AGENTE: DESARROLLADOR BACKEND---")
    plan = state.get("dev_plan")
    if not plan or not plan.get("backend_task"):
        return {}

    tech = plan.get("backend_tech", "Python con FastAPI") # <-- Un default más específico
    task = plan.get("backend_task")
    feedback = state.get("review_feedback")
    
    prompt_additions = ""
    existing_code_prompt = ""
    # <-- CAMBIO CLAVE: Manejo de código existente igual que el frontend
    if feedback:
        existing_backend_code = state.get("backend_code", {})
        if isinstance(existing_backend_code, dict):
            full_existing_code = []
            for lang, code in existing_backend_code.items():
                full_existing_code.append(f"--- {lang.upper()} ---\n{code}")
            existing_code_prompt = "\n\n".join(full_existing_code)

        prompt_additions = f"""
        **Feedback de la Revisión Anterior (Debes Corregirlo):**
        ---
        {feedback}
        ---
        
        **CÓDIGO EXISTENTE (MODIFICA ESTE CÓDIGO PARA INCORPORAR LAS CORRECCIONES):**
        ```
        {existing_code_prompt}
        ```
        
        Por favor, genera la versión COMPLETA y CORREGIDA de todos los archivos de código necesarios. No solo los cambios.
        """

    # <-- CAMBIO CLAVE: Prompt mucho más estructurado, similar al del frontend
    prompt = f"""
    Eres un desarrollador de software senior experto en {tech}.
    Tu tarea es generar el código backend completo y funcional para la siguiente tarea.

    **Instrucciones CRÍTICAS:**
    1.  Genera el código en bloques separados y claramente delimitados. Por ejemplo, uno para el código principal de la aplicación (Python), otro para los requisitos (`requirements.txt`), y si es necesario, otro para el esquema de la base de datos (SQL).
    2.  Usa los siguientes delimitadores EXACTOS para cada bloque. Los nombres de los lenguajes/archivos deben estar en MINÚSCULAS:
        - Para Python: `<!--- python_code_start --->` y `<!--- python_code_end --->`
        - Para Requisitos: `<!--- requirements.txt_code_start --->` y `<!--- requirements.txt_code_end --->`
        - Para SQL: `<!--- sql_code_start --->` y `<!--- sql_code_end --->`
    3.  Asegúrate de que el código esté bien documentado con comentarios.
    4.  No añadas explicaciones fuera de los bloques de código delimitados.

    **Plan de Desarrollo y Tarea Asignada:**
    ---
    {plan}
    ---
    
    **Contexto General del Proyecto (de la solicitud del usuario):**
    ---
    {state.get('user_input', 'No se proporcionó contexto adicional.')}
    ---
    {prompt_additions}
    """
    response = creative_llm.invoke(prompt)
    full_code = response.content

    # --- PASO DE DEPURACIÓN ---
    print("\n--- SALIDA COMPLETA DEL LLM (PARA DEPURACIÓN) ---\n")
    print(full_code)
    print("\n--- FIN DE LA SALIDA DE DEPURACIÓN ---\n")

    # <-- CAMBIO CLAVE: Usar la herramienta de extracción
    # El delimitador para archivos backend será '<!--- {lang}_code_start --->'
    extracted_code_dict = extract_and_save_code(full_code, start_pattern=r"<!--- (\w+\.?\w+)_code_start --->", end_pattern=r"<!--- \1_code_end --->")
    
    return {
        "backend_code": extracted_code_dict, # <-- Devuelve un diccionario
        "last_code_generated": "backend",
        "review_feedback": None # ¡CLAVE! Limpiar el bucle de feedback.
    }