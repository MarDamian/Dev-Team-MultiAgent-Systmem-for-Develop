import os
import json
from src.model import analytical_llm
from src.rag_retriever import retrieve_context
from src.tools.code_reader import read_code_from_files 

def quality_auditor_node(state: dict) -> dict:
    """
    Nodo del grafo que audita la calidad del código generado.
    Utiliza RAG para fundamentar sus decisiones y lee el código directamente
    desde los archivos generados usando la herramienta 'code_reader'.
    """
    print("---AGENTE: AUDITOR DE CALIDAD (POTENCIADO CON RAG)---")
    
    # --- 1. Recopilar información del estado ---
    user_input = state.get("user_input", "")
    plan = state.get("dev_plan", {})
    review_count = state.get("review_count", 0)
    
    # --- 2. Determinar qué archivos auditar ---
    code_to_review = ""
    tech_to_review = ""
    files_to_read = []

    last_generated = state.get("last_code_generated")
    if last_generated == "frontend":
        print("Auditoría de código Frontend detectada.")
        files_to_read = ["outputs/index.html", "outputs/style.css", "outputs/script.js"]
        tech_to_review = plan.get("frontend_tech", "HTML, CSS, JavaScript")
    elif last_generated == "backend":
        print("Auditoría de código Backend detectada.")
        files_to_read = ["outputs/app.py"] # Asumiendo este nombre de archivo
        tech_to_review = plan.get("backend_tech", "Python")

    # --- 3. Leer el código usando la herramienta centralizada ---
    if not files_to_read:
        print("Error: El auditor fue llamado pero no se especificó qué tipo de código revisar (frontend/backend).")
        return {"review_feedback": "Error interno: No se pudo determinar qué código auditar."}
        
    code_files_content = read_code_from_files(files_to_read)
    
    # Formatear el código leído para incluirlo en el prompt
    full_code_parts = []
    for filename, content in code_files_content.items():
        if content: # Solo añadir si el archivo tiene contenido
            full_code_parts.append(f"--- CÓDIGO DEL ARCHIVO: {filename} ---\n{content}")
    code_to_review = "\n\n".join(full_code_parts)
    
    # Salvaguarda: si después de leer, no hay código, romper el bucle con un error
    if not code_to_review:
        print("Advertencia: La herramienta de lectura no encontró código en los archivos para auditar.")
        return {"review_feedback": "Error: No se encontró código en los archivos para auditar. Por favor, genera el código de nuevo."}

    # --- 4. Enriquecer con RAG ---
    task_description_for_rag = plan.get("frontend_task") or plan.get("backend_task") or user_input
    print(f"Buscando principios de calidad relevantes para: '{task_description_for_rag[:80]}...'")
    quality_principles = retrieve_context(task_description_for_rag)
    print("Contexto de calidad recuperado.")

    # --- 5. Construir el Prompt para el LLM ---
    prompt_text = f"""
    Eres un auditor de calidad de software meticuloso y experto. Tu misión es evaluar si el código generado cumple no solo con la solicitud del usuario, sino también con los principios de alta calidad definidos en nuestra base de conocimientos.

    **SOLICITUD ORIGINAL DEL USUARIO:** "{user_input}"
    
    **PLAN DE TAREA PARA EL DESARROLLADOR:**
    {plan}

    **PRINCIPIOS DE CALIDAD Y BUENAS PRÁCTICAS RELEVANTES (de nuestra base de conocimientos):**
    ---
    {quality_principles}
    ---

    **CÓDIGO GENERADO A AUDITAR (leído de los archivos):**
    {code_to_review}
    

    **Tus Criterios de Auditoría:**
    1.  **Corrección Funcional/Visual:** ¿El código parece implementar lo solicitado por el usuario y el plan?
    2.  **Adherencia a Principios:** ¿El código respeta los principios de calidad y buenas prácticas descritos arriba? (Ej: ¿Es legible, mantenible, sigue patrones de diseño recomendados?).
    3.  **Errores Obvios:** ¿Hay algún error de sintaxis evidente que impida su funcionamiento?

    **Formato de Respuesta (OBLIGATORIO):**
    Tu respuesta DEBE ser un objeto JSON con la siguiente estructura y NADA MÁS:
    - "approved": (boolean) `true` si el código pasa la auditoría, `false` si requiere cambios.
    - "feedback": (string) Si se rechaza, un feedback claro, conciso y constructivo que explique QUÉ cambiar y POR QUÉ, haciendo referencia a los principios de calidad si es necesario. Si se aprueba, un breve mensaje de confirmación (ej. "El código cumple con los estándares de calidad y la especificación.").
    """
    
    # --- 6. Invocar al LLM y Procesar la Respuesta ---
    response = analytical_llm.invoke(prompt_text)
    review_count += 1
    
    try:
        json_response = response.content.strip().replace("```json", "").replace("```", "").strip()
        audit_result = json.loads(json_response)
        feedback = audit_result.get("feedback", "No se proporcionó feedback.")
        is_approved = audit_result.get("approved", False)

        review_count += 1

        if is_approved:
            print(f"Auditoría de Calidad: APROBADO. Feedback: {feedback}")
            # --- ¡ESTE ES EL BLOQUE QUE NECESITA CORRECCIÓN! ---
            # Debemos devolver el feedback Y la bandera de aprobación para que el frontend los vea.
            return {
                "feedback": feedback,         # <-- CLAVE: Devolver el feedback de aprobación.
                "review_feedback": None,      # Limpiar el feedback de rechazo.
                "review_count": review_count,
                "code_approved": True         # Señal para que el supervisor finalice.
            }
        else:
            print(f"Auditoría de Calidad: REQUIERE CAMBIOS. Feedback: {feedback}")
            # Este bloque ya estaba bien, pero lo revisamos para consistencia.
            return {
                "feedback": feedback,         # Devolver el feedback.
                "review_feedback": feedback,  # Llenar el campo de feedback de rechazo.
                "review_count": review_count,
                "code_approved": False        # Indicar que no está aprobado.
            }

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error: El auditor no devolvió un JSON válido. Error: {e}")
        # Asegurarnos de que el feedback de error también se devuelva.
        feedback_error = "Error interno del auditor: La respuesta no fue un JSON válido. Por favor, intenta generar el código de nuevo."
        return {
            "feedback": feedback_error,
            "review_feedback": feedback_error,
            "review_count": review_count,
            "code_approved": False
        }