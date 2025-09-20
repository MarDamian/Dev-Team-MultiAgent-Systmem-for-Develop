# Contenido para: src/graph/state.py

from typing import TypedDict, List, Dict, Annotated

class GraphState(TypedDict):
    # --- Campos de Conversación y Decisión ---
    user_input: str
    chat_history: Annotated[List[str], lambda x, y: x + y]
    # La respuesta final generada por un agente de respuesta directa (conversacional, multimodal, etc.)
    final_response: str | None
    # Una bandera para indicar que una tarea de un solo paso ha terminado.
    task_complete: bool | None
    # La decisión de enrutamiento del supervisor.
    routing_decision: str

    # --- Campos de Desarrollo ---
    # La especificación técnica generada por el diseñador de UI/UX a partir de una maqueta.
    ui_ux_spec: str | None
    file_paths: List[str]
    file_description: str
    dev_plan: Dict[str, str] | None
    backend_code: str | None
    frontend_code: str | None
    review_feedback: str | None
    tool_output: str
    review_count: int
    last_code_generated: str | None
