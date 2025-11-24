import json
from src.model import analytical_llm
from src.rag_retriever import retrieve_context
from src.tools.project_manager import create_project, set_active_project
from src.tools.contract_manager import define_api_contract, define_data_contract

def planner_node(state: dict) -> dict:
    print("---AGENTE: PLANIFICADOR DE PROYECTO---")


    context_ui_ux = state.get("ui_ux_spec")
    context_user = state.get("user_input")
    context_media= state.get("analysis_result")

    # --- Recuperación de Contexto con RAG ---
 
    retrieved_info = retrieve_context(context_user)

    prompt = f"""
Eres un jefe de proyecto técnico senior con 15+ años de experiencia en arquitectura de software,
análisis de requisitos y planificación de proyectos. Eres conocido por crear planes precisos,
realistas y técnicamente sólidos.

**TU MISIÓN:**
Analizar la solicitud del usuario y generar un plan de desarrollo detallado en formato JSON,
incluyendo un PRD (Product Requirements Document) implícito con todos los requisitos técnicos.


CONTEXTO RELEVANTE DE LA BASE DE CONOCIMIENTOS

{retrieved_info}

INFORMACIÓN DISPONIBLE PARA EL ANÁLISIS

**SOLICITUD DEL USUARIO:**
{context_user}

**CONTEXTO DE INTERFAZ (Opcional):**
{context_ui_ux}

**CONTEXTO MULTIMEDIA (Opcional):**
{context_media}

PROCESO DE ANÁLISIS (SIGUE ESTOS PASOS)

**PASO 1: ANÁLISIS DE REQUISITOS**
- Identifica el objetivo principal del proyecto
- Extrae funcionalidades explícitas mencionadas
- Infiere funcionalidades implícitas necesarias
- Identifica restricciones técnicas o de negocio
- Determina audiencia objetivo y casos de uso

**PASO 2: DECISIÓN DE ARQUITECTURA**
- Evalúa si necesita frontend, backend, base de datos o combinación
- Aplica las reglas de decisión (ver abajo)
- Justifica cada decisión técnica con principios de la base de conocimientos

**PASO 3: SELECCIÓN DE TECNOLOGÍAS**
- Elige tecnologías apropiadas según requisitos
- Considera complejidad, escalabilidad y mantenibilidad
- Usa tecnologías modernas y bien soportadas
- Justifica selecciones con referencias a buenas prácticas

**PASO 4: DEFINICIÓN DE CONTRATOS (SI APLICA)**
- Define endpoints de API con schemas completos
- Define modelos de datos con todos los campos
- Asegura consistencia entre frontend y backend
- Especifica códigos de estado HTTP apropiados

REGLAS DE DECISIÓN (APLICAR ESTRICTAMENTE EN ORDEN)

**REGLA 1: SIMPLIFICACIÓN - FRONTEND ONLY**
Condiciones (TODAS deben cumplirse):
□ La funcionalidad puede ejecutarse completamente en el cliente
□ NO requiere almacenamiento persistente en servidor
□ NO requiere autenticación/autorización
□ NO requiere procesamiento pesado del lado servidor
□ NO requiere compartir datos entre usuarios
□ Ejemplos: landing pages, calculadoras, visualizadores, juegos simples

→ Si se cumplen todas: `plan_type: "frontend-only"`
→ Completar SOLO: frontend_task, frontend_tech
→ Resto en null

**REGLA 2: BASE DE DATOS ÚNICAMENTE**
Condiciones:
□ Solicitud explícita de diseño de BD
□ Solo pide esquema, modelo de datos o estructura
□ NO pide implementación de aplicación

→ Si se cumple: `plan_type: "database-only"`
→ Completar SOLO: db_task, db_tech
→ Resto en null

**REGLA 3: BACKEND ONLY**
Condiciones (UNA o más se cumple):
□ Solicitud explícita de API REST/GraphQL
□ Menciona tecnología backend específica (Python, Node.js, Java, etc.)
□ Requiere lógica de servidor sin interfaz gráfica
□ Es un servicio, microservicio o API
□ Juego o programa de consola simple

→ Si se cumple: `plan_type: "backend-only"`
→ Completar: backend_task, backend_tech, backend_port
→ Si necesita BD: db_task, db_tech
→ frontend en null

**REGLA 4: FULLSTACK**
Condiciones (UNA o más se cumple):
□ Requiere interfaz de usuario Y lógica de servidor
□ Necesita autenticación/autorización
□ Necesita almacenamiento persistente Y interfaz
□ Aplicación multiusuario con UI
□ CRUD completo con interfaz web

→ Si se cumple: `plan_type: "fullstack"`
→ Completar: frontend_task, frontend_tech, backend_task, backend_tech, backend_port
→ Si necesita BD: db_task, db_tech
→ OBLIGATORIO: api_contracts, data_contracts

**REGLA 5: COORDINACIÓN FULLSTACK (Solo si plan_type es "fullstack")**
□ Backend Task debe listar endpoints explícitamente
□ Backend Port debe especificarse (Flask: 5000, Express: 3000, Django: 8000)
□ Frontend Task debe mencionar consumo de endpoints específicos
□ API Contracts deben estar completos y detallados
□ Data Contracts deben tener todos los campos requeridos

ESTRUCTURA JSON ESPERADA (FORMATO EXACTO)

Tu salida debe ser ÚNICAMENTE un objeto JSON con esta estructura:

{{
  "project_name": "Nombre Descriptivo del Proyecto",
  "plan_type": "frontend-only | backend-only | database-only | fullstack",
  
  "frontend_task": "string detallado | null",
  "frontend_tech": "string específico | null",
  
  "backend_task": "string detallado | null",
  "backend_tech": "string específico | null",
  "backend_port": number | null,
  
  "db_task": "string detallado | null",
  "db_tech": "string específico | null",
  
  "api_contracts": [
    {{
      "endpoint": "/api/ruta",
      "method": "GET|POST|PUT|DELETE",
      "description": "Descripción clara del propósito",
      "request_schema": {{
        "campo1": "tipo (string, number, boolean, object, array)",
        "campo2": "tipo"
      }},
      "response_schema": {{
        "campo1": "tipo",
        "campo2": "tipo"
      }},
      "status_codes": [200, 400, 401, 404, 500]
    }}
  ] | null,
  
  "data_contracts": [
    {{
      "model_name": "NombreDelModelo",
      "description": "Descripción del modelo",
      "fields": {{
        "campo1": {{
          "type": "tipo (string, integer, boolean, date, etc.)",
          "required": true|false,
          "unique": true|false,
          "description": "Descripción del campo"
        }}
      }}
    }}
  ] | null
}}

GUÍA PARA ESCRIBIR TAREAS DE CALIDAD

**ESTRUCTURA DE UNA TAREA EXCELENTE:**

1. **Descripción General** (1-2 líneas)
   - Qué se va a construir

2. **Requisitos Funcionales** (Lista detallada)
   - Funcionalidad 1: Descripción específica
   - Funcionalidad 2: Descripción específica
   - [etc.]

3. **Requisitos Técnicos**
   - Framework/librerías a usar
   - Patrones de diseño recomendados
   - Consideraciones de seguridad
   - Consideraciones de performance

4. **Especificaciones de Integración** (si aplica)
   - Endpoints a implementar/consumir
   - Formato de datos
   - Manejo de errores esperado

5. **Justificación Técnica**
   (**Justificación:** Según [principio de base de conocimientos], se recomienda
   [decisión técnica] porque [razón]. Esto garantiza [beneficio].)

**EJEMPLO DE TAREA BACKEND DE CALIDAD:**

"Implementar API REST para sistema de autenticación y gestión de usuarios.

Requisitos Funcionales:
- Registro de usuarios con validación de email y password
- Login con generación de JWT
- Endpoints protegidos con middleware de autenticación
- CRUD completo de perfiles de usuario
- Logout con invalidación de token

Requisitos Técnicos:
- Usar Flask con Flask-JWT-Extended
- Hashing de passwords con bcrypt (12 rounds mínimo)
- Validación de inputs con schemas (marshmallow o similar)
- Manejo de errores con códigos HTTP apropiados
- CORS configurado para localhost:3000
- Variables de entorno para SECRET_KEY y DATABASE_URL

Integración:
- Implementar endpoints: POST /api/auth/register, POST /api/auth/login,
  POST /api/auth/logout, GET /api/users/profile, PUT /api/users/profile
- Responder con JSON en formato: {{success: bool, data: object, message: string}}
- Códigos de estado: 200 (éxito), 201 (creado), 400 (validación), 401 (no autorizado), 500 (error servidor)

(**Justificación:** Según las mejores prácticas de seguridad en APIs REST,
se utiliza JWT para autenticación stateless y bcrypt con 12 rounds para
hashing de contraseñas. Esto garantiza seguridad sin comprometer performance.
La separación de concerns mediante middleware permite código mantenible y testeable.)"

 CHECKLIST ANTES DE GENERAR

□ ¿Analicé completamente la solicitud del usuario?
□ ¿Identifiqué todas las funcionalidades necesarias (explícitas e implícitas)?
□ ¿Apliqué las reglas de decisión correctamente?
□ ¿El plan_type refleja exactamente los campos completados?
□ ¿Las tareas son específicas, detalladas y accionables?
□ ¿Incluí justificaciones técnicas con referencias?
□ ¿Las tecnologías seleccionadas son apropiadas y modernas?
□ ¿Los contratos están completos con todos los campos necesarios?
□ ¿El JSON es válido y sigue la estructura exacta?
□ ¿No hay texto fuera del JSON?

INSTRUCCIONES FINALES

1. Analiza toda la información proporcionada
2. Aplica las reglas de decisión en orden
3. Consulta la base de conocimientos para justificaciones
4. Genera el JSON completo con todas las especificaciones
5. Valida que el JSON sea sintácticamente correcto
6. NO añadas texto fuera del JSON

**AHORA GENERA EL PLAN DE DESARROLLO COMPLETO EN FORMATO JSON.**
    """

    response = analytical_llm.invoke(prompt)
    
    try:
        json_response = response.content.strip().replace("```json", "").replace("```", "").strip()
        plan = json.loads(json_response)
        print(f"Plan de desarrollo generado: {plan}")
        
        # --- CREAR PROYECTO Y CONTRATOS ---
        project_name = plan.get("project_name", "Proyecto Sin Nombre")
        plan_type = plan.get("plan_type", "frontend-only")
        
        # Recopilar tecnologías
        technologies = {}
        if plan.get("frontend_tech"):
            technologies["frontend"] = plan["frontend_tech"]
        if plan.get("backend_tech"):
            technologies["backend"] = plan["backend_tech"]
        if plan.get("db_tech"):
            technologies["database"] = plan["db_tech"]
        
        # Crear proyecto
        project_id = create_project(
            name=project_name,
            plan_type=plan_type,
            technologies=technologies,
            description=context_user[:200]  # Primeros 200 caracteres de la solicitud
        )
        
        # Establecer como proyecto activo
        set_active_project(project_id)
        
        # Definir contratos si existen
        api_contracts_list = []
        data_contracts_list = []
        
        if plan.get("api_contracts"):
            for contract in plan["api_contracts"]:
                define_api_contract(
                    project_id=project_id,
                    endpoint=contract.get("endpoint", "/api/unknown"),
                    method=contract.get("method", "GET"),
                    request_schema=contract.get("request_schema", {}),
                    response_schema=contract.get("response_schema", {}),
                    status_codes=contract.get("status_codes", [200]),
                    description=contract.get("description", "")
                )
                api_contracts_list.append(contract)
        
        if plan.get("data_contracts"):
            for contract in plan["data_contracts"]:
                define_data_contract(
                    project_id=project_id,
                    model_name=contract.get("model_name", "UnknownModel"),
                    fields=contract.get("fields", {}),
                    description=contract.get("description", "")
                )
                data_contracts_list.append(contract)
        
        print(f"✅ Proyecto creado: {project_id}")
        print(f"   Contratos de API: {len(api_contracts_list)}")
        print(f"   Contratos de datos: {len(data_contracts_list)}")
        
        return {
            "dev_plan": plan,
            "project_id": project_id,
            "api_contracts": api_contracts_list,
            "data_contracts": data_contracts_list
        }
        
    except json.JSONDecodeError:
        print("Error: El planificador no devolvió un JSON válido.")
        return {
            "dev_plan": {"plan_type": "none"},
            "supervisor_iterations": state.get("supervisor_iterations")+1
        }

