# Contenido para: src/agents/frontend_developer.py

from src.model import advanced_llm
from src.tools.code_extractor import extract_and_save_code
from src.tools.contract_manager import get_contracts_for_prompt
from src.tools.project_manager import get_active_project_id

def frontend_developer_node(state: dict) -> dict:
    """
    Agente que genera el código de la aplicación frontend en la tecnología especificada.
    Utiliza el plan, la tarea específica, el diseño UI/UX y los contratos de API del backend.
    """
    print("---AGENTE: DESARROLLADOR FRONTEND---")
    
    plan = state.get("dev_plan")
    if not plan or not plan.get("frontend_task"):
        print("Advertencia: No se encontró un plan de frontend válido. Omitiendo nodo.")
        return {}

    # --- Recopilación de contexto ---
    frontend_tech = plan.get("frontend_tech", "HTML, CSS y JavaScript")
    task = plan.get("frontend_task")
    backend_port = plan.get("backend_port", 5000)  # Puerto por defecto
    feedback = state.get("review_feedback")
    ui_ux_spec = state.get("ui_ux_spec", "No se proporcionó especificación de UI/UX. Crea una interfaz limpia y moderna.")
    
    # Obtener contratos del proyecto activo
    project_id = get_active_project_id()
    contracts_text = ""
    if project_id:
        # Solo obtener contratos de API para el frontend
        contracts_text = get_contracts_for_prompt(project_id, "api")
        if contracts_text:
            print(f"✅ Contratos de API cargados para desarrollo frontend")
    
    prompt_additions = ""
    # Si hay feedback, incluir código existente
    if feedback:
        existing_frontend_code = state.get("frontend_code", {})
        existing_code_prompt = ""
        if isinstance(existing_frontend_code, dict):
            full_existing_code = []
            for filename, code in existing_frontend_code.items():
                full_existing_code.append(f"--- {filename} ---\n{code}")
            
            existing_code_prompt = "\n\n".join(full_existing_code)

        prompt_additions = f"""
        **Feedback de la Revisión Anterior (Debes Corregirlo):**
        ---
        {feedback}
        ---
        **CÓDIGO EXISTENTE (MODIFICA ESTE CÓDIGO):**
        ```
        {existing_code_prompt}
        ```
        """

    # --- Construcción del Prompt ---
    prompt = f"""
    Eres un desarrollador frontend senior experto en {frontend_tech}.
    Tu tarea es generar el código frontend completo, funcional y bien documentado.

    **Instrucciones CRÍTICAS:**
    1.  Genera el código en bloques separados para cada archivo (HTML, CSS, JavaScript).
        Usa los nombres de archivo estándar y completos (incluyendo extensión) DENTRO de los delimitadores.
    2.  Usa el estilo de comentario apropiado para cada delimitador:
        - Para HTML: `<!--- index.html_CODE_START --->`  y `<!--- index.html_CODE_END --->`
        - Para CSS: `/* --- style.css_CODE_START --- */` y `/* --- style.css_CODE_END --- */`
        - Para JavaScript: `// --- script.js_CODE_START ---` y `// --- script.js_CODE_END ---`
    3.  No añadas explicaciones fuera de los bloques de código.
    4.  **IMPORTANTE:** Si hay contratos de API definidos, DEBES consumir EXACTAMENTE esos endpoints con los schemas especificados.
    5.  **CONFIGURACIÓN DE BACKEND URL:**
        - El backend corre en el puerto {backend_port}
        - En JavaScript, define la URL base del backend como: `const BASE_URL = 'http://localhost:{backend_port}';`
        - Usa esta constante para todas las llamadas fetch a los endpoints del backend
        - Ejemplo: `fetch(\`${{BASE_URL}}/api/login\`, {{...}})`
    6.  El código debe ser responsive y seguir las mejores prácticas de UI/UX.

    **Tarea Específica Asignada:**
    ---
    {task}
    ---
    
    **CONTRATOS DE API DEL BACKEND (DEBES CONSUMIR ESTOS ENDPOINTS):**
    ---
    {contracts_text if contracts_text else "No hay contratos de API definidos. Implementa según la tarea."}
    ---
    
    **Especificación de UI/UX:**
    ---
    {ui_ux_spec}
    ---
    {prompt_additions}
    """
    
    response = advanced_llm.invoke(prompt)
    full_code = response.content

    print("\n--- SALIDA COMPLETA DEL LLM (PARA DEPURACIÓN) ---\n")
    print(full_code)
    print("\n--- FIN DE LA SALIDA DE DEPURACIÓN ---\n")

    extracted_code_dict = extract_and_save_code(full_code, default_folder="frontend")
    
    return {
        "frontend_code": extracted_code_dict,
        "last_code_generated": "frontend",
        "review_feedback": None,
        "supervisor_iterations": state.get("supervisor_iterations")+1
    }
