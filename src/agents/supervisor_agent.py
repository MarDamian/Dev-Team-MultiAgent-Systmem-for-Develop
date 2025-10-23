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
- `ui_ux_designer`: Analiza bocetos o imágenes de diseño para crear especificaciones de UI/UX. **Úsalo si la entrada es visual y el objetivo es crear una interfaz.**
- `multimodal_analyzer`: Extrae información de archivos (PDF, TXT, etc.). Úsalo si el usuario pide analizar, resumir o entender un documento.
- `conversational_agent`: Responde a preguntas generales, saludos o si la petición del usuario no está clara. Úsalo como último recurso.
- `__end__`: Finaliza la tarea. Úsalo solo cuando el objetivo final se haya cumplido satisfactoriamente.

**ESTADO ACTUAL DE LA TAREA (CONTEXTO):**
{state_json}

**INSTRUCCIÓN:**
Basado en TODO el estado actual, analiza la situación y determina el siguiente paso lógico. ¿Qué agente debe actuar ahora?
"""

def supervisor_node(state: dict) -> dict:
    """
    Supervisor inteligente que utiliza un LLM para enrutar tareas basándose en el estado completo.
    """
    print("---AGENTE: SUPERVISOR INTELIGENTE---")

    # --- LÓGICA DE FINALIZACIÓN PRIORITARIA ---
    # Si un agente especialista ha marcado la tarea como completa, forzamos el fin del flujo.
    if state.get("task_complete"):
        print("Decisión del Supervisor: Tarea marcada como completa. Finalizando.")
        return {"routing_decision": "__end__"}

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
