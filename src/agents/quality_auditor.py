import os
import json
from src.model import analytical_llm
from src.rag_retriever import retrieve_context
from src.tools.code_reader import (
    list_code_files_in_directory, 
    read_code_from_files, 
    format_code_for_prompt
)

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
    output_dir = "outputs"
    files_to_read = list_code_files_in_directory(output_dir)

    if not files_to_read:
        print("Auditor: No se encontraron archivos para auditar.")
        return {"review_feedback": "Error: No se encontró código en la carpeta de salida para auditar."}
    
    # --- 3. Leer el código usando la herramienta centralizada ---
    
    code_files_content = read_code_from_files(files_to_read)

    # --- 4. Formatear el código para el prompt del LLM (¡NUEVA LÓGICA SIMPLIFICADA!) ---
    code_to_review = format_code_for_prompt(code_files_content)
    
    if not code_to_review:
        print("Advertencia: No se encontró contenido auditable en los archivos.")
        return {"review_feedback": "Error: Los archivos encontrados estaban vacíos. Por favor, genera el código de nuevo."}
    
    # --- 5. Enriquecer con RAG ---
    task_description_for_rag = plan.get("frontend_task") or plan.get("backend_task") or plan.get("db_task") or user_input
    print(f"Buscando principios de calidad relevantes para: '{task_description_for_rag[:80]}...'")
    quality_principles = retrieve_context(task_description_for_rag)
    print("Contexto de calidad recuperado.")

    # --- 6. Construir el Prompt para el LLM ---
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