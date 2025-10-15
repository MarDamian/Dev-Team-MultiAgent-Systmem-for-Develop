import json
from src.model import analytical_llm
from src.rag_retriever import retrieve_context

def planner_node(state: dict) -> dict:
    print("---AGENTE: PLANIFICADOR DE PROYECTO---")


    context_ui_ux = state.get("ui_ux_spec")
    context_user = state.get("user_input")
    context_media= state.get("analysis_result")

    # --- Recuperación de Contexto con RAG ---
 
    retrieved_info = retrieve_context(context_user)

    prompt = f"""
        Eres un jefe de proyecto técnico. Tu tarea es analizar la siguiente información y generar un plan de desarrollo en formato JSON.

        **Contexto Relevante de la Base de Conocimientos (Para guiar decisiones técnicas):**
        ---
        {retrieved_info}
        ---

        **Solicitud del Usuario ({context_user}):**
        ---
        **Contexto de Interfaz(Opcional) ({context_ui_ux}):**
        ---
        **Contexto Multimedia (Opcional) ( {context_media}):**

        
        **INSTRUCCIONES:**
        1.  **Analiza** la solicitud del usuario y la base de conocimientos.
        2.  **Formula un plan** para los desarrolladores frontend y/o backend.
        3.  **Justifica tus decisiones técnicas** incorporando citas de la "Base de Conocimientos" directamente en la descripción de la tarea. La justificación debe ser breve y empezar con "(Justificación: ...)" para ser fácilmente identificable.
        4.  **Genera un único objeto JSON** con la respuesta, sin texto introductorio ni de cierre.

        **Ejemplo de justificación en una tarea:** "Crear los endpoints API para la gestión de usuarios. (Justificación: La base de conocimientos indica que 'la autenticación debe manejarse en el backend')."

        **IMPORTANTE:** Tu salida debe ser un objeto JSON VÁLIDO con la siguiente estructura y NADA MÁS:
        {{
            "plan_type": "frontend", "backend","database".
            "frontend_task": "(string | null) Descripción clara de la tarea para el desarrollador frontend, incluyendo justificación si aplica.",
            "frontend_tech": "(string | null) Tecnología específica para el frontend (ej. 'HTML, CSS y JavaScript').",
            "backend_task": "(string | null) Descripción clara de la tarea para el desarrollador backend, incluyendo justificación si aplica.",
            "backend_tech": "(string | null) Tecnología específica para el backend (ej. 'Python con Flask').",
            "db_task:"(string | null) Descripción clara de la tarea para el arquitecto de base de datos, 
                incluyendo justificación si aplica.(no des detalles  sobre la base de datos ya hay un agente especializado en su creacion)",
            "db_tech": "(string | null) Tecnología específica para de base de datos (ej. 'MongoDB' o 'PostgreSQL' o 'Neo4j').",
        }}

        **REGLA CRÍTICA:** Adhiérete ESTRICTAMENTE a las tecnologías solicitadas en la petición del usuario. 
        Si el usuario pide "HTML, CSS y JS" o una implementacion de interfaz a partir de un muckup o video:
            Los campos `frontend_task`, `frontend_tech` unicamente no añadas otros campos  
        Si el usuario te pide unicamente bases de datos,
            entonces solo ocupas `db_task` y `db_tech`.

        No sugieras frameworks, librerías o herramientas de construcción a menos que se pidan explícitamente.  
    """
    
    response = analytical_llm.invoke(prompt)
    
    try:
        json_response = response.content.strip().replace("```json", "").replace("```", "").strip()
        plan = json.loads(json_response)
        print(f"Plan de desarrollo generado: {plan}")
        return {"dev_plan": plan}
    except json.JSONDecodeError:
        print("Error: El planificador no devolvió un JSON válido.")
        return {
            "dev_plan": {"plan_type": "none"},
            "supervisor_iterations": state.get("supervisor_iterations")+1
            }

