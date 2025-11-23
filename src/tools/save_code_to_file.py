# Contenido para: src/tools/save_code_to_file.py

import os
from .project_manager import get_active_project_path

def save_code_to_file(filename: str, code: str | None) -> str | None:
    """
    Guarda el código generado en un archivo específico dentro del proyecto activo.
    Puede manejar subdirectorios (ej: 'frontend/index.html').
    Sobrescribe el archivo si ya existe.
    
    IMPORTANTE: Ahora usa el sistema de gestión de proyectos. El código se guarda
    en la estructura: outputs/{project_id}/{subfolder}/{filename}
    """
    if not code:
        return None
    
    # Obtener la ruta base del proyecto activo
    project_base = get_active_project_path()
    
    if not project_base:
        print("⚠️ ADVERTENCIA: No hay proyecto activo. Usando carpeta 'outputs' por defecto.")
        project_base = "outputs"
        os.makedirs(project_base, exist_ok=True)
    
    try:
        # Construir la ruta completa del archivo
        filepath = os.path.join(project_base, filename)
        
        # Obtener el directorio de la ruta del archivo (ej: 'outputs/project_id/frontend')
        directory = os.path.dirname(filepath)
        
        # Asegurarse de que toda la estructura de directorios exista
        os.makedirs(directory, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        print(f"→ Código guardado/sobrescrito en '{filepath}'")
        return filepath
    except Exception as e:
        # Usamos f-string para formatear la variable en el mensaje de error
        print(f"Error al guardar el archivo {filename}: {e}")
        return None