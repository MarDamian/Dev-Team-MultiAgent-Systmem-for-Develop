from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


try:
    analytical_llm = ChatGroq(
        model="llama-3.3-70b-versatile",  
        groq_api_key=GROQ_API_KEY,
        temperature=0.3
    )

    conversational_llm = ChatGroq(
        model="llama-3.1-8b-instant",  
        groq_api_key=GROQ_API_KEY,
        temperature=0.7
    )
    
    print("✅ Groq configurado correctamente")
except Exception as e:
    print(f"⚠️ Error configurando Groq: {e}")
    print("   Obtén tu API key en: https://console.groq.com/")
    analytical_llm = None
    conversational_llm = None

# --- GEMINI (GRATIS - 250 req/día) ---
# Para: Generación de código (Frontend, Backend, Database)
try:
    creative_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,
        max_output_tokens=8192
    )
    print("✅ Gemini configurado correctamente")
except Exception as e:
    print(f"⚠️ Error configurando Gemini: {e}")
    print("   Obtén tu API key en: https://aistudio.google.com/apikey")
    creative_llm = None


def validate_configuration():
    """Valida que al menos un modelo esté configurado."""
    if analytical_llm is None and creative_llm is None:
        print("\n❌ ERROR CRÍTICO: No hay modelos configurados")
        return False
    
    print("\n Configuración de modelos lista:")
    if analytical_llm:
        print("   ✓ Analytical LLM: Groq Llama 3.3 70B")
    if conversational_llm:
        print("   ✓ Conversational LLM: Groq llama-3.1-8b-instant")
    if creative_llm:
        print("   ✓ Creative LLM: Gemini 2.0 Flash")
    print()
    return True

# Ejecutar validación al importar
validate_configuration()

__all__ = [
    'analytical_llm',
    'creative_llm',
    'conversational_llm'
]