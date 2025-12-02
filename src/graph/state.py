from typing import TypedDict, List, Dict, Annotated, Optional, Union

class GraphState(TypedDict):
    # --- Campos de Conversación y Decisión ---
    user_input: str
    chat_history: Annotated[List[str], lambda x, y: x + y]
    final_response: Optional[str]
    task_complete: Optional[bool]
    routing_decision: str
    supervisor_iterations: Optional[int] 

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
    nodes_visited: Optional[List[str]]
    backend_iterations: Optional[int]
    frontend_iterations: Optional[int]
    database_iterations: Optional[int]

    # --- CAMPO CLAVE PARA VISUALIZAR EL PROCESO RAG ITERATIVO ---
    rag_steps: Annotated[List[str], lambda x, y: x + y]
    
    # --- NUEVOS CAMPOS PARA GESTIÓN DE PROYECTOS Y CONTRATOS ---
    project_id: Optional[str]
    project_metadata: Optional[Dict]
    api_contracts: Optional[List[Dict]]
    data_contracts: Optional[List[Dict]]
    contract_validation_results: Optional[Dict]
