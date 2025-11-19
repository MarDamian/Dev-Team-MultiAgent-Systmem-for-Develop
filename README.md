# Sistema Multiagente de Soporte al Desarrollo de Software (SMA-DevTeam)

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-v0.3-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange)

## 📄 Descripción General

[cite_start]Este proyecto implementa un **Sistema Multiagente (SMA)** diseñado para automatizar y asistir en las fases iniciales del desarrollo de software[cite: 43]. [cite_start]El sistema es capaz de interpretar especificaciones **multimodales** (texto, diagramas, imágenes, bocetos) para generar artefactos de software estructurados, planes de desarrollo y código fuente funcional[cite: 45, 51].

[cite_start]La arquitectura emula un equipo de desarrollo humano, donde agentes autónomos especializados (Analistas, Arquitectos, Desarrolladores y Auditores QA) colaboran bajo la supervisión de un orquestador inteligente para transformar requisitos ambiguos en soluciones técnicas[cite: 44, 52].

[cite_start]Este trabajo representa una implementación práctica de los conceptos de **Ingeniería de Software Asistida por IA** y orquestación de grafos de estado[cite: 73, 286].

## 🚀 Características Principales

* [cite_start]**Procesamiento Multimodal:** Capacidad para analizar y extraer requisitos técnicos a partir de imágenes (bocetos, diagramas UML) y texto utilizando modelos avanzados como Gemini[cite: 110, 202].
* [cite_start]**Arquitectura Basada en Grafos:** Utiliza **LangGraph** para gestionar el flujo de estado y la toma de decisiones condicionales entre agentes[cite: 216, 286].
* [cite_start]**Roles Especializados:** Nueve agentes distintos con responsabilidades segregadas, incluyendo Supervisor, Planificador, Desarrolladores (Backend/Frontend) y Diseñadores UI/UX[cite: 302].
* [cite_start]**Mejora Continua (RAG + QA):** Incluye un ciclo de retroalimentación donde un agente Auditor utiliza **RAG (Retrieval-Augmented Generation)** para validar el código contra estándares de calidad y solicitar correcciones automáticas[cite: 296, 338].
* [cite_start]**Estrategia de Modelos Híbrida:** Combina modelos de alto razonamiento (Gemini 2.5 Pro) para generación compleja y modelos de baja latencia (Llama 3.3 vía Groq) para el control de flujo[cite: 279, 280, 281].

## 🛠️ Arquitectura del Sistema

[cite_start]El sistema sigue un patrón de **Orquestación Basada en Grafos** (Graph-Based Agent Orchestration), donde un Agente Supervisor evalúa el estado global y enruta la tarea al especialista adecuado[cite: 286, 290].

### Agentes Implementados

1.  [cite_start]**Supervisor (`supervisor_agent.py`):** Cerebro del sistema, decide el siguiente paso en el grafo basándose en el estado actual[cite: 304].
2.  [cite_start]**Conversacional (`conversational_agent.py`):** Interfaz con el usuario para clarificar requisitos y eliminar ambigüedades[cite: 309].
3.  [cite_start]**Analista Multimodal (`multimodal_analyzer_agent.py`):** Procesa inputs visuales y genera especificaciones técnicas[cite: 313].
4.  [cite_start]**Planificador (`planner.py`):** Descompone la solicitud en tareas técnicas (Frontend/Backend/DB)[cite: 317].
5.  [cite_start]**Diseñador UI/UX (`ui_ux_designer_agent.py`):** Crea guías de estilo y especificaciones de componentes[cite: 322].
6.  [cite_start]**Desarrollador Frontend (`frontend_developer.py`):** Genera código HTML/CSS/JS estructurado[cite: 330].
7.  [cite_start]**Desarrollador Backend (`backend_developer.py`):** Implementa lógica de servidor y APIs[cite: 326].
8.  [cite_start]**Arquitecto de Base de Datos (`database_architech_agent.py`):** Diseña esquemas SQL/NoSQL[cite: 334].
9.  [cite_start]**Auditor de Calidad (`quality_auditor.py`):** Revisa el código y aprueba o rechaza con feedback constructivo basado en normas RAG[cite: 337].

## 📋 Pre-requisitos

Antes de instalar, asegúrate de tener lo siguiente:

* **Python >3.10 or <3.13**
* **API Key de Google AI Studio** (Para acceder a modelos Gemini).
* **API Key de Groq** (Para acceder a modelos Llama de alta velocidad).

## ⚙️ Instalación y Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/sma-devteam.git](https://github.com/tu-usuario/sma-devteam.git)
    cd sma-devteam
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    El proyecto requiere librerías específicas de IA y WebSockets listadas en `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz del proyecto. Puedes usar `env.examples` como guía:
    ```env
    GOOGLE_API_KEY="tu_api_key_de_google"
    GROQ_API_KEY="tu_api_key_de_groq"
    GEMINI_MODEL="gemini-2.5-pro" # O la versión configurada en src/config.py
    ```

5.  **Base de Conocimiento (Opcional - RAG):**
    Para que el agente QA funcione correctamente, coloca tus documentos de estándares (PDFs) en la carpeta `knowledge_base/` (créala si no existe). El sistema indexará estos documentos automáticamente al iniciar.

## ▶️ Uso y Ejecución

### Iniciar el Servidor
[cite_start]El sistema utiliza **FastAPI** para el backend y WebSockets para la comunicación en tiempo real[cite: 276].

```bash
python main.py
*El servidor iniciará por defecto en `http://127.0.0.1:8000`.*

### Interacción
1.  Abre tu navegador web y ve a `http://127.0.0.1:8000`.
2.  Verás una interfaz de chat. Puedes:
    * Escribir una solicitud de software (ej: "Crea una Landing Page para una veterinaria").
    * Adjuntar una imagen, boceto o diagrama de tu diseño deseado para que el **Agente Analista Multimodal** lo interprete.
3.  El sistema procesará la solicitud, mostrando en tiempo real qué agente está trabajando (Supervisor -> Planificador -> Desarrolladores).
4.  El código generado se guardará automáticamente en la carpeta `outputs/`.

## 📂 Estructura del Proyecto

```text
sma-devteam/
├── embeddings_chroma/   # Base de datos vectorial persistente (ChromaDB) para el contexto RAG
├── knowledge_base/      # Carpeta para documentos PDF de normas y buenas prácticas (Fuente RAG)
├── outputs/             # Directorio donde los agentes guardan el código generado
├── src/
│   ├── agents/          # Lógica de los agentes (Supervisor, Backend, Frontend, QA, etc.)
│   ├── graph/           # Definición del grafo de estado y flujo de trabajo (LangGraph)
│   ├── tools/           # Herramientas (Extractor de código, Analizador de archivos, Guardado)
│   ├── config.py        # Gestión centralizada de configuración
│   ├── model.py         # Inicialización de modelos LLM (Gemini y Llama/Groq)
│   └── rag_retriever.py # Lógica de embeddings y recuperación de información
├── static/              # Frontend de la aplicación (HTML/CSS/JS)
├── main.py              # Punto de entrada del servidor FastAPI y gestión de WebSockets
├── requirements.txt     # Lista de dependencias de Python
└── .env                 # Variables de entorno (API Keys)

## 🧠 Tecnologías Clave

* **Lenguaje:** Python 3.10+.
* [cite_start]**Orquestación:** [LangGraph](https://langchain-ai.github.io/langgraph/) (Gestión de estado y grafos cíclicos para flujos complejos)[cite: 74, 307].
* **Modelos de Lenguaje (LLMs):**
    * [cite_start]**Google Gemini 2.5 Pro:** Utilizado para el razonamiento profundo, generación de código complejo y análisis multimodal (imágenes/video)[cite: 280].
    * [cite_start]**Llama 3.3 (vía Groq):** Utilizado para decisiones de enrutamiento de baja latencia y control de flujo[cite: 281].
* **Backend Web:** FastAPI (Manejo asíncrono de peticiones y WebSockets para comunicación en tiempo real).
* **Base de Datos Vectorial:** ChromaDB (Almacenamiento de embeddings para el sistema RAG y memoria de contexto).
* **Frontend:** JavaScript Vanilla (Módulos ES6) + WebSocket API.

## 📞 Contacto y Créditos

[cite_start]**Autor:** Damián Enrique Martínez Jaimes [cite: 2, 10]
[cite_start]**Institución:** Universidad de Pamplona, Colombia [cite: 3, 19]
[cite_start]**Facultad:** Facultad de Ingenierías y Arquitectura [cite: 4, 20]
[cite_start]**Programa:** Ingeniería de Sistemas [cite: 6, 22]
[cite_start]**Año:** 2025 [cite: 8, 24]

---
