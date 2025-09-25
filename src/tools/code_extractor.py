# Contenido para: src/tools/code_extractor.py

import re
from .save_code_to_file import save_code_to_file

def extract_and_save_code(full_code_string: str, default_folder: str) -> dict:
    """
    Extrae múltiples bloques de código de una cadena y los guarda en una subcarpeta
    especificada (ej. 'frontend' o 'backend'), usando nombres de archivo descriptivos
    extraídos de los delimitadores.

    Args:
        full_code_string: La cadena completa de texto generada por el LLM.
        default_folder: La carpeta de destino ('frontend', 'backend', 'misc', etc.).

    Returns:
        Un diccionario con el código extraído, usando el nombre de archivo como clave.
    """
    print(f"---HERRAMIENTA: EXTRACTOR Y ORGANIZADOR DE CÓDIGO (Guardando en: {default_folder})---")
    
    # Patrón universal que soporta varios tipos de comentarios: --, //, /*, <!--
    pattern = re.compile(
        r"(?:<!---|\/\* ---|\/\/ ---|-- ---)\s*"
        r"([\w\.-]+)_CODE_START"  # Permite '.' y '-' en el nombre del archivo
        r"\s*(?:--- \*/|--->|---)"
        r"([\s\S]*?)"
        r"(?:<!---|\/\* ---|\/\/ ---|-- ---)\s*"
        r"\1_CODE_END"
        r"\s*(?:--- \*/|--->|---)",
        re.IGNORECASE
    )

    matches = pattern.finditer(full_code_string)
    
    extracted_code = {}
    for match in matches:
        filename_key = match.group(1).lower()
        code = match.group(2).strip()
        extracted_code[filename_key] = code

    if not extracted_code:
        print("ADVERTENCIA: No se encontraron bloques de código con los delimitadores esperados.")
        return {}

    # --- Lógica de guardado y organización ---
    for filename, code in extracted_code.items():
        # La carpeta de destino es determinada por el agente que llama a la función.
        subdirectory = default_folder
    
        final_path = f"{subdirectory}/{filename}"
        save_code_to_file(final_path, code)
            
    return extracted_code