# Sistema Multiagente de Soporte al Desarrollo de Software (SMA-DevTeam)

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-v0.3-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange)

## 📄 Descripción General

Este proyecto implementa un **Sistema Multiagente (SMA)** diseñado para automatizar y asistir en las fases iniciales del desarrollo de software. El sistema es capaz de interpretar especificaciones **multimodales** (texto, diagramas, imágenes, bocetos) para generar artefactos de software estructurados, planes de desarrollo y código fuente funcional.

La arquitectura emula un equipo de desarrollo humano, donde agentes autónomos especializados (Analistas, Arquitectos, Desarrolladores y Auditores QA) colaboran bajo la supervisión de un orquestador inteligente para transformar requisitos ambiguos en soluciones técnicas.

Este trabajo representa una implementación práctica de los conceptos de **Ingeniería de Software Asistida por IA** y orquestación de grafos de estado.

## 🚀 Características Principales

* **Procesamiento Multimodal:** Capacidad para analizar y extraer requisitos técnicos a partir de imágenes (bocetos, diagramas UML) y texto utilizando modelos avanzados como Gemini.
* **Arquitectura Basada en Grafos:** Utiliza **LangGraph** para gestionar el flujo de estado y la toma de decisiones condicionales entre agentes.
* **Roles Especializados:** Nueve agentes distintos con responsabilidades segregadas, incluyendo Supervisor, Planificador, Desarrolladores (Backend/Frontend) y Diseñadores UI/UX.
* **Mejora Continua (RAG + QA):** Incluye un ciclo de retroalimentación donde un agente Auditor utiliza **RAG (Retrieval-Augmented Generation)** para validar el código contra estándares de calidad y solicitar correcciones automáticas.
* **Estrategia de Modelos Híbrida:** Combina modelos de alto razonamiento (Gemini 2.5 Pro) para generación compleja y modelos de baja latencia (Llama 3.3 vía Groq) para el control de flujo.

## 🛠️ Arquitectura del Sistema

El sistema sigue un patrón de **Orquestación Basada en Grafos** (Graph-Based Agent Orchestration), donde un Agente Supervisor evalúa el estado global y enruta la tarea al especialista adecuado.

### Arquitectura General del Sistema Agéntico

![Arquitectura del Sistema](Images/Arquitectura%20Sistema%20Agentico.png)

El diagrama muestra la arquitectura completa del sistema multiagente, donde:
- **Solicitud del Usuario:** Puede incluir texto, imágenes, audio, documentos o videos
- **Supervisor:** Agente central que coordina el flujo de trabajo y toma decisiones de enrutamiento
- **Estado Compartido:** Memoria común accesible por todos los agentes para mantener contexto
- **Agentes Especializados:** Cada uno con herramientas específicas (Conversacional, Multimodal, UI/UX Designer, Planner, Frontend/Backend/Database Developers)
- **Quality Auditor:** Valida el código generado usando RAG (Retrieval-Augmented Generation)
- **Guardado Local:** Almacenamiento persistente del código aprobado

### Diagrama del Grafo MultiAgente

![Diagrama del Grafo](Images/Diagrama%20del%20Grafo%20MultiAgente.png)

Este diagrama ilustra el flujo completo del sistema en tres fases principales:

#### **Fase 1: Análisis y Planificación**
![Fase 1](Images/Fase%201.png)

1. El **Supervisor** recibe la solicitud del usuario
2. **Decisión:** Si hay archivos adjuntos (imágenes, documentos), se enruta al **Multimodal Analyzer** o **UI/UX Designer**
3. Si no hay archivos adjuntos, se procede con el **Planner** y **Conversational Agent**
4. Los agentes actualizan el estado compartido y retornan al Supervisor
5. El Supervisor decide la siguiente fase

#### **Fase 2: Desarrollo**
![Fase 2](Images/Fase%202.png)

1. El **Supervisor** enruta a los agentes de desarrollo según el plan:
   - **Frontend Developer:** Genera HTML, CSS, JavaScript
   - **Backend Developer:** Implementa APIs y lógica de servidor
   - **Database Architect:** Diseña esquemas de base de datos
2. Cada desarrollador guarda su código localmente
3. El código generado regresa al Supervisor para validación

#### **Fase 3: Validación y Refinamiento**
![Fase 3](Images/Fase%203.png)

1. El **Quality Auditor** lee el código guardado
2. Utiliza **RAG** para verificar la calidad del código contra estándares
3. **Decisión:**
   - ✅ **Código Aprobado:** El Supervisor finaliza el proceso
   - ❌ **Código No Aprobado:** Retroalimenta a los Developer Agents (Fase 2)
4. Los desarrolladores corrigen el código según el feedback
5. El ciclo continúa hasta que el código sea aprobado

### Agentes Implementados

1.  **Supervisor (`supervisor_agent.py`):** Cerebro del sistema, decide el siguiente paso en el grafo basándose en el estado actual.
2.  **Conversacional (`conversational_agent.py`):** Interfaz con el usuario para clarificar requisitos y eliminar ambigüedades.
3.  **Analista Multimodal (`multimodal_analyzer_agent.py`):** Procesa inputs visuales y genera especificaciones técnicas.
4.  **Planificador (`planner.py`):** Descompone la solicitud en tareas técnicas (Frontend/Backend/DB).
5.  **Diseñador UI/UX (`ui_ux_designer_agent.py`):** Crea guías de estilo y especificaciones de componentes.
6.  **Desarrollador Frontend (`frontend_developer.py`):** Genera código HTML/CSS/JS estructurado.
7.  **Desarrollador Backend (`backend_developer.py`):** Implementa lógica de servidor y APIs.
8.  **Arquitecto de Base de Datos (`database_architech_agent.py`):** Diseña esquemas SQL/NoSQL.
9.  **Auditor de Calidad (`quality_auditor.py`):** Revisa el código y aprueba o rechaza con feedback constructivo basado en normas RAG.

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
    CEREBRAS_API_KEY="your_cerebras_api_key"
    COHERE_API_KEY="your_cohere_api_key"
    ```
    Configura tus modelos de IA en src/model.py
5.  **Base de Conocimiento (Opcional - RAG):**
    Para que el agente QA funcione correctamente, coloca tus documentos de estándares (PDFs) en la carpeta `knowledge_base/` (créala si no existe). El sistema indexará estos documentos automáticamente al iniciar.

## ▶️ Uso y Ejecución

### Iniciar el Servidor
El sistema utiliza **FastAPI** para el backend y WebSockets para la comunicación en tiempo real.

```bash
python main.py
*El servidor iniciará por defecto en `http://127.0.0.1:8000`.*
```

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
```

## 🧠 Tecnologías Clave

* **Lenguaje:** Python 3.10+.
* **Orquestación:** [LangGraph](https://langchain-ai.github.io/langgraph/) (Gestión de estado y grafos cíclicos para flujos complejos).
* **Modelos de Lenguaje (LLMs):**
    * **Google Gemini 2.5 Pro:** Utilizado para el razonamiento profundo, generación de código complejo y análisis multimodal (imágenes/video).
    * **Llama 3.3 (vía Groq):** Utilizado para decisiones de enrutamiento de baja latencia y control de flujo.
* **Backend Web:** FastAPI (Manejo asíncrono de peticiones y WebSockets para comunicación en tiempo real).
* **Base de Datos Vectorial:** ChromaDB (Almacenamiento de embeddings para el sistema RAG y memoria de contexto).
* **Frontend:** JavaScript Vanilla (Módulos ES6) + WebSocket API.

## 📞 Contacto y Créditos

**Autor:** Damián Enrique Martínez Jaimes
**Institución:** Universidad de Pamplona, Colombia
**Facultad:** Facultad de Ingenierías y Arquitectura
**Programa:** Ingeniería de Sistemas
**Año:** 2025

---
