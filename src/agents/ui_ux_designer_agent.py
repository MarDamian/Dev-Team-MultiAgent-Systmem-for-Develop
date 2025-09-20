# src/agents/ui_ux_designer_agent.py

from src.model import creative_llm
from src.tools.file_analyzer import prepare_multimodal_input
from langchain_core.messages import HumanMessage


def ui_ux_designer_node(state: dict) -> dict:
    print("---AGENTE: DISEÑADOR UI/UX (ESPECIALISTA)---")
    user_input = state["user_input"]
    file_paths = state.get("file_paths", [])

    if not file_paths:
        return {"ui_ux_spec": "Error: No se proporcionó ninguna imagen o video para el análisis de UI/UX."}

    is_video = any(path.lower().endswith(('.mp4', '.mov', '.avi', '.webm')) for path in file_paths)

    if is_video:
        prompt = f"""
        Eres un diseñador UI/UX experto. Analiza el archivo multimedia proporcionado
        y **NO OMITAS NINGUNA SECCIÓN**. Genera la especificación completa en formato Markdown,
        siguiendo estrictamente este orden y formato:

        ## 1. Estructura General y Layout
        - Describe la disposición principal de la interfaz, jerarquía visual y organización.

        ## 2. Paleta de Colores
        - Lista colores principales con sus códigos hexadecimales y su uso.

        ## 3. Tipografía
        - Detalla fuentes, tamaños, grosores y usos.

        ## 4. Desglose de Componentes
        - Lista de componentes reutilizables, su contenido, estilo y estados.

        ## 5. Recursos (Assets)
        - Lista de imágenes, iconos, ilustraciones y otros recursos necesarios.

        ## 6. Comportamiento y Animaciones
        - **Eventos de Usuario:** Tabla con columnas `Tiempo | Acción | Elemento | Cambio de Estado`.
        - **Transiciones de Estado:** Explica cómo cambia la interfaz después de cada evento.
        - **Animaciones:** Describe duración, dirección y estilo.
        - **Lógica de JavaScript:** Sugiere pseudocódigo o funciones para implementar.

        La petición original del usuario es: "{user_input}".
        No respondas fuera de este formato.
        """

    else:
        prompt = f"""
        Eres un diseñador UI/UX experto. Analiza el archivo multimedia proporcionado y **NO OMITAS NINGUNA SECCIÓN**.
        Genera la especificación en formato Markdown, siguiendo estrictamente este orden:

        ## 1. Estructura General y Layout
        ## 2. Paleta de Colores
        ## 3. Tipografía
        ## 4. Desglose de Componentes
        ## 5. Recursos (Assets)

        La petición original del usuario es: "{user_input}".
        """

    content = prepare_multimodal_input(prompt, file_paths)
    response = creative_llm.invoke([HumanMessage(content=content)])
    ui_ux_spec = response.content.strip()

    print(f"--- ESPECIFICACIÓN DE UI/UX GENERADA ---\n{ui_ux_spec[:500]}...\n---")
    return {"ui_ux_spec": ui_ux_spec}
