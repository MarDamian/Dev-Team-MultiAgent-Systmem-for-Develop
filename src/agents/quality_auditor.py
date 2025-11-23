import os
import json
from src.model import analytical_llm
from src.rag_retriever import retrieve_context
from src.tools.code_reader import (
    list_code_files_in_directory, 
    read_code_from_files, 
    format_code_for_prompt
)
from src.tools.code_validator import code_validator
from src.tools.contract_manager import get_contracts_for_prompt
from src.tools.project_manager import get_active_project_id

def quality_auditor_node(state: dict) -> dict:
    """
    Agente Auditor de Calidad que impulsa el ciclo de RAG Iterativo.

    Este nodo actúa como el "evaluador" en un bucle de mejora continua. Su función es:
    1. Leer el código generado por otro agente directamente desde los archivos.
    2. Utilizar RAG para recuperar los principios de calidad y buenas prácticas relevantes
       de una base de conocimientos.
    3. Evaluar el código en función de la solicitud original, el plan de desarrollo y
       dichos principios de calidad.
    4. Generar un "feedback" constructivo si el código no cumple los estándares.
    5. Validar cumplimiento de contratos de interfaz.

    Este feedback es la pieza clave del RAG Iterativo, ya que se utiliza para instruir
    al agente generador de código en la siguiente iteración, permitiendo refinar y
    mejorar el resultado hasta que se alcance la calidad deseada.
    """
    print("---AGENTE: AUDITOR DE CALIDAD (POTENCIADO CON RAG Y CONTRATOS)---")
    
    # --- 1. Recopilar información del estado ---
    user_input = state.get("user_input", "")
    plan = state.get("dev_plan", {})
    review_count = state.get("review_count", 0)
    
    # --- 2. Determinar qué archivos auditar (usa proyecto activo) ---
    files_to_read = list_code_files_in_directory()

    if not files_to_read:
        print("Auditor: No se encontraron archivos para auditar.")
        return {"review_feedback": "Error: No se encontró código en la carpeta de salida para auditar."}
    
    # --- 3. Leer el código usando la herramienta centralizada ---
    code_files_content = read_code_from_files(files_to_read)

    # --- 4. Formatear el código para el prompt del LLM ---
    code_to_review = format_code_for_prompt(code_files_content)
    
    if not code_to_review:
        print("Advertencia: No se encontró contenido auditable en los archivos.")
        return {"review_feedback": "Error: Los archivos encontrados estaban vacíos. Por favor, genera el código de nuevo."}
    
    # --- 5. Enriquecer con RAG y CONTRATOS ---
    task_description_for_rag = plan.get("frontend_task") or plan.get("backend_task") or plan.get("db_task") or user_input
    print(f"Buscando principios de calidad relevantes para: '{task_description_for_rag[:80]}...'")
    
    # Invocación al sistema de recuperación para obtener principios de calidad
    quality_principles = retrieve_context(task_description_for_rag)
    print("Contexto de calidad recuperado.")
    
    # Obtener contratos del proyecto activo
    project_id = get_active_project_id()
    contracts_text = ""
    syntax_report = ""
    
    if project_id:
        contracts_text = get_contracts_for_prompt(project_id, "all")
        if contracts_text:
            print(f"✅ Contratos de interfaz cargados para validación.")
        
        # Validación de sintaxis
        print("Ejecutando validación de sintaxis...")
        syntax_validation = code_validator.validate_project_code(project_id)
        syntax_report = code_validator.format_validation_report(syntax_validation)
        print(syntax_report)

    # --- 6. Construir el Prompt para el LLM ---
    prompt_text = f"""
    Eres un auditor de calidad de software meticuloso y experto. Tu misión es evaluar si el código generado cumple no solo con la solicitud del usuario, sino también con los principios de alta calidad definidos en nuestra base de conocimientos Y los contratos de interfaz definidos.

    **SOLICITUD ORIGINAL DEL USUARIO:** "{user_input}"
    
    **PLAN DE TAREA PARA EL DESARROLLADOR:**
    {plan}

    **PRINCIPIOS DE CALIDAD Y BUENAS PRÁCTICAS RELEVANTES (de nuestra base de conocimientos):**
    ---
    {quality_principles}
    ---
    
    **CONTRATOS DE INTERFAZ DEFINIDOS:**
    ---
    {contracts_text if contracts_text else "No hay contratos definidos para este proyecto."}
    ---
    
    **REPORTE DE VALIDACIÓN DE SINTAXIS:**
    ---
    {syntax_report if syntax_report else "No se ejecutó validación de sintaxis."}
    ---

    **CÓDIGO GENERADO A AUDITAR (leído de los archivos):**
    {code_to_review}
    

    **Tus Criterios de Auditoría:**
    1.  **Corrección Funcional/Visual:** ¿El código parece implementar lo solicitado por el usuario y el plan?
    2.  **Adherencia a Principios:** ¿El código respeta los principios de calidad y buenas prácticas descritos arriba? (Ej: ¿Es legible, mantenible, sigue patrones de diseño recomendados?).
    3.  **Errores de Sintaxis:** ¿Hay errores de sintaxis según el reporte de validación?
    4.  **Cumplimiento de Contratos:** ¿El código cumple con los contratos de interfaz definidos? (Endpoints correctos, schemas de datos coincidentes, etc.)
    5.  **Coherencia de Integración e Infraestructura:** ¿Existe sincronización entre cliente y servidor?(Verificar: coincidencia exacta de endpoints, manejo dinámico de puertos/URLs base y correspondencia en los tipos de datos enviados/recibidos).

    **Formato de Respuesta (OBLIGATORIO):**
    Tu respuesta DEBE ser un objeto JSON con la siguiente estructura y NADA MÁS:
    - "approved": (boolean) `true` si el código pasa la auditoría, `false` si requiere cambios.
    - "feedback": (string) Si se rechaza, un feedback claro, conciso y constructivo que explique QUÉ cambiar y POR QUÉ, haciendo referencia a los principios de calidad y contratos si es necesario. Si se aprueba, un breve mensaje de confirmación (ej. "El código cumple con los estándares de calidad, contratos y la especificación.").
    """
    
    # --- 7. Invocar al LLM y Procesar la Respuesta ---
    response = analytical_llm.invoke(prompt_text)
    review_count += 1 # Incrementa el contador de revisiones (útil para limitar iteraciones)
    print("Archivos auditados: ", files_to_read)
    
    try:
        json_response = response.content.strip().replace("```json", "").replace("```", "").strip()
        audit_result = json.loads(json_response)
        feedback = audit_result.get("feedback", "No se proporcionó feedback.")
        is_approved = audit_result.get("approved", False)

        if is_approved:
            print(f"Auditoría de Calidad: APROBADO. Feedback: {feedback}")
            # Debemos devolver el feedback Y la bandera de aprobación para que el frontend los vea.
            return {
                "feedback": feedback,         # Devolver el feedback de aprobación.
                "review_feedback": None,      # Limpiar el feedback de rechazo.
                "review_count": review_count,
                "code_approved": True         # Señal para que el supervisor finalice.
            }
        else:
            print(f"Auditoría de Calidad: REQUIERE CAMBIOS. Feedback: {feedback}")
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
            "code_approved": False,
            "supervisor_iterations": state.get("supervisor_iterations")+1
        }