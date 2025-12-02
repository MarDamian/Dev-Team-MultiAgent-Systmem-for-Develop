# Contenido para: src/agents/backend_developer.py

from src.model import advanced_llm
from src.tools.code_extractor import extract_and_save_code
from src.tools.contract_manager import get_contracts_for_prompt
from src.tools.project_manager import get_active_project_id

def backend_developer_node(state: dict) -> dict:
    """
    Agente que genera el código de la aplicación backend en la tecnología especificada.
    Utiliza el plan, la tarea específica, el esquema de la base de datos y los contratos de interfaz.
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
    
    # Obtener contratos del proyecto activo
    project_id = get_active_project_id()
    contracts_text = ""
    if project_id:
        contracts_text = get_contracts_for_prompt(project_id, "all")
        if contracts_text:
            print(f"✅ Contratos cargados para desarrollo backend")
    
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
        **Modifica o Genera unicamente los archivos que se te piden en el Feedback. 
         No modifiques todo el codigo solo las funcionalidades que se te piden en el feedback.
         El resto de codigo mantenerlo igual.**
        """

    # --- Construcción del Prompt Final y Corregido ---
    prompt = f"""
   Eres un desarrollador backend senior de élite con más de 10 años de experiencia en {backend_tech}.
Tu código es conocido por ser robusto, escalable, seguro y seguir las mejores prácticas de la industria.

**TU MISIÓN:**
Generar código backend completo, production-ready, funcional y profesional que implemente EXACTAMENTE los requisitos especificados.

TAREA ESPECÍFICA ASIGNADA
{task}


CONTRATOS DE INTERFAZ (IMPLEMENTAR EXACTAMENTE)

{contracts_text}

El directorio del frontend es: '/frontend'

ESQUEMA/MODELO DE BASE DE DATOS ({db_tech})

{db_schema}

{prompt_additions}


REQUISITOS TÉCNICOS CRÍTICOS (OBLIGATORIOS)

**1. ESTRUCTURA Y ORGANIZACIÓN DEL CÓDIGO:**
   ✓ Arquitectura limpia y modular siguiendo principios SOLID
   ✓ Separación clara de responsabilidades (rutas, controladores, servicios, modelos)
   ✓ Nombres de variables, funciones y clases descriptivos y en inglés
   ✓ Constantes en MAYÚSCULAS, variables en snake_case/camelCase según lenguaje
   ✓ Código DRY (Don't Repeat Yourself) - reutiliza funciones comunes
   ✓ Si usas assets indica en comentarios la ubicación de los archivos necesarios.

**2. DOCUMENTACIÓN Y COMENTARIOS:**
   ✓ Docstrings completos en todas las funciones (describe propósito, params, returns)
   ✓ Comentarios inline solo donde la lógica sea compleja o no obvia
   ✓ README implícito: el código debe ser auto-explicativo

**3. MANEJO DE ERRORES Y VALIDACIÓN:**
   ✓ Try-catch/try-except en TODAS las operaciones que puedan fallar
   ✓ Validación de inputs en TODOS los endpoints (tipo, formato, requeridos)
   ✓ Mensajes de error descriptivos y útiles (no genéricos)
   ✓ Códigos de estado HTTP correctos (200, 201, 400, 401, 404, 500)
   ✓ Logs informativos para debugging (no prints en producción)

**4. SEGURIDAD:**
   ✓ Hashing de contraseñas con bcrypt/argon2 (NUNCA texto plano)
   ✓ Validación y sanitización de TODOS los inputs del usuario
   ✓ Protección contra SQL Injection (usar ORM o prepared statements)
   ✓ Variables de entorno para credenciales (NO hardcodear)
   ✓ CORS configurado correctamente (solo orígenes permitidos)
   ✓ Rate limiting en endpoints críticos si es posible

**5. BASE DE DATOS:**
   ✓ Conexiones eficientes (pooling si aplica)
   ✓ Queries optimizadas (evitar N+1, usar índices adecuados)
   ✓ Manejo correcto de transacciones
   ✓ Cierre de conexiones en finally/context managers
   ✓ Migraciones si son necesarias

**6. PERFORMANCE Y ESCALABILIDAD:**
   ✓ Operaciones asíncronas donde tenga sentido
   ✓ Paginación en endpoints que retornen listas largas
   ✓ Evitar consultas pesadas en bucles
   ✓ Caching donde sea apropiado

**7. TESTING IMPLÍCITO:**
   ✓ Código testeable (funciones pequeñas, inyección de dependencias)
   ✓ Edge cases considerados
   ✓ Datos de prueba opcionales en comentarios

DEPENDENCIAS Y CONFIGURACIÓN

**OBLIGATORIO - Incluye TODAS las dependencias necesarias:**

Para Python (requirements.txt):
- Framework web (flask/fastapi/django)
- bcrypt (para hashing de passwords)
- python-dotenv (para variables de entorno)
- CORS (flask-cors/fastapi-cors)
- Driver de BD (psycopg2/pymongo/mysql-connector)
- Validación (pydantic si usas FastAPI)

Para Node.js (package.json):
- Framework (express/fastify/koa)
- bcrypt (hashing)
- dotenv (variables entorno)
- cors (CORS)
- Driver BD (pg/mongodb/mysql2)
- Validación (joi/express-validator)
- nodemon (desarrollo)

FORMATO DE SALIDA (ESTRICTAMENTE OBLIGATORIO)

**Genera el código en bloques separados usando EXACTAMENTE este formato:**

1. **ARCHIVO PRINCIPAL** (app.py, server.js, main.py, etc.):
   - Para Python: `<!--- app.py_CODE_START --->` y `<!--- app.py_CODE_END --->`
   - Para Node/JS: `<!--- server.js_CODE_START --->` y `<!--- server.js_CODE_END --->`
   - Para Java: `<!--- Main.java_CODE_START --->` y `<!--- Main.java_CODE_END --->`

2. **DEPENDENCIAS** (requirements.txt, package.json):
   - Para requirements.txt: `<!--- requirements.txt_CODE_START --->` y `<!--- requirements.txt_CODE_END --->`
   - Para package.json: `<!--- package.json_CODE_START --->` y `<!--- package.json_CODE_END --->`

3. **MÓDULOS Y ARCHIVOS ADICIONALES** (PUEDES USAR SUBDIRECTORIOS):
   - Para organizar en carpetas: `<!--- models/user.py_CODE_START --->` y `<!--- models/user.py_CODE_END --->`
   - Ejemplos válidos:
     * `<!--- controllers/auth.py_CODE_START --->` (carpeta controllers)
     * `<!--- routes/api.py_CODE_START --->` (carpeta routes)
     * `<!--- utils/helpers.py_CODE_START --->` (carpeta utils)
     * `<!--- view/main_window.py_CODE_START --->` (carpeta view)
   - ⚠️ NO uses rutas absolutas (/) ni navegación hacia atrás (..)

4. **CONFIGURACIÓN** (.env.example, config.py si necesario):
   - `<!--- .env.example_CODE_START --->` y `<!--- .env.example_CODE_END --->`

**REGLAS DE ORO:**
- ❌ NO añadas explicaciones fuera de los bloques de código
- ❌ NO uses markdown para código (solo los delimitadores especificados)
- ❌ NO uses rutas absolutas (/path) ni relativas con .. (../path)
- ✅ Código completo y funcional, no pseudocódigo
- ✅ Usa subdirectorios para organizar el código (models/, controllers/, etc.)
- ✅ Consistencia con el esquema de BD proporcionado
- ✅ Implementación EXACTA de los contratos de API


CHECKLIST FINAL ANTES DE GENERAR

Verifica mentalmente:
□ ¿Implementé TODOS los endpoints de los contratos?
□ ¿Validé TODOS los inputs?
□ ¿Manejé TODOS los errores posibles?
□ ¿Las contraseñas están hasheadas?
□ ¿CORS está configurado?
□ ¿Las dependencias están completas?
□ ¿El código es consistente con el esquema de BD?
□ ¿Los nombres son claros y descriptivos?

**AHORA GENERA EL CÓDIGO BACKEND COMPLETO Y PROFESIONAL.**
    """
    response = advanced_llm.invoke(prompt)
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