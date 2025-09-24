# Contenido para: src/tools/save_code_to_file.py

import os

def save_code_to_file(filename: str, code: str | None) -> str | None:
    """
    Guarda el código generado en un archivo específico dentro de la carpeta 'outputs'.
    Puede manejar subdirectorios (ej: 'frontend/index.html').
    Sobrescribe el archivo si ya existe.
    """
    if not code:
        return None
    
    try:
        # Construir la ruta completa del archivo
        filepath = os.path.join("outputs", filename)
        
        # --- CAMBIO CLAVE ---
        # Obtener el directorio de la ruta del archivo (ej: 'outputs/frontend')
        directory = os.path.dirname(filepath)
        
        # Asegurarse de que toda la estructura de directorios exista
        os.makedirs(directory, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        print(f"-> Código guardado/sobrescrito en '{filepath}'")
        return filepath
    except Exception as e:
        # Usamos f-string para formatear la variable en el mensaje de error
        print(f"Error al guardar el archivo {filename}: {e}")
        return None