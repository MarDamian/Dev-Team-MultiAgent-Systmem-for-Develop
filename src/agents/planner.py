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
Ademas de plantear los requisitos del sistema basado en la solicitud del usuario.

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
2.  **Formula un plan** para los desarrolladores frontend, backend y/o de base de datos.
3.  **Justifica tus decisiones técnicas** incorporando citas de la "Base de Conocimientos" directamente en la descripción de la tarea. La justificación debe ser breve y empezar con "(Justificación: ...)" para ser fácilmente identificable.
4.  **Genera un único objeto JSON** con la respuesta, sin texto introductorio ni de cierre.

**Ejemplo de justificación en una tarea:** "Crear los endpoints API para la gestión de usuarios. (Justificación: La base de conocimientos indica que 'la autenticación debe manejarse en el backend')."

**IMPORTANTE:** Tu salida debe ser un objeto JSON VÁLIDO con la siguiente estructura y NADA MÁS:
{{
    "plan_type": "(string) Uno de: 'frontend-only', 'backend-only', 'database-only', 'fullstack'.",
    "frontend_task": "(string | null) Descripción clara de la tarea para el desarrollador frontend, incluyendo justificación si aplica.",
    "frontend_tech": "(string | null) Tecnología específica para el frontend (ej. 'HTML, CSS y JavaScript').",
    "backend_task": "(string | null) Descripción clara de la tarea para el desarrollador backend, incluyendo justificación si aplica.",
    "backend_tech": "(string | null) Tecnología específica para el backend (ej. 'Python con Flask').",
    "db_task": "(string | null) Descripción clara de la tarea para el arquitecto de base de datos, incluyendo justificación si aplica. (no des detalles sobre la base de datos ya hay un agente especializado en su creacion)",
    "db_tech": "(string | null) Tecnología específica para de base de datos (ej. 'MongoDB' o 'PostgreSQL' o 'Neo4j')."
}}

**REGLA CRÍTICA:** Adhiérete ESTRICTAMENTE a las siguientes reglas de decisión para determinar qué tareas incluir:

1.  **Regla de Simplificación (Prioridad Frontend):**
    * Si la solicitud del usuario describe una funcionalidad que puede resolverse **completamente en el cliente** (ej. manipulación de imágenes en el navegador, conversores de unidades, cálculos simples, generación y *descarga local* de archivos , implementar una interfaz) Y **no solicita explícitamente** guardado en servidor, autenticación, funcionalidad multiusuario o una base de datos:
    * **DEBES** optar por una solución `frontend-only`.
    * Establece `plan_type` en 'frontend-only'.
    * Rellena **únicamente** `frontend_task` y `frontend_tech`.
    * Todos los demás campos (`backend_task`, `backend_tech`, `db_task`, `db_tech`) **deben ser `null`**.
    * *(Ejemplo: La solicitud del "creador de stickers" que pide "guardar como archivo PNG" debe interpretarse como una descarga local, por lo tanto, es 'frontend-only').*

2.  **Regla de Base de Datos Única:**
    * Si el usuario pide **únicamente** un diseño, esquema o tarea de base de datos:
    * Establece `plan_type` en 'database-only'.
    * Rellena **únicamente** `db_task` y `db_tech`.
    * Todos los demás campos deben ser `null`.

3.  **Regla Fullstack o Backend Explícito:**
    * Si el usuario pide explícitamente tecnologías de backend (ej. 'Python', 'Node.js', 'Java') O si la funcionalidad **requiere inequívocamente un servidor** (ej. "iniciar sesión de usuario", "guardar perfiles", "compartir datos entre usuarios", "procesamiento pesado"):
    * Establece `plan_type` en 'fullstack' (o 'backend-only' si aplica).
    * Rellena todos los campos (`frontend`, `backend`, `db`) que sean necesarios para cumplir con la solicitud.

4.  **Consistencia del `plan_type`:** El valor de `plan_type` siempre debe reflejar con precisión qué campos de tareas (frontend, backend, db) se han rellenado.
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

