# En el archivo: src/tools/code_reader.py

import os
from typing import List, Dict # Asegúrate de que List y Dict estén importados

def list_code_files_in_directory(directory_path: str) -> List[str]:
    """
    Busca de forma recursiva todos los archivos dentro de un directorio y sus subdirectorios.

    Args:
        directory_path: La ruta a la carpeta raíz que se va a escanear (ej. 'outputs').

    Returns:
        Una lista de rutas completas a cada archivo encontrado.
        Devuelve una lista vacía si el directorio no existe o no contiene archivos.
    """
    found_files = []
    
    if not os.path.isdir(directory_path):
        print(f"ADVERTENCIA (Herramienta list_files): El directorio '{directory_path}' no existe.")
        return []

    # os.walk() recorre el directorio de arriba hacia abajo (recursivamente)
    for dirpath, _, filenames in os.walk(directory_path):
        for filename in filenames:
            # Construimos la ruta completa y la añadimos a la lista
            full_path = os.path.join(dirpath, filename)
            found_files.append(full_path)
    
    if not found_files:
        print(f"Herramienta 'list_files': No se encontraron archivos en '{directory_path}' o sus subdirectorios.")
    else:
        print(f"Herramienta 'list_files' (recursiva): Encontrados {len(found_files)} archivos en '{directory_path}'.")
        
    return found_files


# Tu función existente debe permanecer en este archivo también
def read_code_from_files(file_paths: List[str]) -> Dict[str, str]:
    """
    Lee el contenido de una lista de archivos de código y lo devuelve como un diccionario.
    Maneja de forma segura los casos en que un archivo no se encuentra.
    ... (el resto de tu función no cambia)
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
            code_contents[filename] = ""
            
    return code_contents

def format_code_for_prompt(code_files: Dict[str, str]) -> str:
    """
    Toma un diccionario de archivos de código y lo formatea en un solo string
    para ser incluido en un prompt de LLM.

    Args:
        code_files: Un diccionario donde las claves son nombres de archivo y los
                    valores son el contenido del archivo.

    Returns:
        Un único string con todo el código formateado, listo para el prompt.
        Los archivos con contenido vacío son ignorados.
    """
    full_code_parts = []
    for filename, content in code_files.items():
        # Solo procesar si el archivo tiene contenido
        if content and content.strip():
            full_code_parts.append(f"--- CÓDIGO DEL ARCHIVO: {filename} ---\n{content}")
    
    formatted_string = "\n\n".join(full_code_parts)
    print(f"Herramienta 'format_code': Formateados {len(full_code_parts)} archivos en un solo bloque de texto.")
    
    return formatted_string