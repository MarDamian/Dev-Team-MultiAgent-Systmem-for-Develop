# Contenido para: src/config.py

import os
from dotenv import load_dotenv

# Cargar variables del archivo .env al iniciar el módulo
load_dotenv()

def get_config():
    """
    Carga y devuelve la configuración principal de la aplicación.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GEMINI_MODEL")
    
    if not api_key:
        raise ValueError("La clave de API de Google no se encontró. Revisa tu archivo .env.")
    if not model_name:
        raise ValueError("El nombre del modelo de Gemini no se encontró. Revisa tu archivo .env.")
    
    # Establecer la API key en el entorno para que las librerías de Google la usen
    os.environ["GOOGLE_API_KEY"] = api_key
    
    print(f"Configuración cargada: Usando el modelo '{model_name}'")
    
    return {"model_name": model_name}

# Obtenemos la configuración una vez y la hacemos disponible para importar
APP_CONFIG = get_config()