from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_cerebras import ChatCerebras
from langchain_cohere import ChatCohere
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")


try:
    analytical_llm3 = ChatGroq(
        model="llama-3.3-70b-versatile",  
        groq_api_key=GROQ_API_KEY,
        temperature=0.3
    )

    analytical_llm2 = ChatCohere(
        model="command-r-plus-08-2024",  
        api_key=COHERE_API_KEY,
        temperature=0.3
    )

    analytical_llm = ChatGoogleGenerativeAI(
        #model="gemini-2.5-flash",
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
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

try:
    creative_llm = ChatGoogleGenerativeAI(
        #model="gemini-2.5-flash",
        model="gemini-2.0-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3
    )
    print("✅ Gemini configurado correctamente")
except Exception as e:
    print(f"⚠️ Error configurando Gemini: {e}")
    print("   Obtén tu API key en: https://aistudio.google.com/apikey")
    creative_llm = None

try:
    advanced_llm1 = ChatCerebras(
        model="llama-3.3-70b",
        api_key=CEREBRAS_API_KEY,
        temperature=0.3
    )
    advanced_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        #model="gemini-2.5-pro",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3
    )
    print("✅ Cerebras configurado correctamente")
except Exception as e:
    print(f"⚠️ Error configurando Cerebras: {e}")
    print("   Obtén tu API key en: https://cloud.cerebras.ai/")
    advanced_llm = None


def validate_configuration():
    """Valida que al menos un modelo esté configurado."""
    if analytical_llm is None and creative_llm is None:
        print("\n❌ ERROR CRÍTICO: No hay modelos configurados")
        return False
    
    print("\n📋 Configuración de modelos lista:")
    if analytical_llm:
        print("   ✓ Analytical LLM: Groq Llama 3.3 70B Versatile")
    if conversational_llm:
        print("   ✓ Conversational LLM: Groq Llama 3.1 8B Instant")
    if creative_llm:
        print("   ✓ Creative LLM: Gemini 2.5 Flash Lite")
    if advanced_llm:
        print("   ✓ Advanced LLM (Code): Cerebras Llama 3.3 70B")
    print()
    return True

# Ejecutar validación al importar
validate_configuration()

__all__ = [
    'analytical_llm',
    'creative_llm',
    'conversational_llm',
    'advanced_llm'
]