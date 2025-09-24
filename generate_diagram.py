# Contenido para: generate_diagram.py
# --- VERSIÓN DEFINITIVA: GENERA EL CÓDIGO DE TEXTO PARA LA WEB ---

import os
from langgraph.checkpoint.sqlite import SqliteSaver
from src.graph.workflow import build_graph

def main():
    """
    Función principal para generar la definición de texto del grafo (código Mermaid)
    y guardarla en un archivo, lista para visualizar en la web.
    """
    print("Gestionando el checkpointer en memoria para construir el grafo...")

    with SqliteSaver.from_conn_string(":memory:") as memory:
        
        print("Construyendo el grafo...")
        compiled_graph = build_graph(checkpointer=memory)

        print("Generando la definición de texto del grafo (código Mermaid)...")

        try:
            # --- FUNCIÓN CLAVE ---
            # .draw_mermaid() extrae el código de texto del diagrama.
            # Es una operación local, instantánea y nunca falla por problemas de red.
            mermaid_text = compiled_graph.get_graph().draw_mermaid()

            output_filename = "diagrama_definicion.md"

            # Guardamos el texto en un archivo, envuelto en un bloque de código Mermaid
            # para que sea fácil de copiar y pegar.
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write("```mermaid\n")
                f.write(mermaid_text)
                f.write("\n```")
            
            print(f"\n¡Éxito! El código del diagrama se ha guardado en: {os.path.abspath(output_filename)}")
            print("\n--- ¡ACCIÓN REQUERIDA! ---")
            print("1. Abre el archivo 'diagrama_definicion.md' que se acaba de crear.")
            print("2. Copia TODO el contenido (incluyendo ```mermaid).")
            print("3. Pégalo en el editor online de Mermaid para visualizarlo y descargarlo:")
            print("   https://mermaid.live")

        except Exception as e:
            print(f"\n--- ERROR AL EXTRAER LA DEFINICIÓN ---")
            print(f"Detalle del error: {e}")

if __name__ == "__main__":
    main()