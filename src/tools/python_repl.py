# Contenido para: src/tools/python_repl.py

# CORRECCIÓN: La ruta de importación ha sido actualizada a su nueva ubicación.
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import Tool

# Creamos una instancia de la herramienta PythonREPL
repl = PythonREPL()

# La envolvemos en un objeto Tool para que LangGraph pueda usarla fácilmente
python_repl_tool = Tool(
    name="python_repl",
    description="Una herramienta para ejecutar código Python. Toma como entrada un bloque de código Python y devuelve el resultado de su ejecución.",
    func=repl.run,
)

def execute_code(state: dict) -> dict:
    """
    Ejecuta el código que se encuentra en el estado usando la herramienta PythonREPL.
    """
    print("---HERRAMIENTA: EJECUTOR DE CÓDIGO---")
    
    # Solo intentaremos ejecutar si el código es de backend y es Python
    plan = state.get("dev_plan", {})
    if plan.get("backend_tech", "").lower().startswith("python"):
        code_to_run = state.get("backend_code")
        if not code_to_run:
            return {"tool_output": "No se proporcionó código de backend para ejecutar."}
        
        try:
            output = python_repl_tool.invoke(code_to_run)
            print(f"Resultado de la ejecución: {output}")
            return {"tool_output": output}
        except Exception as e:
            print(f"Error ejecutando el código: {e}")
            return {"tool_output": f"Error: {e}"}
    else:
        output_msg = "La ejecución de código fue omitida porque el código generado no es Python."
        print(output_msg)
        return {"tool_output": output_msg}