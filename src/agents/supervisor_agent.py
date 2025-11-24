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


**REGLAS DE DECISIÓN CLAVE (Evaluar en este orden):**

1.  **Después de un Análisis (si `analysis_result` o `ui_ux_spec` está presente):**
    - **Revisa la `user_input` original.** Si la petición era únicamente para analizar, describir, transcribir o entender algo (ej: "¿qué dice este archivo?", "resume este documento"), la tarea está completa. **Elige `__end__`.**
    - Si la petición era para **CONSTRUIR** algo a partir del análisis (ej: "crea una web basada en esta imagen"), entonces el siguiente paso es el `planner`.

2.  **Si ya existe un `dev_plan`:**
    - **Estrategia Fullstack Secuencial:** Si `plan_type` es 'fullstack':
        - Si NO hay `backend_code` (o está vacío), el siguiente paso ES `develop_backend`. (Prioridad: Backend primero).
        - Si HAY `backend_code` pero NO hay `frontend_code`, el siguiente paso ES `develop_frontend`. (El frontend usará el contexto del backend).
        - Si HAY `backend_code` Y `frontend_code`, pero NO se ha auditado (`code_approved` no está presente o es False), el siguiente paso ES `quality_auditor`.
    - **Otros tipos de plan:** Si es 'backend-only', ve a `develop_backend`. Si es 'frontend-only', ve a `develop_frontend`. Si es 'database-only', ve a `database_architech`.

3.  **Si hay código generado (`frontend_code`, `backend_code`, o `db_schema`):**
    - Si `code_approved` es True, finaliza con `__end__`.
    - Si `code_approved` es False o no existe, y NO hay `review_feedback` reciente, el siguiente paso es `quality_auditor`.
    - Si hay `review_feedback` (código rechazado), devuelve al desarrollador correspondiente según `last_code_generated`.
        Ten en cunta que solo pasa una vez por cada agente. es un ciclo etre los desarrolladores y el quality auditor.
        (CRITICO: NO deber repetir el mismo agente dos veces seguidas.
4.  **Si el quality auditor aprobó el código:** Finaliza la tarea `__end__`.

**INSTRUCCIÓN:**
Basado en TODO el estado actual, analiza la situación y determina el siguiente paso lógico. ¿Qué agente debe actuar ahora?
"""

def supervisor_node(state: dict) -> dict:
    """
    Supervisor inteligente que utiliza un LLM para enrutar tareas basándose en el estado completo.
    """
    print("---AGENTE: SUPERVISOR INTELIGENTE---")


    # Convertir el estado a una cadena JSON para una visualización clara en el prompt.
    # Se excluyen claves que no son útiles para la decisión de enrutamiento.
    excluded_keys = {"routing_decision", "final_response"}
    state_for_prompt = {k: v for k, v in state.items() if k not in excluded_keys and v}
    state_json = json.dumps(state_for_prompt, indent=2)

    # Formatear el prompt con el estado actual.
    prompt = SUPERVISOR_PROMPT.format(state_json=state_json)
    
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

    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error al parsear la respuesta del LLM: {e}. Usando fallback.")
        # Fallback robusto: buscar el nombre del nodo en el texto si el JSON falla.
        decision = "conversational_agent"
        for node in AVAILABLE_NODES:
            if f'"{node}"' in response.content or f"'{node}'" in response.content:
                decision = node
                break

    print(f"Decisión del Supervisor: Enviar a '{decision}'")
    return {"routing_decision": decision}
