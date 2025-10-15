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
    Tu tarea es generar el código completo y funcional para la siguiente tarea {task}, basándote en el plan y el feedback proporcionado.
    Si se proporciona código existente y feedback, DEBES modificar el código existente para aplicar las correcciones.

    **Instrucciones CRÍTICAS:**
1.  Genera el código en tres bloques separados y claramente delimitados: uno para HTML, uno para CSS y uno para JavaScript.
    2.  **Usa los nombres de archivo estándar y completos (incluyendo extensión) DENTRO de los delimitadores.**
        - Para HTML, usa el nombre de archivo `index.html`.
        - Para CSS, usa el nombre de archivo `style.css`.
        - Para JavaScript, usa el nombre de archivo `script.js`.
    3.  Usa el estilo de comentario apropiado para cada delimitador. Por ejemplo:
        - Para HTML: `<!--- index.html_CODE_START --->` y `<!--- index.html_CODE_END --->`
        - Para CSS: `/* --- style.css_CODE_START --- */` y `/* --- style.css_CODE_END --- */`
        - Para JavaScript: `// --- script.js_CODE_START ---` y `// --- script.js_CODE_END ---`
    4.  Asegúrate de que el archivo HTML (`index.html`) enlace correctamente a `./style.css` y `./script.js`.
    5.  No añadas explicaciones fuera de los bloques de código.

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
    extracted_code_dict = extract_and_save_code(full_code, default_folder="frontend")
    # Devolvemos todos los bloques de código y limpiamos el feedback
    return {
        "frontend_code": extracted_code_dict,
        "last_code_generated": "frontend",
        "review_feedback": None,
        "supervisor_iterations": state.get("supervisor_iterations")+1
    }
