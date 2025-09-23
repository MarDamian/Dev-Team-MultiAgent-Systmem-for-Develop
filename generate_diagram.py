import os
from langgraph.checkpoint.sqlite import SqliteSaver 
from langgraph.graph import MermaidDrawMethod
from src.graph.workflow import build_graph

def main():
    """
    Función principal para generar y guardar la imagen del grafo,
    gestionando correctamente el checkpointer y exportando también el .mmd
    para inspección manual en caso de error.
    """
    print("Gestionando el checkpointer en memoria para construir el grafo...")

    with SqliteSaver.from_conn_string(":memory:") as memory:
        
        print("Construyendo el grafo...")
        compiled_graph = build_graph(checkpointer=memory)

        # 🔹 Exportar Mermaid code (texto)
        try:
            mermaid_code = compiled_graph.get_graph().draw_mermaid()
            mmd_filename = "workflow_diagram.mmd"
            with open(mmd_filename, "w", encoding="utf-8") as f:
                f.write(mermaid_code)
            print(f"\n✔ Código Mermaid exportado en: {os.path.abspath(mmd_filename)}")
            print("Puedes abrirlo en https://mermaid.live para validar la estructura.")
        except Exception as e:
            print("\n--- ERROR AL GENERAR EL CÓDIGO MERMAID ---")
            print(f"Detalle del error: {e}")
            return

        # 🔹 Intentar renderizar con Pyppeteer
        print("\nGenerando la imagen del grafo usando Mermaid con Pyppeteer... (esto puede tardar un momento)")

        try:
            png_bytes = compiled_graph.get_graph().draw_mermaid_png(
                draw_method=MermaidDrawMethod.PYPPETEER
            )

            output_filename = "workflow_diagram.png"
            with open(output_filename, "wb") as f:
                f.write(png_bytes)
            
            print(f"\n¡Éxito! La imagen del grafo se ha guardado en: {os.path.abspath(output_filename)}")

        except Exception as e:
            print("\n--- ERROR AL GENERAR LA IMAGEN ---")
            print("No se pudo generar la imagen del grafo.")
            print(f"Detalle del error: {e}")
            print("⚠ Pero el archivo .mmd ya fue generado para revisar en Mermaid Live.")

if __name__ == "__main__":
    main()
