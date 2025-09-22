from typing import TypedDict, List, Dict, Annotated, Optional, Union

class GraphState(TypedDict):
    # --- Campos de Conversación y Decisión ---
    user_input: str
    chat_history: Annotated[List[str], lambda x, y: x + y]
    final_response: Optional[str]
    task_complete: Optional[bool]
    routing_decision: str

    # --- Campos de Desarrollo y Archivos ---
    file_paths: List[str]
    file_description: Optional[str] # Campo opcional para descripciones de archivos
    ui_ux_spec: Optional[str]
    dev_plan: Optional[Dict[str, str]]

    # --- Campos de Código (con tipado mejorado) ---
    # El código de frontend puede ser un diccionario (html, css, js), mientras que el backend suele ser un solo string.
    frontend_code: Optional[Dict[str, str]]
    backend_code: Optional[str]
    last_code_generated: Optional[Union[str, Dict[str, str]]]

    # --- Campos de Auditoría y Feedback --
    feedback: Optional[str]
    review_feedback: Optional[str]
    review_count: int
    code_approved: Optional[bool] # Bandera para finalizar el ciclo de desarrollo

    # --- NUEVOS CAMPOS PARA EL RAG ITERATIVO DEL PLANNER ---
    # El estado actual de la investigación del planner ('continue' o 'complete')
    rag_status: Optional[str]
    # El contexto de la base de conocimientos acumulado a través de las iteraciones
    rag_context: Optional[str]
    # Una lista de las preguntas que el planner ya ha hecho para evitar repeticiones
    rag_queries_made: Optional[List[str]]

    # --- CAMPO CLAVE PARA VISUALIZAR EL PROCESO RAG ITERATIVO ---
    rag_steps: Annotated[List[str], lambda x, y: x + y]
