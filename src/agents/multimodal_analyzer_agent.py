# Contenido para: src/agents/multimodal_analyzer_agent.py

from src.model import creative_llm
from src.tools.file_analyzer import prepare_multimodal_input
from langchain_core.messages import HumanMessage

def multimodal_analyzer_node(state: dict) -> dict:
    """
    Este agente se especializa en describir el contenido de los archivos.
    """
    print("---AGENTE: ANALISTA MULTIMODAL (ESPECIALISTA)---")
    user_input = state["user_input"]
    file_paths = state.get("file_paths", [])
    
    # Determinar si hay un video entre los archivos adjuntos
    has_video = any(file_path.endswith((".mp4", ".mov", ".avi", ".mkv")) for file_path in file_paths)

    if has_video:
        prompt_text = f"""
        Eres un experto analista de UI/UX. La petición del usuario es: "{user_input}".
        Has recibido un video con indicaciones. Tu tarea es analizar el video y extraer una especificación DETALLADA y ESTRUCTURADA de UI/UX para el frontend.

        **INSTRUCCIONES CRÍTICAS:**
        - **IGNORA COMPLETAMENTE CUALQUIER DESCRIPCIÓN DE ACCIONES DEL USUARIO (CLICKS, NAVEGACIÓN, MOVIMIENTOS DEL RATÓN, ETC.).**
        - **TU ÚNICO ENFOQUE DEBE SER EN LOS ASPECTOS VISUALES Y DE DISEÑO DE LA INTERFAZ DE USUARIO.**
        - **NO MENCIONES NINGUNA ACCIÓN DEL USUARIO EN TU RESPUESTA.**

        Tu respuesta DEBE incluir las siguientes secciones, con la mayor cantidad de detalles visuales posible:

        **1. Paleta de Colores Principal:**
        - Colores dominantes (fondo, texto, elementos interactivos).
        - Ejemplos de códigos de color si son discernibles (ej. #FFFFFF, #000000).

        **2. Disposición y Estructura (Layout):**
        - Descripción general de la distribución de los elementos en la página (ej. barra lateral izquierda, encabezado fijo, contenido central).
        - Uso de columnas, filas, cuadrículas.
        - Alineación de elementos (izquierda, derecha, centro).

        **3. Tamaños y Espaciado:**
        - Tamaños relativos de elementos (ej. "el encabezado es grande", "los botones son pequeños").
        - Espaciado entre elementos (márgenes, paddings).

        **4. Tipografía:**
        - Tipos de fuente aparentes (ej. serif, sans-serif).
        - Tamaños de texto para títulos, subtítulos, cuerpo de texto.

        **5. Componentes de UI Clave:**
        - Descripción de botones (forma, color, texto).
        - Campos de entrada (estilo, placeholders).
        - Iconos (descripción, ubicación).
        - Imágenes (si aplica, cómo se muestran).
        - Barras de navegación, menús, etc.

        **6. Interacciones y Animaciones (si son visibles):**
        - Comportamiento al hacer clic en botones/enlaces.
        - Efectos de hover, transiciones.
        - Apertura de modales o diálogos.

        Tu objetivo es proporcionar una guía visual exhaustiva para el desarrollador frontend.
        """
    else:
        prompt_text = f"""
        Eres un experto analista. La petición del usuario es: "{user_input}".
        Tu única tarea es analizar los archivos adjuntos y proporcionar una descripción detallada y útil en respuesta a la petición del usuario.
        """
    
    multimodal_content = prepare_multimodal_input(prompt_text, file_paths)
    message = HumanMessage(content=multimodal_content)
    response = creative_llm.invoke([message])
    
    analysis_result = response.content.strip()

    print(f"--- SALIDA DEL ANALISTA MULTIMODAL: {analysis_result[:80]}... ---")

    if has_video:
        # Si había un video, guardamos el resultado como especificación de UI/UX
        return {"ui_ux_spec": analysis_result, "task_complete": False} # No completamos la tarea, solo preparamos la especificación
    else:
        # Si no había video, es una respuesta final o una descripción general
        return {"final_response": analysis_result, "task_complete": True}
