from langgraph.graph import StateGraph, END
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
from src.agents.database_architech_agent import database_architech_node


def route_to_specialist(state: dict) -> str:
    """Enruta desde el supervisor a los especialistas o finaliza."""
    decision = state.get("routing_decision")
    print(f"---LÓGICA DE ENRUTAMIENTO CENTRAL: Decisión del Supervisor = {decision}---")
    return decision


def should_continue_or_end(state: dict) -> str:
    """
    Decide si continuar al supervisor o finalizar el flujo.
    
    Esta función se ejecuta después de cada agente especialista para determinar
    si la tarea está completa o si debe continuar el procesamiento.
    """
    # Condiciones de finalización
    if state.get("code_approved"):
        print("✓ Flujo finalizado: Código aprobado")
        return END
    
    if state.get("task_complete"):
        print("✓ Flujo finalizado: Tarea simple completada")
        return END
    
    # Protección adicional: si hay demasiadas iteraciones
    iterations = state.get("supervisor_iterations", 0)
    if iterations > 10:
        print(f"⚠️ Flujo finalizado: Límite de iteraciones ({iterations})")
        return END
    
    # Continuar al supervisor para siguiente paso
    print(f"→ Regresando al supervisor (iteración {iterations})")
    return "supervisor"


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
    workflow.add_node("database_architech", database_architech_node)
    
    # Punto de entrada
    workflow.set_entry_point("supervisor")

    # --- ENRUTAMIENTO DESDE EL SUPERVISOR ---
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
            "database_architech": "database_architech",
            "__end__": END
        }
    )

    # --- ENRUTAMIENTO DE REGRESO (CON CONDICIÓN DE SALIDA) ---
    # CAMBIO CLAVE: Usar conditional_edges en lugar de add_edge directo
    
    workflow.add_conditional_edges(
        "conversational_agent",
        should_continue_or_end,
        {
            "supervisor": "supervisor",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "multimodal_analyzer",
        should_continue_or_end,
        {
            "supervisor": "supervisor",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "ui_ux_designer",
        should_continue_or_end,
        {
            "supervisor": "supervisor",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "planner",
        should_continue_or_end,
        {
            "supervisor": "supervisor",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "develop_backend",
        should_continue_or_end,
        {
            "supervisor": "supervisor",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "develop_frontend",
        should_continue_or_end,
        {
            "supervisor": "supervisor",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "quality_auditor",
        should_continue_or_end,
        {
            "supervisor": "supervisor",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "database_architech",
        should_continue_or_end,
        {
            "supervisor": "supervisor",
            END: END
        }
    )

    app = workflow.compile(checkpointer=checkpointer)
    
    print("✅ Grafo compilado exitosamente con salidas condicionales")
    return app