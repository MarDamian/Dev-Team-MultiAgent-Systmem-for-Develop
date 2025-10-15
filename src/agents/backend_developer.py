# Contenido para: src/agents/backend_developer.py

from src.model import creative_llm
from src.tools.code_extractor import extract_and_save_code 

def backend_developer_node(state: dict) -> dict:
    """
    Agente que genera el código de la aplicación backend en la tecnología especificada.
    Utiliza el plan, la tarea específica y el esquema de la base de datos como contexto.
    """
    print("---AGENTE: DESARROLLADOR BACKEND---")
    
    plan = state.get("dev_plan")
    if not plan or not plan.get("backend_task"):
        print("Advertencia: No se encontró un plan de backend válido. Omitiendo nodo.")
        return {}

    # --- Recopilación de contexto FLEXIBLE ---
    backend_tech = plan.get("backend_tech", "Python")
    db_tech = plan.get("db_tech", "la base de datos especificada")
    task = plan.get("backend_task")
    feedback = state.get("review_feedback")
    db_schema = state.get("db_schema", "No se proporcionó un esquema de base de datos específico. Asume un diseño apropiado.")
    
    prompt_additions = ""
    # --- CORRECCIÓN CLAVE ---
    if feedback:
        existing_backend_code = state.get("backend_code", {})
        existing_code_prompt = "" # Inicializar la variable
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
        **CÓDIGO EXISTENTE (MODIFICA ESTE CÓDIGO):**
        ```
        {existing_code_prompt}
        ```
        """

    # --- Construcción del Prompt Final y Corregido ---
    prompt = f"""
    Eres un desarrollador de software senior experto en {backend_tech}.
    Tu tarea es generar el código backend completo, funcional y bien documentado.

    **Instrucciones CRÍTICAS:**
    1.  Genera el código en bloques separados. El código principal debe estar en un bloque con el nombre de la tecnología (ej: 'python', 'javascript') y las dependencias en un bloque de gestor de paquetes (ej: 'requirements.txt', 'package.json').
    2.  Usa delimitadores como `<!--- python_code_start --->` o `<!--- package.json_code_start --->`.
    3.  No añadas explicaciones fuera de los bloques de código.
    4.  Tu código DEBE ser consistente con el modelo/esquema de la base de datos proporcionado.

    **Tarea Específica Asignada:**
    ---
    {task}
    ---
    
    **Esquema/Modelo de Base de Datos ({db_tech}) (DEBES SEGUIR ESTE DISEÑO):**
    ---
    {db_schema}
    ---
    {prompt_additions}
    """
    response = creative_llm.invoke(prompt)
    full_code = response.content

    print("\n--- SALIDA COMPLETA DEL LLM (PARA DEPURACIÓN) ---\n")
    print(full_code)
    print("\n--- FIN DE LA SALIDA DE DEPURACIÓN ---\n")

    extracted_code_dict = extract_and_save_code(full_code, default_folder="backend")
    
    return {
        "backend_code": extracted_code_dict,
        "last_code_generated": "backend",
        "review_feedback": None,
        "supervisor_iterations": state.get("supervisor_iterations")+1
    }