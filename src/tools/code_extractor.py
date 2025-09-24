# Contenido para: src/tools/code_extractor.py

import re
from .save_code_to_file import save_code_to_file

# --- Definición de los tipos de archivos ---
# Esto nos ayudará a decidir en qué carpeta guardar cada archivo.
FRONTEND_LANGS = {'html', 'css', 'javascript', 'js'}
BACKEND_LANGS = {'python', 'sql', 'requirements.txt', 'dockerfile'} # Añadimos algunos extra para el futuro

def extract_and_save_code(full_code_string: str) -> dict:
    """
    Extrae múltiples bloques de código de una cadena, los clasifica como frontend o backend,
    y los guarda en subcarpetas ('outputs/frontend' o 'outputs/backend') usando save_code_to_file.
    Devuelve un diccionario con el código extraído.
    """
    print("---HERRAMIENTA: EXTRACTOR Y ORGANIZADOR DE CÓDIGO---")
    
    # El mismo patrón universal que desarrollamos antes. Funciona para ambos casos.
    pattern = re.compile(
        r"(?:<!---|\/\* ---|\/\/ ---)\s*"
        r"([\w\.]+)_CODE_START"
        r"\s*(?:--- \*/|--->|---)"
        r"([\s\S]*?)"
        r"(?:<!---|\/\* ---|\/\/ ---)\s*"
        r"\1_CODE_END"
        r"\s*(?:--- \*/|--->|---)",
        re.IGNORECASE
    )

    matches = pattern.finditer(full_code_string)
    
    extracted_code = {}
    for match in matches:
        lang_or_filename = match.group(1).lower()
        code = match.group(2).strip()
        
        # Guardar en el diccionario de resultados.
        key = 'javascript' if lang_or_filename == 'js' else lang_or_filename
        extracted_code[key] = code

    if not extracted_code:
        print("ADVERTENCIA: No se encontraron bloques de código con los delimitadores esperados.")
        return {}

    # --- Lógica de guardado y organización ---
    for key, code in extracted_code.items():
        # 1. Determinar la subcarpeta de destino
        if key in FRONTEND_LANGS:
            subdirectory = "frontend"
        elif key in BACKEND_LANGS:
            subdirectory = "backend"
        else:
            subdirectory = "misc" # Carpeta para tipos no reconocidos

        # 2. Determinar el nombre del archivo
        if key == 'html':
            filename = "index.html"
        elif key == 'css':
            filename = "style.css"
        elif key == 'javascript':
            filename = "script.js"
        elif key == 'python':
            filename = "app.py"
        elif key == 'requirements.txt':
            filename = "requirements.txt"
        else:
            # Fallback para sql, dockerfile, etc.
            ext = key.split('.')[-1] if '.' in key else key
            filename = f"{key}.{ext}"

        # 3. Construir la ruta final y guardar usando la herramienta
        # La herramienta save_code_to_file necesita una ruta relativa a 'outputs', 
        # así que le pasamos 'frontend/index.html', por ejemplo.
        final_filename = f"{subdirectory}/{filename}"
        save_code_to_file(final_filename, code)
            
    return extracted_code