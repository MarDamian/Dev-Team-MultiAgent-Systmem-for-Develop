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
    last_code_generated = state.get("last_code_generated", "")
    
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
    contract_report = ""
    
    if project_id:
        contracts_text = get_contracts_for_prompt(project_id, "all")
        if contracts_text:
            print(f"✅ Contratos de interfaz cargados para validación.")
        

    # --- 6. Construir el Prompt para el LLM ---
    prompt_text = f"""
Eres un auditor de calidad de software de élite con 15+ años de experiencia en revisión de código,
arquitectura de software y aseguramiento de calidad. 

**TU MISIÓN:**
Evaluar el código generado con criterio profesional y determinar si cumple con los estándares
de calidad, funcionalidad y contratos de interfaz definidos.

CONTEXTO DE LA SOLICITUD ORIGINAL

**SOLICITUD DEL USUARIO:** 
"{user_input}"

**PLAN DE DESARROLLO ASIGNADO:(Si crees que puede ser mejorado, propónlo)**
{plan}

PRINCIPIOS DE CALIDAD Y BUENAS PRÁCTICAS (BASE DE CONOCIMIENTOS)

{quality_principles}

CONTRATOS DE INTERFAZ DEFINIDOS

{contracts_text}

REPORTES DE VALIDACIÓN TÉCNICA

**Validación de Sintaxis:**
{syntax_report}

**Validación de Contratos:**
{contract_report}

CÓDIGO A AUDITAR

{code_to_review}

CODIGO GENERADO ANTERIORMENTE SOlO APLICA FEEDBACK A ESTE CODIGO

{last_code_generated}

CRITERIOS DE AUDITORÍA (EVALUAR TODOS)


**1. CORRECCIÓN FUNCIONAL (CRÍTICO):**
   □ ¿El código implementa TODAS las funcionalidades solicitadas?
   □ ¿La lógica de negocio es correcta y completa?
   □ ¿Los casos de uso están cubiertos?
   □ ¿No hay funcionalidad faltante o incompleta?

**2. CUMPLIMIENTO DE CONTRATOS (FLEXIBLE):**
   □ ¿Todos los endpoints definidos están implementados?
   □ ¿Los métodos HTTP son correctos (GET, POST, PUT, DELETE)?
   □ ¿Los códigos de estado son los especificados?
   □ ¿Los modelos de datos tienen todos los campos requeridos?
   □ ¿Los tipos de datos son consistentes?

**3. INTEGRACIÓN CLIENTE-SERVIDOR (FULLSTACK):**
   □ ¿El frontend usa el puerto correcto del backend y viceversa?
   □ ¿La BASE_URL está configurada correctamente?
   □ ¿Los endpoints del frontend coinciden EXACTAMENTE con los del backend?
   □ ¿Los payloads enviados coinciden con los esperados?
   □ ¿Los responses del backend son parseados correctamente en el frontend?

**4. MANEJO DE ERRORES:**
   □ ¿Hay try-catch en operaciones que pueden fallar?
   □ ¿Los mensajes de error son descriptivos pero no técnicos?
   □ ¿Se validan inputs antes de procesarlos?

**5. CALIDAD DEL CÓDIGO:**
   □ ¿El código es legible y bien estructurado?
   □ ¿Los nombres son descriptivos?
   □ ¿Hay separación de responsabilidades?
   □ ¿Se evita duplicación (DRY)?
   □ ¿Hay comentarios donde es necesario?

**6. BASE DE DATOS:**
   □ ¿Las conexiones se manejan correctamente?
   □ ¿Las queries son eficientes?
   □ ¿Hay manejo de transacciones donde es necesario?
   □ ¿Se cierran las conexiones apropiadamente?
   □ ¿El esquema es consistente con los modelos?

**7. FRONTEND (SI APLICA):**
   □ ¿HTML es semántico y accesible?
   □ ¿CSS es responsive (móvil, tablet, desktop)?
   □ ¿Hay feedback visual en todas las acciones?
   □ ¿Los formularios se validan antes de enviar?
   □ ¿Hay estados de loading/error/success?

**8. DEPENDENCIAS Y CONFIGURACIÓN:**
   □ ¿Están todas las dependencias necesarias?
   □ ¿Las versiones son compatibles?
   □ ¿Hay archivo de configuración (.env.example)?
   □ ¿Las dependencias son las mínimas necesarias?

FORMATO DE RESPUESTA (ESTRICTAMENTE OBLIGATORIO)

Debes responder ÚNICAMENTE con un objeto JSON con esta estructura exacta:

{{
  "approved": true o false,
  "feedback": "Tu mensaje aquí"
}}

**SI APRUEBAS (approved: true):**
- Feedback debe ser un mensaje breve y profesional confirmando la calidad
- Ejemplo: "El código cumple con todos los estándares de calidad, y contratos definidos. Está listo para producción.(solo es un ejemplo)"

**SI RECHAZAS (approved: false):**
- Feedback debe ser ESPECÍFICO, CONSTRUCTIVO y ACCIONABLE
- Estructura tu feedback así:

  "PROBLEMAS ENCONTRADOS:

  1. [Categoría]
     - Problema: [Descripción específica del problema]
     - Ubicación: [Archivo y línea/función si es posible]
     - Solución: [Qué hacer exactamente para corregirlo]
     - Por qué: [Referencia a principios de calidad o riesgos]

  2. [Siguiente problema...]

  CORRECCIONES REQUERIDAS:
  - [Lista de acciones específicas que el desarrollador debe tomar]"

**REGLAS CRÍTICAS:**
- ❌ NO apruebes código que no cumple los contratos
- ❌ NO apruebes código con funcionalidad faltante
- ❌ NO seas excesivamente estricto 
- ✅ Sé sugerente y constructivo
- ✅ Sé objetivo y basado en hechos
- ✅ Prioriza problemas críticos sobre estéticos
- ✅ Da feedback que el desarrollador pueda actuar inmediatamente

PROCESO DE EVALUACIÓN

**Recuerda:** Tu rol es asegurar que SOLO una version inicial y completa de código llegue al usuario final.
   El objetivo es mejora continua, no perfección imposible(Da recomendaciones al usuario).


**AHORA EVALÚA EL CÓDIGO Y GENERA TU RESPUESTA JSON.**
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
            last_generated = state.get("last_code_generated")
            approval_flags = {}
            
            if last_generated == "backend":
                approval_flags["backend_approved"] = True
                print("✅ Backend aprobado")
            elif last_generated == "frontend":
                approval_flags["frontend_approved"] = True
                print("✅ Frontend aprobado")
            elif last_generated == "database":
                approval_flags["database_approved"] = True
                print("✅ Database aprobado")
            
            return {
                "feedback": feedback,         # Devolver el feedback de aprobación.
                "review_feedback": None,      # Limpiar el feedback de rechazo.
                "review_count": review_count,
                **approval_flags,
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
            "supervisor_iterations": state.get("supervisor_iterations", 0) + 1
        }