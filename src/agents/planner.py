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
    Eres un jefe de proyecto técnico. Tu tarea es analizar la siguiente información y generar un plan de desarrollo en formato JSON.
    Además de plantear los requisitos del sistema basado en la solicitud del usuario.

    **Contexto Relevante de la Base de Conocimientos (Para guiar decisiones técnicas):**
    ---
    {retrieved_info}
    ---

    Genera un PRD, o Documento de Requisitos del Producto, que detalla las características,
    funcionalidades y objetivos de un producto para que los equipos de desarrollo y pruebas sepan qué construir.

    **Solicitud del Usuario ({context_user}):**
    ---
    **Contexto de Interfaz (Opcional) ({context_ui_ux}):**
    ---
    **Contexto Multimedia (Opcional) ({context_media}):**

    **INSTRUCCIONES:**
    1.  **Analiza** la solicitud del usuario y la base de conocimientos.
    2.  **Formula un plan** siguiendo las reglas de decisión.
    3.  **Justifica tus decisiones técnicas** incorporando citas de la "Base de Conocimientos" directamente en la descripción de la tarea. 
        La justificación puntual para la tarea y empezar con "(**Justificación:** ...)" para ser fácilmente identificable.
    4.  **Genera un único objeto JSON** con la respuesta, sin texto introductorio ni de cierre.

    **IMPORTANTE:** Tu salida debe ser un objeto JSON VÁLIDO con la siguiente estructura y NADA MÁS:
    {{
        "project_name": "(string) Nombre descriptivo del proyecto",
        "plan_type": "(string) Uno de: 'frontend-only', 'backend-only', 'database-only', 'fullstack'.",
        "frontend_task": "(string | null) Descripción clara de la tarea para el desarrollador frontend con requisitos técnicos, incluyendo justificación si aplica.",
        "frontend_tech": "(string | null) Tecnología específica para el frontend (ej. 'HTML, CSS y JavaScript').",
        "backend_task": "(string | null) Descripción clara de la tarea para el desarrollador backend con requisitos técnicos, incluyendo justificación si aplica.",
        "backend_tech": "(string | null) Tecnología específica para el backend (ej. 'Python con Flask').",
        "backend_port": "(number | null) Puerto en el que correrá el backend (ej. 5000 para Flask, 3000 para Express). Solo para backend/fullstack.",
        "db_task": "(string | null) Descripción clara de la tarea para el arquitecto de base de datos con requisitos técnicos, incluyendo justificación si aplica. (no des detalles sobre la base de datos ya hay un agente especializado en su creación)",
        "db_tech": "(string | null) Tecnología específica para base de datos (ej. 'MongoDB' o 'PostgreSQL' o 'Neo4j').",
        "api_contracts": "(array | null) Solo para fullstack: Array de contratos de API con estructura: [{{'endpoint': '/api/resource', 'method': 'GET/POST/PUT/DELETE', 'description': 'descripción', 'request_schema': {{'campo': 'tipo'}}, 'response_schema': {{'campo': 'tipo'}}, 'status_codes': [200, 400, 500]}}]",
        "data_contracts": "(array | null) Solo para fullstack/backend/database: Array de modelos de datos con estructura: [{{'model_name': 'NombreModelo', 'description': 'descripción', 'fields': {{'campo': {{'type': 'tipo', 'required': true}}}}}}]"
    }}

    **REGLA CRÍTICA:** Adhiérete ESTRICTAMENTE a las siguientes reglas de decisión:

    1.  **Regla de Simplificación (Prioridad Frontend):**
        * Si la solicitud del usuario puede resolverse completamente en el cliente (ej. landing page, interfaz web, programa basico web...)
        **y NO solicita** (guardado en servidor, autenticación, multiusuario o base de datos...):
        * Establece `plan_type` en 'frontend-only'.
        * Rellena SOLO `frontend_task` y `frontend_tech` los demas en null.

    2.  **Regla de Base de Datos Única:**
        * Si el usuario pide únicamente diseño, creación, esquema o una tarea exclusiva de base de datos:
        * Establece `plan_type` en 'database-only'.
        * Rellena únicamente `db_task` y `db_tech` los demás campos deben ser `null`.

    3.  **Regla de Backend Explícito:** 
        * Si el usuario pide explícitamente tecnologías de backend (ej. 'Python', 'Node.js', 'Java') o juego/programas sencillos.
        o la funcionalidad requiere inequívocamente un servidor (ej. iniciar sesión, guardar perfiles, compartir datos, procesamiento pesado):
        * Establece `plan_type` en 'backend-only'.
        * Rellena solo `backend_task` y `backend_tech` (y `db` si aplica).
        * **Consistencia del `plan_type`:** Debe reflejar exactamente los campos rellenados.

    4.  **Regla Fullstack:** *(Solo úsala si es estrictamente necesario el fullstack)*
        * Si la solicitud combina claramente frontend + backend, o si para cumplirla se necesitan ambos:
        * Establece `plan_type` en 'fullstack'.
        * Rellena `frontend`, `backend` y `db` según corresponda.
        * **Consistencia del `plan_type`:** Debe coincidir con los campos completados.

    4.5.  **Regla de Coordinación Fullstack (Estrategia de Contrato):** *(Solo si `plan_type` es 'fullstack')*
        * **Backend Task:** Define explícitamente los endpoints clave (Ruta, Método, Input esperado, Output esperado).
        * **Backend Port:** Especifica el puerto estándar para la tecnología (Flask: 5000, Express: 3000, Django: 8000).
        * **Frontend Task:** Indica que la interfaz debe consumir los endpoints definidos en el backend, mencionando los relevantes.
        * **Objetivo:** Garantizar que el frontend conozca exactamente lo que debe esperar del backend (endpoints y puerto) antes de iniciar la implementación.
    
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

