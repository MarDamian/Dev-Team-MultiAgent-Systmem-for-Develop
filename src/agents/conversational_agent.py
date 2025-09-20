# Contenido para: src/agents/conversational_agent.py

from src.model import creative_llm # Usamos el LLM creativo para un chat más natural

def conversational_node(state: dict) -> dict:
    """
    Este agente se especializa en generar una respuesta conversacional.
    Se activa cuando el supervisor determina que la intención del usuario es 'CHAT' o 'CLARIFY'.
    """
    print("---AGENTE: CONVERSACIONAL (ESPECIALISTA)---")
    user_input = state["user_input"]
    chat_history = state.get("chat_history", [])
    history_str = "\n".join(chat_history[-6:]) # Usamos un historial un poco más largo para el contexto

    prompt = f"""
    Eres DevTeam-Bot, un asistente de IA amigable y servicial. Tu propósito es conversar con el usuario, entender sus necesidades y, si es necesario, pedirle más detalles.

    Aquí está el historial reciente de la conversación:
    <historial>
    {history_str}
    </historial>

    La última entrada del usuario es: "{user_input}"

    Genera una respuesta natural, amigable y útil.
    - Si te saludan, saluda de vuelta.
    - Si te preguntan qué puedes hacer, explica brevemente tus capacidades (analizar imágenes/audio, escribir código, etc.).
    - Si la petición del supervisor fue para clarificar, haz una pregunta relevante para obtener más detalles.
    """

    response = creative_llm.invoke(prompt)
    final_bot_response = response.content.strip()

    print(f"--- SALIDA DEL AGENTE CONVERSACIONAL: {final_bot_response[:80]}... ---")

    # La salida de este agente es la respuesta final para el usuario.
    # También actualizamos el historial y marcamos la tarea como completa.
    new_history = chat_history + [f"Usuario: {user_input}", f"Bot: {final_bot_response}"]
    return {
        "final_response": final_bot_response,
        "task_complete": True,
        "chat_history": new_history
    }
