import os

def save_code_to_file(filename: str, code: str | None) -> str | None:
    """
    Guarda el código generado en un archivo específico en la carpeta 'outputs'
    y devuelve la ruta del archivo. Sobrescribe el archivo si ya existe.
    """
    if not code:
        return None
    
    try:
        filepath = os.path.join("outputs", filename)
        
        # Asegurarse de que el directorio 'outputs' exista
        os.makedirs("outputs", exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        print(f"-> Código guardado/sobrescrito en '{filepath}'")
        return filepath
    except Exception as e:
        print(f"Error al guardar el archivo {filepath}: {e}")
        return None
