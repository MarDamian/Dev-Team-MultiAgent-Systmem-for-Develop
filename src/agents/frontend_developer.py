# Contenido para: src/agents/frontend_developer.py

from src.model import creative_llm
from src.tools.code_extractor import extract_and_save_code

def frontend_developer_node(state: dict) -> dict:
    print("---AGENTE: DESARROLLADOR FRONTEND---")
    plan = state.get("dev_plan")
    if not plan or not plan.get("frontend_task"):
        return {}

    tech = plan.get("frontend_tech", "tecnología solicitada") 
    task = plan.get("frontend_task")

    feedback = state.get("review_feedback")
    
    prompt_additions = ""
    existing_code_prompt = ""
    if feedback:
        # Si hay feedback, incluimos el código existente para que el LLM lo modifique.
        existing_frontend_code = state.get("frontend_code", {})
        if isinstance(existing_frontend_code, dict):
            full_existing_code = []
            for lang, code in existing_frontend_code.items():
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
        
        Por favor, genera la versión COMPLETA y CORREGIDA del código. No solo los cambios.
        """

    prompt = f"""
    Eres un desarrollador de software senior experto en {tech}.
    Tu tarea es generar el código completo y funcional para la siguiente tarea, basándote en el plan y el feedback proporcionado.
    Si se proporciona código existente y feedback, DEBES modificar el código existente para aplicar las correcciones.

    **Instrucciones CRÍTICAS:**
    1.  Genera el código en tres bloques separados y claramente delimitados: uno para HTML, uno para CSS y uno para JavaScript.
    2.  Usa los siguientes delimitadores EXACTOS para cada bloque:
        - Para HTML: `<!--- HTML_CODE_START --->` y `<!--- HTML_CODE_END --->`
        - Para CSS: `/* --- CSS_CODE_START --- */` y `/* --- CSS_CODE_END --- */`
        - Para JavaScript: `// --- JS_CODE_START ---` y `// --- JS_CODE_END ---`
    3.  Asegúrate de que el archivo HTML enlace correctamente a `style.css` y `script.js` .
    4.  No añadas explicaciones fuera de los bloques de código.

    **Plan de Desarrollo y Tarea Asignada:**
    ---
    {plan}
    ---

    **Especificación Técnica de UI/UX (Debes seguirla al pie de la letra):**
    ---
    {state.get('ui_ux_spec', 'No se proporcionó una especificación detallada.')}
    ---
    {prompt_additions}
    """
    response = creative_llm.invoke(prompt)
    full_code = response.content

    # --- PASO DE DEPURACIÓN ---
    # Imprimimos la salida completa del LLM para inspeccionar los delimitadores.
    print("\n--- SALIDA COMPLETA DEL LLM (PARA DEPURACIÓN) ---\n")
    print(full_code)
    print("\n--- FIN DE LA SALIDA DE DEPURACIÓN ---\n")

    # Usar la nueva herramienta para extraer y guardar el código
    output_code = extract_and_save_code(full_code)
    
    # Devolvemos todos los bloques de código y limpiamos el feedback
    return {
        "frontend_code": output_code,
        "last_code_generated": "frontend",
        "review_feedback": None # ¡CLAVE! Limpiar el bucle.
    }
