import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema.vectorstore import VectorStoreRetriever


model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': True} # La normalización es una buena práctica

print(f"Inicializando embeddings con el modelo multilingüe: {model_name}")
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# --- CONFIGURACIÓN DE CHROMA Y RETRIEVER ---
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Cambiamos el nombre del directorio para no mezclar embeddings de modelos distintos
persist_directory = "embeddings_chroma"

vectorstore: Chroma | None = None
retriever: VectorStoreRetriever | None = None

def initialize_rag():
    """
    Inicializa el sistema RAG. Carga o crea la base de datos vectorial.
    """
    global vectorstore, retriever
    
    knowledge_base_dir = "knowledge_base"
    
    try:
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            print(f"Cargando base de datos de vectores existente desde: {persist_directory}")
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            print(f"Creando nueva base de datos de vectores en: {persist_directory}")
            if not os.path.exists(knowledge_base_dir):
                print(f"Error: Directorio de base de conocimientos no encontrado: {knowledge_base_dir}")
                return

            documents = []
            pdf_files = [f for f in os.listdir(knowledge_base_dir) if f.endswith(".pdf")]
            
            if not pdf_files:
                print("No se encontraron archivos PDF en la base de conocimientos.")
                return

            print(f"Encontrados {len(pdf_files)} PDF(s) para procesar...")
            for filename in pdf_files:
                file_path = os.path.join(knowledge_base_dir, filename)
                print(f"Cargando y procesando: {filename}")
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())

            print("Dividiendo documentos en chunks...")
            splits = text_splitter.split_documents(documents)
            
            print(f"Creando embeddings para {len(splits)} chunks y guardando en la base de datos...")
            vectorstore = Chroma.from_documents(
                documents=splits, 
                embedding=embeddings,
                persist_directory=persist_directory
            )
            print("Base de datos de vectores creada y guardada con éxito.")

        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={'k': 4, 'fetch_k': 20}
        )
        
        print("--- RAG inicializado con éxito ---")

    except Exception as e:
        print(f"Ocurrió un error durante la inicialización de RAG: {e}")

# (Las funciones retrieve_context e initialize_rag() se mantienen igual)
def retrieve_context(query: str) -> str:
    if not retriever:
        print("Error: El sistema RAG no ha sido inicializado. Llamando a initialize_rag() ahora.")
        initialize_rag()
        if not retriever:
            print("Error fatal: No se pudo inicializar el sistema RAG.")
            return "Error: El sistema de recuperación de información no está disponible."
    print(f"Recuperando contexto para la consulta: '{query[:80]}...'")
    retrieved_docs = retriever.invoke(query)
    if not retrieved_docs:
        print("No se encontraron documentos relevantes.")
        return "No se encontró información relevante en la base de conocimientos."
    context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    print(f"Contexto recuperado exitosamente ({len(retrieved_docs)} chunks).")
    return context

initialize_rag()