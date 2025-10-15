# Contenido para: src/nodes/database_developer_node.py

from src.model import creative_llm
from src.tools.code_extractor import extract_and_save_code

def database_architech_node(state: dict) -> dict:
    """
    Agente que genera código para la capa de datos (SQL, NoSQL, scripts, etc.)
    basado en un análisis, la solicitud del usuario y el feedback de una revisión.
    Es agnóstico a la tecnología de base de datos.
    """
    print("---AGENTE: DESARROLLADOR DE LA CAPA DE DATOS---")

    analysis_result = state.get("analysis_result")
    feedback = state.get("review_feedback")
    user = state.get("user_input")
    
    prompt_additions = ""
    if feedback:
        existing_db_code = state.get("database_code", {})
        # Toma el primer fragmento de código encontrado, sea cual sea su lenguaje.
        first_code_snippet = next(iter(existing_db_code.values()), None)

        if first_code_snippet:
            prompt_additions = f"""
            **Feedback de la Revisión Anterior (Debes Corregirlo):**
            ---
            {feedback}
            ---
            
            **CÓDIGO EXISTENTE (MODIFICA ESTE CÓDIGO PARA INCORPORAR LAS CORRECCIONES):**
            ```
            {first_code_snippet}
            ```
            
            Por favor, genera la versión COMPLETA y CORREGIDA del código. No solo los cambios.
            """

    prompt = f"""
    Eres un experto desarrollador de la capa de datos. Tu tarea es generar el código o script necesario para la base de datos o sistema de almacenamiento de datos que se infiera de la solicitud. Puede ser SQL, un script para MongoDB (JavaScript), Cypher (Neo4j), un archivo JSON de configuración, etc.

    Te basarás en:
     - Análisis Multimodal: {analysis_result}
     - Solicitud del Usuario: {user}
    
    Si se proporciona código existente y feedback, DEBES modificar el código existente para aplicar las correcciones.

    **Instrucciones CRÍTICAS:**
    1.  Genera todo el código dentro de un único bloque delimitado.
    2.  **Usa un nombre de archivo descriptivo CON LA EXTENSIÓN CORRECTA** en el delimitador (ej. `create_tables.sql`, `insert_users.js`, `seed_data.json`).
    3.  **Elige el estilo de comentario correcto para los delimitadores** según el lenguaje del código que estás generando.
        - Para SQL: `-- --- create_tables.sql_CODE_START ---`
        - Para JavaScript/JSON: `// --- insert_users.js_CODE_START ---` o `/* --- insert_users.js_CODE_START --- */`
        - Para otros, usa el comentario de bloque o línea apropiado.
    4.  El código debe ser sintácticamente correcto y listo para ejecutarse en el entorno de destino.
    5.  No añadas explicaciones fuera del bloque de código delimitado.

    {prompt_additions}
    """
    response = creative_llm.invoke(prompt)
    full_code = response.content

    print("\n--- INICIO DE LA SALIDA DE DEPURACIÓN (LLM Response) ---")
    print(full_code)
    print("--- FIN DE LA SALIDA DE DEPURACIÓN ---\n")

    # Pasamos el contexto de la carpeta: este nodo siempre genera código de backend.
    extracted_code_dict = extract_and_save_code(full_code, default_folder="database")

    return {
        "db_schema": extracted_code_dict,
        "last_code_generated": "database",
        "review_feedback": None ,
        "supervisor_iterations": state.get("supervisor_iterations")+1
    }