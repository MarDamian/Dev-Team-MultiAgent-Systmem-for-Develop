import os
from typing import Dict, List

def read_code_from_files(file_paths: List[str]) -> Dict[str, str]:
    """
    Lee el contenido de una lista de archivos de código y lo devuelve como un diccionario.
    Maneja de forma segura los casos en que un archivo no se encuentra.

    Args:
        file_paths: Una lista de rutas completas a los archivos de código (ej. ['outputs/index.html']).

    Returns:
        Un diccionario donde las claves son los nombres de los archivos (ej. 'index.html')
        y los valores son el contenido del archivo como un string.
    """
    code_contents = {}
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_contents[filename] = f.read()
                print(f"Herramienta 'read_code': Leído exitosamente '{file_path}'")
        except FileNotFoundError:
            print(f"ADVERTENCIA (Herramienta read_code): No se encontró el archivo '{file_path}'. Se devolverá un contenido vacío.")
            code_contents[filename] = ""  # Devolver string vacío si el archivo no existe
            
    return code_contents