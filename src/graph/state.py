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
    ui_ux_spec: Optional[str]
    dev_plan: Optional[Dict[str, str]]

    frontend_code: Optional[Dict[str, str]]
    backend_code: Optional[str]
    last_code_generated: Optional[Union[str, Dict[str, str]]]
    db_schema: Optional[str]

    # --- Campos de Auditoría y Feedback --
    feedback: Optional[str]
    review_feedback: Optional[str]
    review_count: int
    code_approved: Optional[bool] 
    rag_status: Optional[str]
    rag_context: Optional[str]
    rag_queries_made: Optional[List[str]]
    analysis_result: Optional[str]

    # --- CAMPO CLAVE PARA VISUALIZAR EL PROCESO RAG ITERATIVO ---
    rag_steps: Annotated[List[str], lambda x, y: x + y]
