# Contenido para: src/agents/code_revisor.py

from src.model import analytical_llm

def review_code_node(state: dict) -> dict:
    """
    Nodo del grafo que revisa el código generado.
    Este revisor ha sido "relajado" para enfocarse en la apariencia visual y no en la funcionalidad profunda.
    """
    print("---AGENTE: REVISOR DE CÓDIGO (MODO RELAJADO)---")
    
    # La "pregunta" o solicitud original del usuario se encuentra en 'user_input'.
    # El error KeyError ocurría porque 'question' no existe en el estado.
    question = state.get("user_input", "")
    plan = state.get("dev_plan", {})
    review_count = state.get("review_count", 0)
    
    # Determinar qué código y tecnología revisar
    code_to_review = ""
    tech_to_review = ""
    frontend_code = state.get("frontend_code")
    backend_code = state.get("backend_code")

    if isinstance(frontend_code, dict):
        # Nuevo formato: combinar todos los bloques de código en uno solo para la revisión
        full_code = []
        for lang, code in frontend_code.items():
            full_code.append(f"--- {lang.upper()} ---\n{code}")
        code_to_review = "\n\n".join(full_code)
        tech_to_review = plan.get("frontend_tech", "desconocida")
    elif backend_code:
        code_to_review = backend_code
        tech_to_review = plan.get("backend_tech", "desconocida")
    else:
        print("Advertencia: El revisor fue llamado pero no hay código para revisar.")
        return {"review_feedback": None}

    print(f"Revisando código de {tech_to_review}...")

    # --- EL PROMPT CLAVE Y CORREGIDO ---
    prompt_text = f"""
    Eres un revisor de código con un único y claro objetivo: evaluar si el código generado CUMPLE VISUALMENTE con la solicitud del usuario.

    SOLICITUD DEL USUARIO: "{question}"
    
    CÓDIGO GENERADO A REVISAR:
    ```{tech_to_review.split()}
    {code_to_review}
    ```
    
    Tus reglas de revisión son simples:
    1.  **APROBAR** si el código parece que generará una interfaz o una funcionalidad que coincide con lo que el usuario pidió. No tiene que ser perfecto ni funcionalmente completo. La funcionalidad simulada o con placeholders es aceptable.
    2.  **RECHAZAR** solo si el código tiene un error de sintaxis OBVIO que impedirá que se ejecute, o si visualmente es MUY DIFERENTE a lo que se pidió.

    IGNORA por completo los siguientes aspectos, a menos que la solicitud los pida explícitamente:
    - Funcionalidad real o de backend (ej. si un botón realmente funciona).
    - Buenas prácticas de código menores (estilo, PEP 8).
    - Atributos de accesibilidad o seguridad complejos.

    Tu respuesta DEBE ser una de dos opciones:
    1.  Si el código es aceptable bajo estas reglas relajadas, responde ÚNICAMENTE con la palabra `approve`.
    2.  Si el código tiene un error de sintaxis obvio o es visualmente incorrecto, proporciona un feedback muy corto y directo para arreglar ESE problema específico.
    """
    
    response = analytical_llm.invoke(prompt_text)
    feedback = response.content.strip()

    review_count += 1

    state["last_code_generated"] = None

    if feedback.lower() == "approve":
        print("Revisión de código: APROBADO.")
        # ¡CLAVE! Limpiamos el código y añadimos la bandera de aprobación.
        return {
            "review_feedback": None,
            "review_count": review_count,
            "frontend_code": None,
            "backend_code": None,
            "code_approved": True  # Nueva bandera para la aprobación
        }
    else:
        print(f"Revisión de código: REQUIERE CAMBIOS (Modo Relajado).")
        # ¡CLAVE! Devolvemos el feedback y el código para que se pueda iterar sobre él.
        state["review_feedback"] = feedback
        state["review_count"] = review_count
        return state
