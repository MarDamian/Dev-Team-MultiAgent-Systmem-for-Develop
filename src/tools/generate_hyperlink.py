import os

def generate_local_html_hyperlink(file_path: str) -> str:
    """
    Genera un hipervínculo de archivo local para un archivo HTML.
    """
    if not os.path.exists(file_path):
        return ""
    
    absolute_path = os.path.abspath(file_path)
    # Reemplazar backslashes por forward slashes para URL en Windows
    hyperlink = f"file:///{absolute_path.replace(os.sep, '/')}"
    return hyperlink

def create_hyperlink_message(hyperlink: str) -> str:
    """
    Crea un mensaje formateado con el hipervínculo.
    """
    if hyperlink:
        return f"\n\n¡Se ha generado un sitio web! Puedes verlo aquí: [Abrir sitio web]({hyperlink})"
    return ""
