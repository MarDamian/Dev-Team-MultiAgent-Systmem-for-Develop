# Contenido para: src/graph/workflow.py

from langgraph.graph import StateGraph
from src.graph.state import GraphState

# --- Importar todos los nodos de los agentes y herramientas ---
from src.agents.supervisor_agent import supervisor_node
from src.agents.conversational_agent import conversational_node
from src.agents.multimodal_analyzer_agent import multimodal_analyzer_node
from src.agents.ui_ux_designer_agent import ui_ux_designer_node # <-- ¡NUEVO AGENTE!
from src.agents.planner import planner_node
from src.agents.backend_developer import backend_developer_node
from src.agents.frontend_developer import frontend_developer_node
from src.agents.code_revisor import review_code_node
from src.tools.python_repl import execute_code

# --- Función Central de Enrutamiento del Grafo ---

def route_to_specialist(state: dict) -> str:
    """
    Lee la decisión del supervisor y enruta la tarea al nodo correspondiente.
    Esta es la única función de enrutamiento en el grafo.
    """
    decision = state.get("routing_decision")
    print(f"---LÓGICA DE ENRUTAMIENTO CENTRAL: Decisión del Supervisor = {decision}---")
    
    # El supervisor ahora devuelve directamente el nombre del nodo.
    # Si la decisión no es un nodo válido, el supervisor devuelve '__end__'.
    return decision

# --- Constructor del Grafo Principal ---

def build_graph(checkpointer):
    """
    Construye el grafo completo con la arquitectura Supervisor/Trabajador.
    """
    workflow = StateGraph(GraphState)

    # --- Añadir TODOS los nodos al grafo ---
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("conversational_agent", conversational_node)
    workflow.add_node("multimodal_analyzer", multimodal_analyzer_node)
    workflow.add_node("ui_ux_designer", ui_ux_designer_node) # <-- ¡NUEVO NODO!
    workflow.add_node("planner", planner_node)
    workflow.add_node("develop_backend", backend_developer_node)
    workflow.add_node("develop_frontend", frontend_developer_node)
    workflow.add_node("review_code", review_code_node)
    workflow.add_node("execute_code", execute_code)

    # --- Definir el Flujo del Grafo (Arquitectura "Hub and Spoke") ---
    workflow.set_entry_point("supervisor")

    # El supervisor es el único que toma decisiones de enrutamiento.
    workflow.add_conditional_edges(
        "supervisor",
        route_to_specialist,
        {
            # El mapeo ahora es directo desde la decisión a todos los nodos posibles.
            "conversational_agent": "conversational_agent",
            "multimodal_analyzer": "multimodal_analyzer",
            "ui_ux_designer": "ui_ux_designer", # <-- ¡NUEVA RUTA!
            "planner": "planner",
            "develop_backend": "develop_backend",
            "develop_frontend": "develop_frontend",
            "review_code": "review_code",
            "execute_code": "execute_code",
            "__end__": "__end__"  # Asegura que el grafo pueda terminar.
        }
    )

    # Todos los nodos de especialistas, después de completar su tarea,
    # devuelven el control al supervisor.
    workflow.add_edge("conversational_agent", "supervisor")
    workflow.add_edge("multimodal_analyzer", "supervisor")
    workflow.add_edge("ui_ux_designer", "supervisor")
    workflow.add_edge("planner", "supervisor")
    workflow.add_edge("develop_backend", "supervisor")
    workflow.add_edge("develop_frontend", "supervisor")
    workflow.add_edge("review_code", "supervisor")
    workflow.add_edge("execute_code", "supervisor")

    # --- Compilar el Grafo ---
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["execute_code"]
    )
    
    print("Grafo final y simplificado compilado exitosamente.")
    return app
