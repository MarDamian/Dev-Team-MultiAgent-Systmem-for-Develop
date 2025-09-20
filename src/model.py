# Contenido para: src/llm_provider.py

from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import APP_CONFIG

# Obtenemos el nombre del modelo de nuestra configuración centralizada
model_name = APP_CONFIG['model_name']

# Instancia del LLM para tareas creativas y de generación de código.
# Una ligera "temperatura" puede dar lugar a un código más natural.
creative_llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.4)

# Instancia del LLM para tareas de análisis y revisión que requieren consistencia.
# La temperatura 0 hace que las respuestas sean más deterministas y predecibles.
analytical_llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)