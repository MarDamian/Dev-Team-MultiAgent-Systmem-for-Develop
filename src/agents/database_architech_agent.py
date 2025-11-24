# Contenido para: src/nodes/database_developer_node.py

from src.model import advanced_llm
from src.tools.code_extractor import extract_and_save_code
from src.tools.contract_manager import get_contracts_for_prompt
from src.tools.project_manager import get_active_project_id, get_project_path
import os

def database_architech_node(state: dict) -> dict:
    """
    Agente que genera código para la capa de datos (SQL, NoSQL, scripts, archivos TXT, etc.)
    basado en el plan de desarrollo, contratos de datos y la solicitud del usuario.
    Es agnóstico a la tecnología de base de datos.
    """
    print("---AGENTE: DESARROLLADOR DE LA CAPA DE DATOS---")

    analysis_result = state.get("analysis_result", "No disponible")
    ui_ux_spec = state.get("ui_ux_spec", "No disponible")
    feedback = state.get("review_feedback")
    user = state.get("user_input")
    dev_plan = state.get("dev_plan", {})
    
    # Obtener plan de base de datos y contratos
    db_task = dev_plan.get("db_task", "")
    db_tech = dev_plan.get("db_tech", "")
    
    # Obtener contratos de datos del proyecto activo
    project_id = get_active_project_id()
    data_contracts_text = ""
    
    if project_id:
        data_contracts_text = get_contracts_for_prompt(project_id, "data")
        if data_contracts_text:
            print(f"✅ Contratos de datos cargados para el diseño de base de datos.")
    
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
    Eres un experto desarrollador de la capa de datos. Tu tarea es generar el código o script necesario para la base de datos o sistema de almacenamiento de datos según el plan de desarrollo.

    **PLAN DE BASE DE DATOS:**
    {db_task}
    
    **TECNOLOGÍA A USAR:**
    {db_tech}
    
    **CONTRATOS DE DATOS DEFINIDOS:**
    ---
    {data_contracts_text if data_contracts_text else "No hay contratos de datos definidos."}
    ---

    Te basarás en:
     - Análisis Multimodal(Opcional): {analysis_result}
     - Análisis de Interfaz(Opcional): {ui_ux_spec}
     - Solicitud del Usuario: {user}
    
    Si se proporciona código existente y feedback, DEBES modificar el código existente para aplicar las correcciones.

    **Instrucciones CRÍTICAS:**
    1.  Genera todo el código dentro de un único bloque delimitado.
    2.  **Usa un nombre de archivo descriptivo CON LA EXTENSIÓN CORRECTA** en el delimitador.
        - Para SQL: `create_tables.sql`, `schema.sql`
        - Para archivos TXT: `users.txt`, `data.txt` (usa formato delimitado como CSV o pipe-separated)
        - Para JavaScript/JSON: `insert_users.js`, `seed_data.json`
        - Para otros, usa la extensión apropiada
    3.  **Elige el estilo de comentario correcto para los delimitadores** según el lenguaje:
        - Para SQL: `-- --- create_tables.sql_CODE_START ---`
        - Para TXT: `# --- users.txt_CODE_START ---` (o sin comentario si es datos puros)
        - Para JavaScript/JSON: `// --- insert_users.js_CODE_START ---`
    4.  **Si la tecnología es "TXT files" o archivos de texto plano:**
        - Genera la estructura del archivo con encabezados o líneas de ejemplo
        - Usa delimitadores claros (coma, pipe |, tab)
        - Incluye comentarios sobre el formato si es necesario
    5.  El código debe ser sintácticamente correcto y listo para usar.
    6.  **IMPORTANTE:** Si el plan menciona archivos TXT específicos (ej. users.txt), DEBES generarlos.
    7.  No añadas explicaciones fuera del bloque de código delimitado.

    {prompt_additions}
    """
    response = advanced_llm.invoke(prompt)
    full_code = response.content

    print("\n--- INICIO DE LA SALIDA DE DEPURACIÓN (LLM Response) ---")
    print(full_code)
    print("--- FIN DE LA SALIDA DE DEPURACIÓN ---\n")

    # Pasamos el contexto de la carpeta: este nodo siempre genera código de backend.
    extracted_code_dict = extract_and_save_code(full_code, default_folder="database")
    
    # Si no se generó ningún archivo pero el plan requiere archivos TXT, crear archivo vacío
    if project_id and not extracted_code_dict and "txt" in db_tech.lower():
        print("⚠️ No se generó código. Creando archivo TXT vacío según plan...")
        project_path = get_project_path(project_id)
        database_path = os.path.join(project_path, "database")
        os.makedirs(database_path, exist_ok=True)
        
        # Crear archivo vacío con estructura básica
        txt_file_path = os.path.join(database_path, "users.txt")
        with open(txt_file_path, 'w', encoding='utf-8') as f:
            f.write("# Archivo de datos de usuarios\n")
            f.write("# Formato: username|password_hash\n")
            f.write("# Ejemplo: admin|$2b$12$...\n")
        
        extracted_code_dict = {"users.txt": "# Archivo de datos creado"}
        print(f"✅ Archivo TXT creado: {txt_file_path}")

    return {
        "db_schema": extracted_code_dict,
        "last_code_generated": "database",
        "review_feedback": None ,
        "supervisor_iterations": state.get("supervisor_iterations")+1
    }