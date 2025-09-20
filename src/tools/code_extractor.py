import re
from .save_code_to_file import save_code_to_file

def extract_and_save_code(full_code: str) -> dict:
    """
    Extrae bloques de código HTML, CSS y JavaScript de una cadena de texto,
    los guarda en archivos estándar y devuelve un diccionario con el código.
    """
    # Versión final y robusta de los regex para asegurar la extracción.
    html_match = re.search(r"<!---\s*HTML_CODE_START\s*--->([\s\S]*?)<!---\s*HTML_CODE_END\s*--->", full_code, re.IGNORECASE)
    css_match = re.search(r"\/\*\s*---\s*CSS_CODE_START\s*---\s*\*\/([\s\S]*?)\/\*\s*---\s*CSS_CODE_END\s*---\s*\*\/", full_code, re.IGNORECASE)
    js_match = re.search(r"\/\/\s*---\s*JS_CODE_START\s*---([\s\S]*?)\/\/\s*---\s*JS_CODE_END\s*---", full_code, re.IGNORECASE)

    output_code = {}
    
    if html_match:
        code = html_match.group(1).strip()
        save_code_to_file("index.html", code)
        output_code['html'] = code
        
    if css_match:
        code = css_match.group(1).strip()
        save_code_to_file("style.css", code)
        output_code['css'] = code

    if js_match:
        code = js_match.group(1).strip()
        save_code_to_file("script.js", code)
        output_code['javascript'] = code

    print(f"Código extraído y guardado: {list(output_code.keys())}")
    return output_code
