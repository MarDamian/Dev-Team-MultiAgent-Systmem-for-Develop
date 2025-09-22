from src.model import creative_llm
from src.tools.file_analyzer import prepare_multimodal_input
from langchain_core.messages import HumanMessage

def multimodal_analyzer_node(state: dict) -> dict:
    """
    Este agente se especializa en describir el contenido de los archivos.
    Su única responsabilidad es analizar y devolver el resultado.
    """
    print("---AGENTE: ANALISTA MULTIMODAL (ESPECIALISTA)---")
    user_input = state["user_input"]
    file_paths = state.get("file_paths", [])
    
    # El prompt puede permanecer igual, es muy bueno.
    prompt_text = f"""
    Eres un experto analista. La petición del usuario es: "{user_input}".
    Tu única tarea es analizar los archivos adjuntos y proporcionar una descripción detallada y útil en respuesta a la petición del usuario.
    """
    
    multimodal_content = prepare_multimodal_input(prompt_text, file_paths)
    message = HumanMessage(content=multimodal_content)
    response = creative_llm.invoke([message])
    
    analysis_result = response.content.strip()

    print(f"--- SALIDA DEL ANALISTA MULTIMODAL: {analysis_result[:80]}... ---")


    return {"final_response": analysis_result}