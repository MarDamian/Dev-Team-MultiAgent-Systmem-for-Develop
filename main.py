# Contenido para: main.py

import uvicorn
import uuid
import os
import shutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form # Importar Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Importar nuestras funciones y configuración de LangGraph
import src.config 
from src.graph.workflow import build_graph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# --- Configuración de la App FastAPI ---
app = FastAPI()

# Montar la carpeta 'static' para que el navegador pueda acceder a index.html, css, js
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Funciones de Utilidad ---
def save_code_to_file(filename: str, code: str | None):
    """Guarda el código generado en un archivo si no es None."""
    if not code:
        return
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"-> Código guardado en '{filename}'")
    except Exception as e:
        print(f"Error guardando el archivo {filename}: {e}")

# --- Endpoints de la API ---

@app.get("/")
async def get_root():
    """Sirve el archivo principal del frontend (index.html)."""
    return FileResponse("static/index.html")

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    """Recibe archivos del frontend, los guarda en la carpeta 'uploads' y devuelve sus nombres.
       Este endpoint ahora solo se usa para la subida inicial de archivos si fuera necesario por separado."""
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    
    filenames = []
    for file in files:
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        filenames.append(file.filename)
        print(f"Archivo guardado: {file.filename}")
        
    return JSONResponse(content={"filenames": filenames}, status_code=200)

@app.post("/submit-message-with-files")
async def submit_message_with_files(user_input: str = Form(""), files: list[UploadFile] = File([])):
    """
    Recibe el mensaje de usuario y los archivos adjuntos en una sola solicitud HTTP POST,
    procesa la entrada con el grafo y devuelve la respuesta final.
    """
    print(f"Mensaje y archivos recibidos del cliente (HTTP POST): {user_input}, {len(files)} archivos")

    # Guardar archivos subidos
    file_names = []
    file_paths = []
    if files:
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
        for file in files:
            file_path = os.path.join("uploads", file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_names.append(file.filename)
            file_paths.append(file_path)
            print(f"Archivo guardado: {file.filename}")

    # Invocar el grafo con la entrada
    # Cada invocación HTTP obtiene su propio checkpointer y su propia instancia del grafo.
    async with AsyncSqliteSaver.from_conn_string(":memory:") as memory:
        langgraph_app = build_graph(checkpointer=memory)
        # Cada sesión obtiene un thread_id único para mantener su propia memoria.
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        inputs = {"user_input": user_input, "file_paths": file_paths}
        print(f"Invocando el grafo con la entrada (HTTP): {inputs}")

        final_response_content = ""
        # Usamos astream para procesar y recolectar la respuesta final
        async for event in langgraph_app.astream(inputs, config=config):
            if event:
                # Asumiendo que la 'final_response' es lo que queremos devolver al frontend
                node_name = list(event.keys())[0]
                if node_name and event[node_name].get("final_response"):
                    final_response_content = event[node_name]["final_response"]
        
        # Limpiar los archivos temporales después de procesar
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)
        print(f"Archivos de la tarea limpiados (HTTP): {file_names}")

        if final_response_content:
            return JSONResponse(content={"final_response": final_response_content}, status_code=200)
        else:
            return JSONResponse(content={"error": "No se recibió una respuesta final del grafo."}, status_code=500)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Maneja la conexión WebSocket para una sesión de chat y desarrollo."""
    await websocket.accept()
    print("Nuevo cliente conectado. Creando sesión de grafo aislada.")

    # Cada conexión de WebSocket obtiene su propio checkpointer y su propia instancia del grafo.
    # Esto es CRUCIAL para prevenir la contaminación de estado entre usuarios o sesiones.
    async with AsyncSqliteSaver.from_conn_string(":memory:") as memory:
        langgraph_app = build_graph(checkpointer=memory)
        
        # Cada sesión de chat obtiene un thread_id único para mantener su propia memoria.
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Bucle para escuchar mensajes del cliente mientras la conexión esté abierta.
            while True:
                data = await websocket.receive_json()
                print(f"Mensaje recibido del cliente: {data}")
                
                user_input = data.get("user_input")
                # El frontend ahora nos dice explícitamente qué archivos usar.
                file_names = data.get("file_names", []) 
                
                if not user_input:
                    continue

                file_paths = [os.path.join("uploads", f) for f in file_names]
                inputs = {"user_input": user_input, "file_paths": file_paths}

                print(f"Invocando el grafo con la entrada: {inputs}")
                
                # Usamos astream y enviamos los eventos al cliente en tiempo real.
                async for event in langgraph_app.astream(inputs, config=config):
                    if event:
                        await websocket.send_json(event)
                
                # Limpiar solo los archivos que se usaron en esta tarea.
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                print(f"Archivos de la tarea limpiados: {file_names}")

                # Enviar un mensaje especial para indicar que el turno ha terminado.
                await websocket.send_json({"type": "done"})

        except WebSocketDisconnect:
            print(f"Cliente desconectado.")
        except Exception as e:
            print(f"Error fatal en el WebSocket: {e}")
            await websocket.send_json({"error": str(e)})

# --- Punto de Entrada para Ejecutar el Servidor ---
if __name__ == "__main__":
    # Crear directorios necesarios al iniciar.
    if not os.path.exists("uploads"): os.makedirs("uploads")
    if not os.path.exists("outputs"): os.makedirs("outputs")

    print("Iniciando servidor FastAPI en http://127.0.0.1:8000")
    # Uvicorn es el servidor ASGI que ejecuta nuestra aplicación FastAPI.
    uvicorn.run(app, host="127.0.0.1", port=8000)
