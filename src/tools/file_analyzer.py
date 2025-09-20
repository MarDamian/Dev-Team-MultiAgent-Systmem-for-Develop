import mimetypes
import os
import base64
from typing import List, Dict, Any

mimetypes.init()

def get_mime_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type if mime_type else "application/octet-stream"

def prepare_multimodal_input(prompt_text: str, file_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Prepara el contenido para un mensaje multimodal, combinando texto y cualquier tipo de media
    (imágenes, audio, video) leyéndolos y codificándolos en Base64.
    """
    content = [{"type": "text", "text": prompt_text}]
    
    for file_path in file_paths:
        try:
            mime_type = get_mime_type(file_path)
            
            # Lógica para manejar PDFs y otros archivos multimedia.
            # CORRECCIÓN: Usar la extensión del archivo para PDFs es más robusto que depender del MIME type del sistema.
            if file_path.lower().endswith('.pdf'):
                print(f"Info: Leyendo y codificando PDF de '{file_path}'...")
                with open(file_path, "rb") as f:
                    file_data = f.read()
                encoded_data = base64.b64encode(file_data).decode('utf-8')
                content.append({
                    "type": "media",
                    "mime_type": "application/pdf", # Forzar el MIME type correcto
                    "data": encoded_data
                })
            elif mime_type.startswith("image/") or mime_type.startswith("audio/") or mime_type.startswith("video/"):
                print(f"Info: Leyendo y codificando datos de media de '{file_path}'...")
                with open(file_path, "rb") as f:
                    file_data = f.read()
                encoded_data = base64.b64encode(file_data).decode('utf-8')
                content.append({
                    "type": "media",
                    "mime_type": mime_type,
                    "data": encoded_data
                })
            else:
                print(f"Advertencia: El tipo de archivo {mime_type} no es soportado. Se omitirá: {file_path}")

        except Exception as e:
            print(f"Error procesando el archivo {file_path}: {e}")
            
    return content
