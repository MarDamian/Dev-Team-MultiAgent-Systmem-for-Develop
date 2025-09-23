# Contenido para: main.py

import uvicorn
import uuid
import os
import shutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from src.graph.workflow import build_graph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# --- Configuración de la App FastAPI ---
app = FastAPI()

# Montar la carpeta 'static'
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Endpoints de la API ---

@app.get("/")
async def get_root():
    return FileResponse("static/index.html")

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    
    filenames = []
    for file in files:
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb", buffering=0) as buffer: # buffering=0 para asegurar escritura inmediata
            shutil.copyfileobj(file.file, buffer)
        filenames.append(file.filename)
        print(f"Archivo guardado: {file.filename}")
        
    return JSONResponse(content={"filenames": filenames}, status_code=200)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Nuevo cliente conectado. Las sesiones se crearán por tarea.")

    # El checkpointer se mantiene vivo durante toda la conexión del WebSocket.
    async with AsyncSqliteSaver.from_conn_string(":memory:") as memory:
        # El grafo se construye una vez por conexión, usando el mismo checkpointer.
        langgraph_app = build_graph(checkpointer=memory)
        
        try:
            while True:
                data = await websocket.receive_json()
                print(f"Mensaje recibido del cliente: {data}")
                
                # --- LÓGICA DE SESIÓN POR TAREA ---
                # ¡CAMBIO CLAVE! Se genera un nuevo thread_id para CADA nueva tarea del usuario.
                # Esto asegura que el estado `task_complete` de una tarea no afecte a la siguiente.
                thread_id = str(uuid.uuid4())
                config = {"configurable": {"thread_id": thread_id}}
                print(f"Iniciando nueva tarea con sesión: {thread_id}")

                user_input = data.get("user_input")
                file_names = data.get("file_names", []) 
                
                if not user_input and not file_names:
                    continue

                file_paths = [os.path.join("uploads", f) for f in file_names]
                inputs = {"user_input": user_input, "file_paths": file_paths}

                print(f"Invocando el grafo con la entrada: {inputs}")
                
                async for event in langgraph_app.astream(inputs, config=config):
                    if event:
                        await websocket.send_json(event)
                
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                print(f"Archivos de la tarea limpiados: {file_names}")

                await websocket.send_json({"type": "done"})

        except WebSocketDisconnect:
            print(f"Cliente desconectado.")
        except Exception as e:
            print(f"Error fatal en el WebSocket: {e}")
            await websocket.send_json({"error": str(e)})

# --- Punto de Entrada para Ejecutar el Servidor ---
if __name__ == "__main__":
    if not os.path.exists("uploads"): os.makedirs("uploads")
    if not os.path.exists("outputs"): os.makedirs("outputs")

    print("Iniciando servidor FastAPI en http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)