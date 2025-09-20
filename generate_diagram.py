# Contenido para: generate_diagram.py

import os
from langgraph.checkpoint.sqlite import SqliteSaver # <-- IMPORTAMOS LA LIBRERÍA
from src.graph.workflow import build_graph

def main():
    """
    Función principal para generar y guardar la imagen del grafo,
    gestionando correctamente el checkpointer.
    """
    print("Gestionando el checkpointer en memoria para construir el grafo...")

    # CORRECCIÓN CLAVE: Usamos 'with' para crear y gestionar correctamente el checkpointer,
    # tal como lo hacemos en main.py.
    with SqliteSaver.from_conn_string(":memory:") as memory:
        
        print("Construyendo el grafo...")
        # Ahora llamamos a build_graph pasándole el checkpointer que requiere.
        compiled_graph = build_graph(checkpointer=memory)

        print("Generando la imagen del grafo usando Mermaid... (esto puede tardar un momento)")

        try:
            # El resto de la lógica para generar la imagen es la misma.
            png_bytes = compiled_graph.get_graph().draw_mermaid_png()

            output_filename = "workflow_diagram.png"

            with open(output_filename, "wb") as f:
                f.write(png_bytes)
            
            print(f"\n¡Éxito! La imagen del grafo se ha guardado en: {os.path.abspath(output_filename)}")

        except Exception as e:
            print("\n--- ERROR AL GENERAR LA IMAGEN ---")
            print("No se pudo generar la imagen del grafo.")
            print(f"Detalle del error: {e}")
            print("\nRecordatorio: ¿Has instalado las dependencias para renderizar?")
            print("1. pip install playwright")
            print("2. playwright install")

if __name__ == "__main__":
    main()