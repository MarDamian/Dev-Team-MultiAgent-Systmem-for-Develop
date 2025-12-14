from src.model import analytical_llm
from langchain_core.messages import HumanMessage
import json

# Lista de nodos disponibles para el enrutamiento.
AVAILABLE_NODES = [
    "planner",
    "database_architech",
    "develop_backend",
    "develop_frontend",
    "quality_auditor",
    "ui_ux_designer",
    "multimodal_analyzer",
    "conversational_agent",
    "__end__"
]



# El nuevo prompt inteligente que centraliza toda la lógica de enrutamiento.
SUPERVISOR_PROMPT = """
Eres el supervisor experto de un equipo de agentes de IA para el desarrollo de software.
Tu única función es analizar el estado completo de una tarea y decidir cuál es el siguiente agente que debe actuar.
Responde ÚNICAMENTE con el nombre de uno de los nodos disponibles en formato JSON. Ejemplo: {{"destination": "planner"}}

**AGENTES DISPONIBLES (NODOS Y SU FUNCIÓN):**

- `planner`: Descompone requisitos complejos en un plan de desarrollo paso a paso. **Es el punto de partida ideal para cualquier nueva solicitud de desarrollo.**
- `database_architech`: Diseña y genera esquemas de bases de datos (código SQL) a partir de un plan.
- `develop_backend`: Escribe el código del lado del servidor (APIs, lógica de negocio) a partir de un plan.
- `develop_frontend`: Escribe el código del lado del cliente (HTML, CSS, JS) a partir de un plan o diseño.
- `quality_auditor`: Revisa el código generado para corregir errores, aplicar feedback o verificar que cumple los requisitos. **Debe actuar siempre después de que se genere código o si hay feedback pendiente.**
- `ui_ux_designer`: Analiza bocetos o imágenes de diseño para crear especificaciones de UI/UX. **Úsalo si la entrada es visual y el objetivo es crear unicamene una interfaz, lanfing page, diseño web.etc**
- `multimodal_analyzer`: Extrae información de archivos (PDF, TXT, png,etc .). Úsalo si el usuario pide analizar, resumir o entender un documento imagen audio etc.
- `conversational_agent`: Responde a preguntas generales, saludos o si la petición del usuario no está clara. Úsalo como último recurso.
- `__end__`: Finaliza la tarea. Úsalo solo cuando el objetivo final se haya cumplido satisfactoriamente.

**ESTADO ACTUAL DE LA TAREA (CONTEXTO):**
{state_json}

**HISTORIAL DE AGENTES VISITADOS:**
{nodes_visited}

**REGLAS DE DECISIÓN CLAVE (Evaluar en este orden):**

**REGLA CRÍTICA DE NO REPETICIÓN:**
- **NUNCA** repitas el mismo agente dos veces seguidas. Revisa `nodes_visited` para ver el último agente ejecutado.
- Si el último nodo visitado fue un desarrollador (develop_backend, develop_frontend, database_architech), el siguiente DEBE ser `quality_auditor` (a menos que el código ya esté aprobado).
- Si el último nodo visitado fue `quality_auditor` y hay `review_feedback`, el siguiente DEBE ser el desarrollador correspondiente según `last_code_generated`.

1.  **Después de un Análisis (si `analysis_result` o `ui_ux_spec` está presente):**
    - **Revisa la `user_input` original.** Si la petición era únicamente para analizar, describir, transcribir o entender algo (ej: "¿qué dice este archivo?", "resume este documento"), la tarea está completa. **Elige `__end__`.**
    - Si la petición era para **CONSTRUIR** algo a partir del análisis (ej: "crea una web basada en esta imagen"), entonces el siguiente paso es el `planner`.

2.  **Si ya existe un `dev_plan`:**
    - **Estrategia Fullstack Secuencial:** Si `plan_type` es 'fullstack':
        - Si NO hay `backend_code` (o está vacío), el siguiente paso ES `develop_backend`. (Prioridad: Backend primero).
        - Si HAY `backend_code` pero NO hay `frontend_code`, el siguiente paso ES `develop_frontend`. (El frontend usará el contexto del backend).
        - Si HAY `backend_code` Y `frontend_code`, pero NO se ha auditado (`code_approved` no está presente o es False), el siguiente paso ES `quality_auditor`.
    - **Otros tipos de plan:** Si es 'backend-only', ve a `develop_backend`. Si es 'frontend-only', ve a `develop_frontend`. Si es 'database-only', ve a `database_architech`.

3.  **CICLO DE REVISIÓN DE CÓDIGO (Crítico - Sigue este flujo exactamente):**
    - **Si hay código generado (`frontend_code`, `backend_code`, o `db_schema`):**
        a) **Código Aprobado:** Si `code_approved` es True, finaliza con `__end__`.
        
        b) **Código Generado, Sin Revisar:** Si `code_approved` es False o no existe, Y NO hay `review_feedback`:
           - Verifica `nodes_visited`: Si el último nodo NO fue `quality_auditor`, el siguiente paso es `quality_auditor`.
           - Si el último nodo fue `quality_auditor`, hay un error de estado. Usa `conversational_agent` como fallback.
        
        c) **Código Rechazado (Hay review_feedback):** 
           - Identifica el desarrollador correcto según `last_code_generated`:
             * Si `last_code_generated` es "backend" → `develop_backend`
             * Si `last_code_generated` es "frontend" → `develop_frontend`
             * Si `last_code_generated` es "database" → `database_architech`
           - **IMPORTANTE:** Verifica `nodes_visited`. Si el último nodo ya fue el desarrollador correspondiente, NO lo repitas. En su lugar, ve a `quality_auditor`.
        d) Después de que el desarrollador corrija el código, el siguiente paso SIEMPRE es `quality_auditor` para re-revisar.
                Solo haz un maximo de 3 iteraciones por cada desarrollador y quality auditor. 
                **CONTADORES DE ITERACIÓN:**
                - Backend: {backend_iterations}/2
                - Frontend: {frontend_iterations}/2
                - Database: {database_iterations}/2
                **BANDERAS DE APROBACIÓN:**
                - backend_approved: {backend_approved}
                - frontend_approved: {frontend_approved}
                - database_approved: {database_approved}
                Si algún componente alcanzó 2 iteraciones sin aprobarse, considera finalizar o avanzar.
Si un componente está aprobado (bandera = True), no lo revises de nuevo.

4.  **Si el quality auditor aprobó el código de todos los desarrolladores (`code_approved` es True):** Finaliza la tarea con `__end__`.

**INSTRUCCIÓN:**
Basado en TODO el estado actual y el historial de nodos visitados, analiza la situación y determina el siguiente paso lógico. 
**RECUERDA:** NO repitas el mismo agente dos veces seguidas. El ciclo debe ser: Desarrollador → Quality Auditor → (si hay feedback) → Desarrollador → Quality Auditor → ... hasta aprobación.
¿Qué agente debe actuar ahora?
"""

def supervisor_node(state: dict) -> dict:
    """
    Supervisor inteligente que utiliza un LLM para enrutar tareas basándose en el estado completo.
    """
    print("---AGENTE: SUPERVISOR INTELIGENTE---")

    # --- SAFETY CHECK: Prevenir bucles infinitos ---
    supervisor_iterations = state.get("supervisor_iterations", 0)
    MAX_ITERATIONS = 20  # Límite de seguridad
    
    if supervisor_iterations >= MAX_ITERATIONS:
        print(f"⚠️ ADVERTENCIA: Se alcanzó el límite de {MAX_ITERATIONS} iteraciones del supervisor.")
        print("Finalizando la tarea para prevenir bucle infinito.")
        return {
            "routing_decision": "__end__",
            "final_response": "Lo siento, he detectado un problema en el flujo de trabajo. Por favor, intenta reformular tu solicitud o contacta al administrador.",
            "task_complete": True
        }

    backend_iterations = state.get("backend_iterations", 0)
    frontend_iterations = state.get("frontend_iterations", 0)
    database_iterations = state.get("database_iterations", 0)
    # Obtener y formatear el historial de nodos visitados
    nodes_visited = state.get("nodes_visited", [])
    nodes_visited_str = " → ".join(nodes_visited) if nodes_visited else "Ninguno (inicio de la tarea)"
    last_node = nodes_visited[-1] if nodes_visited else None
    
    print(f"Nodos Visitados: {nodes_visited_str}")
    if last_node:
        print(f"Último Nodo Ejecutado: {last_node}")

    # Convertir el estado a una cadena JSON para una visualización clara en el prompt.
    # Se excluyen claves que no son útiles para la decisión de enrutamiento.
    excluded_keys = {"routing_decision", "final_response", "nodes_visited"}
    state_for_prompt = {k: v for k, v in state.items() if k not in excluded_keys and v}
    state_json = json.dumps(state_for_prompt, indent=2)

    # Formatear el prompt con el estado actual y el historial de nodos.
    prompt = SUPERVISOR_PROMPT.format(
        state_json=state_json,
        nodes_visited=nodes_visited_str,
        backend_iterations=backend_iterations,
        frontend_iterations=frontend_iterations,
        database_iterations=database_iterations,
        backend_approved=state.get("backend_approved", False),
        frontend_approved=state.get("frontend_approved", False),
        database_approved=state.get("database_approved", False),
    )
    
    # Invocar al LLM para que tome la decisión.
    message = HumanMessage(content=prompt)
    response = analytical_llm.invoke([message])
    
    try:
        # Parsear la respuesta JSON del LLM.
        response_data = json.loads(response.content)
        decision = response_data.get("destination", "conversational_agent")
        print(f"Respuesta del LLM para enrutamiento: '{response.content}'")

        # Validar que la decisión sea un nodo válido.
        if decision not in AVAILABLE_NODES:
            print(f"ADVERTENCIA: Decisión inválida ('{decision}'). Forzando a 'conversational_agent'.")
            decision = "conversational_agent"
        
        # VALIDACIÓN CRÍTICA: Prevenir repetición del mismo agente
        if last_node and decision == last_node and decision not in ["__end__", "conversational_agent"]:
            print(f"⚠️ ADVERTENCIA: El supervisor intentó repetir el agente '{decision}'. Aplicando lógica de corrección...")
            
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error al parsear la respuesta del LLM: {e}. Usando fallback.")
        # Fallback robusto: buscar el nombre del nodo en el texto si el JSON falla.
        decision = "conversational_agent"
        for node in AVAILABLE_NODES:
            if f'"{node}"' in response.content or f"'{node}'" in response.content:
                decision = node
                break
    
    # Actualizar el historial de nodos visitados (solo si no es __end__)
    updated_nodes_visited = nodes_visited.copy()
    if decision != "__end__":
        updated_nodes_visited.append(decision)
    
    print(f"Decisión Final del Supervisor: '{decision}'")
    print(f"Historial Actualizado: {' → '.join(updated_nodes_visited)}")
    
    return {
        "routing_decision": decision,
        "nodes_visited": updated_nodes_visited,
        "supervisor_iterations": supervisor_iterations + 1
    }

