# Contenido para: src/agents/conversational_agent.py

# Usaremos un único modelo para conversar y para decidir la lógica.
from src.model import conversational_llm

def conversational_node(state: dict) -> dict:
    """
    Este agente se especializa en generar una respuesta conversacional.
    Usa un único LLM con un prompt estructurado para generar la respuesta Y
    decidir si la tarea se puede dar por finalizada o si el flujo debe continuar.
    """
    print("---AGENTE: CONVERSACIONAL (ESPECIALISTA)---")
    user_input = state["user_input"]
    chat_history = state.get("chat_history", [])
    history_str = "\n".join(chat_history[-6:])

    # Prompt estructurado que pide al LLM dos cosas: una decisión y una respuesta.
    prompt = f"""
    Eres DevTeam-Bot, un asistente de IA servicial. Tu tarea es doble:
    1.  Decidir si la conversación actual justifica continuar con un flujo de trabajo de desarrollo (CONTINUE) o si es una interacción simple que puede terminar (END).
    2.  Generar una respuesta amigable y apropiada para el usuario.

    Historial de conversación:
    <historial>
    {history_str}
    </historial>

    Petición del usuario: "{user_input}"

    **Reglas para la Decisión:**
    - `CONTINUE`: Si la petición del usuario es una tarea de desarrollo, aunque sea vaga (ej: "hazme una web"), o si estás pidiendo clarificaciones para una futura tarea.
    - `END`: Si la conversación es un saludo, una despedida, o una pregunta general que ya has respondido completamente.

    **Formato de Salida Obligatorio:**
    Debes responder ÚNICAMENTE en el siguiente formato, sin añadir ninguna otra palabra o explicación.

    [DECISION]
    CONTINUE o END
    [RESPONSE]
    Tu respuesta conversacional para el usuario aquí.

    **Ejemplos:**

    Ejemplo 1:
    Usuario: "Hola"
    Tu Salida:
    [DECISION]
    END
    [RESPONSE]
    ¡Hola! Soy DevTeam-Bot. ¿Estás listo para construir algo increíble o tienes alguna pregunta?

    Ejemplo 2:
    Usuario: "quiero un juego de ajedrez en la web"
    Tu Salida:
    [DECISION]
    CONTINUE
    [RESPONSE]
    ¡Excelente idea! Un juego de ajedrez es un proyecto fantástico. Para empezar a planificarlo, ¿tienes alguna característica específica en mente, como un modo de un jugador contra la IA o un diseño visual particular?

    **Tu Salida para la petición actual:**
    """

    # --- PASO ÚNICO: Invocar al LLM y analizar la respuesta estructurada ---
    response = conversational_llm.invoke(prompt)
    raw_output = response.content.strip()

    print(f"--- Salida bruta del LLM: {raw_output[:100]}... ---")

    # --- Lógica de parseo robusta para la salida ---
    try:
        # Por defecto, asumimos que la tarea no está completa
        is_task_complete = False
        final_bot_response = "Parece que he tenido un problema al procesar mi respuesta. ¿Podríamos intentarlo de nuevo?"

        # Dividimos la salida en las secciones [DECISION] y [RESPONSE]
        decision_part, response_part = raw_output.split("[RESPONSE]", 1)
        
        # Extraemos la decisión
        decision = decision_part.replace("[DECISION]", "").strip().upper()
        
        # Extraemos la respuesta final
        final_bot_response = response_part.strip()

        if "END" in decision:
            is_task_complete = True
        
        print(f"--- Decisión de continuación: '{decision}' -> task_complete={is_task_complete} ---")

    except ValueError:
        print("ADVERTENCIA: El LLM no devolvió el formato esperado. Asumiendo que es una respuesta final para evitar bucles.")
        is_task_complete = True
        # Usamos la salida cruda como respuesta si el parseo falla
        final_bot_response = raw_output

    # Actualizamos el historial y devolvemos el estado
    new_history = chat_history + [f"Usuario: {user_input}", f"Bot: {final_bot_response}"]
    return {
        "final_response": final_bot_response,
        "task_complete": is_task_complete,
        "chat_history": new_history,
        "supervisor_iterations": state.get("supervisor_iterations")+1
    }