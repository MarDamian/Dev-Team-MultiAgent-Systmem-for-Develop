from langgraph.graph import StateGraph
from src.graph.state import GraphState

# --- Importar todos los nodos de los agentes y herramientas ---
from src.agents.supervisor_agent import supervisor_node
from src.agents.conversational_agent import conversational_node
from src.agents.multimodal_analyzer_agent import multimodal_analyzer_node
from src.agents.ui_ux_designer_agent import ui_ux_designer_node
from src.agents.planner import planner_node
from src.agents.backend_developer import backend_developer_node
from src.agents.frontend_developer import frontend_developer_node
from src.agents.quality_auditor import quality_auditor_node 


def route_to_specialist(state: dict) -> str:
    decision = state.get("routing_decision")
    print(f"---LÓGICA DE ENRUTAMIENTO CENTRAL: Decisión del Supervisor = {decision}---")
    return decision

# --- Constructor del Grafo Principal ---

def build_graph(checkpointer):
    workflow = StateGraph(GraphState)

    # --- Añadir TODOS los nodos al grafo ---
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("conversational_agent", conversational_node)
    workflow.add_node("multimodal_analyzer", multimodal_analyzer_node)
    workflow.add_node("ui_ux_designer", ui_ux_designer_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("develop_backend", backend_developer_node)
    workflow.add_node("develop_frontend", frontend_developer_node)
    workflow.add_node("quality_auditor", quality_auditor_node)
    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_to_specialist,
        {
            "conversational_agent": "conversational_agent",
            "multimodal_analyzer": "multimodal_analyzer",
            "ui_ux_designer": "ui_ux_designer",
            "planner": "planner",
            "develop_backend": "develop_backend",
            "develop_frontend": "develop_frontend",
            "quality_auditor": "quality_auditor",
            "__end__": "__end__"
        }
    )

    # Todos los nodos de especialistas devuelven el control al supervisor.
    workflow.add_edge("conversational_agent", "supervisor")
    workflow.add_edge("multimodal_analyzer", "supervisor")
    workflow.add_edge("ui_ux_designer", "supervisor")
    workflow.add_edge("planner", "supervisor")
    workflow.add_edge("develop_backend", "supervisor")
    workflow.add_edge("develop_frontend", "supervisor")
    workflow.add_edge("quality_auditor", "supervisor")

    app = workflow.compile(
        checkpointer=checkpointer
    )
    
    print("Grafo final compilado exitosamente.")
    return app