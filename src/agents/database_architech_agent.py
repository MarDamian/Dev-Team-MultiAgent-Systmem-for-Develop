# Contenido para: src/nodes/database_developer_node.py

from src.model import advanced_llm
from src.tools.code_extractor import extract_and_save_code
from src.tools.contract_manager import get_contracts_for_prompt
from src.tools.project_manager import get_active_project_id, get_project_path, ensure_project_folders
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
        # Asegurar que la carpeta database existe
        ensure_project_folders(project_id, ["database"])
        
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
    Eres un arquitecto de bases de datos senior con expertise profundo en {db_tech}.
Tu código es conocido por ser escalable, normalizado, optimizado y seguir las mejores prácticas de diseño de datos.

**TU MISIÓN:**
Generar código o scripts de base de datos completos, production-ready y profesionales que implementen EXACTAMENTE los requisitos especificados.


PLAN DE BASE DE DATOS
{db_task}


CONTRATOS DE DATOS DEFINIDOS

{data_contracts_text}

CONTEXTO ADICIONAL

- Análisis Multimodal: {analysis_result}
- Análisis de Interfaz: {ui_ux_spec}
- Solicitud del Usuario: {user}

{prompt_additions}

REQUISITOS TÉCNICOS CRÍTICOS (OBLIGATORIOS)

**1. DISEÑO Y ESTRUCTURA:**
   ✓ Normalización apropiada (3NF mínimo para SQL, denormalización justificada)
   ✓ Primary Keys en TODAS las tablas/colecciones
   ✓ Foreign Keys con ON DELETE/ON UPDATE apropiados (SQL)
   ✓ Índices en columnas frecuentemente consultadas
   ✓ Nombres descriptivos en inglés (snake_case para SQL, camelCase para NoSQL)
   ✓ Tipos de datos apropiados y restrictivos
   ✓ Constraints de integridad (NOT NULL, UNIQUE, CHECK)

**2. SEGURIDAD Y VALIDACIÓN:**
   ✓ NUNCA almacenar contraseñas en texto plano (campo para hash)
   ✓ Campos de auditoría (created_at, updated_at)
   ✓ Soft deletes donde sea apropiado (is_deleted, deleted_at)
   ✓ Validaciones a nivel de base de datos (CHECK constraints)
   ✓ Usuarios con privilegios mínimos necesarios

**3. ESCALABILIDAD Y PERFORMANCE:**
   ✓ Índices compuestos para queries frecuentes
   ✓ Particionamiento si es necesario para tablas grandes
   ✓ Tipos de datos eficientes (INT vs BIGINT, VARCHAR tamaño apropiado)
   ✓ Evitar columnas TEXT/BLOB donde no sean necesarias
   ✓ Considerar caching/materialized views para queries pesadas

**4. DOCUMENTACIÓN:**
   ✓ Comentarios SQL/NoSQL explicando propósito de tablas/campos complejos
   ✓ Descripción de relaciones entre entidades
   ✓ Ejemplos de datos donde sea útil

**5. TIPO DE TECNOLOGÍA ESPECÍFICA:**

   **Para SQL (PostgreSQL, MySQL, SQLite):**
   ✓ DDL completo (CREATE TABLE, ALTER TABLE si necesario)
   ✓ Foreign Keys con nombres descriptivos
   ✓ Índices con nombres descriptivos (idx_tabla_columna)
   ✓ Triggers solo si son esenciales
   ✓ Scripts de migración si hay versiones anteriores

   **Para NoSQL (MongoDB, Firebase):**
   ✓ Schemas/modelos con validación
   ✓ Relaciones embedded vs referenced justificadas
   ✓ Índices en campos de búsqueda frecuente
   ✓ Agregaciones optimizadas

   **Para archivos TXT/CSV:**
   ✓ Formato delimitado claro (coma, pipe |, tab)
   ✓ Header row con nombres de columnas
   ✓ Datos de ejemplo realistas
   ✓ Documentación del formato en comentarios
   ✓ Encoding UTF-8 especificado

   **Para Graph DB (Neo4j):**
   ✓ Nodos con labels y propiedades
   ✓ Relaciones tipadas
   ✓ Índices en propiedades de búsqueda
   ✓ Constraints de unicidad


 FORMATO DE SALIDA (ESTRICTAMENTE OBLIGATORIO)


**Genera el código en UN ÚNICO BLOQUE usando el formato correcto:**

**Para SQL:**
`-- --- schema.sql_CODE_START ---`
[código SQL completo]
`-- --- schema.sql_CODE_END ---`

**Para archivos TXT/CSV:**
`# --- users.txt_CODE_START ---`
[datos con formato delimitado]
`# --- users.txt_CODE_END ---`

**Para JavaScript/JSON (seeds, config):**
`// --- seed_data.js_CODE_START ---`
[código JavaScript o JSON]
`// --- seed_data.js_CODE_END ---`

**Para Python (ORM models):**
`// --- models.py_CODE_START ---`
[código Python]
`// --- models.py_CODE_END ---`

**ORGANIZACIÓN CON SUBDIRECTORIOS (OPCIONAL):**
   - Para organizar en carpetas: `-- --- migrations/001_initial.sql_CODE_START ---`
   - Ejemplos válidos:
     * `-- --- schemas/users.sql_CODE_START ---` (carpeta schemas)
     * `// --- seeds/initial_data.js_CODE_START ---` (carpeta seeds)
     * `# --- data/users.txt_CODE_START ---` (carpeta data)
     * `// --- models/user.py_CODE_START ---` (carpeta models)
   - ⚠️ NO uses rutas absolutas (/) ni navegación hacia atrás (..)

**REGLAS DE ORO:**
- ❌ NO añadas explicaciones fuera del bloque de código
- ❌ NO uses markdown para código (solo los delimitadores especificados)
- ❌ NO uses rutas absolutas (/path) ni relativas con .. (../path)
- ✅ Código sintácticamente correcto y ejecutable
- ✅ Nombre de archivo descriptivo CON EXTENSIÓN
- ✅ Usa subdirectorios para organizar scripts (migrations/, seeds/, etc.)
- ✅ Consistencia con los contratos de datos proporcionados


CHECKLIST FINAL ANTES DE GENERAR

Verifica mentalmente:
□ ¿Implementé TODOS los modelos de los contratos de datos?
□ ¿Todas las tablas tienen Primary Key?
□ ¿Las relaciones están correctamente definidas?
□ ¿Los índices cubren las queries esperadas?
□ ¿Los tipos de datos son apropiados?
□ ¿Hay campos de auditoría (timestamps)?
□ ¿Las contraseñas NO están en texto plano?
□ ¿El código es sintácticamente correcto?

**AHORA GENERA EL CÓDIGO DE BASE DE DATOS COMPLETO Y PROFESIONAL.**
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