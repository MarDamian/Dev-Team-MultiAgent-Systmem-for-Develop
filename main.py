# Contenido para: main.py

import uvicorn
import uuid
import os
import shutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from src.graph.workflow import build_graph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        with open(file_path, "wb", buffering=0) as buffer:
            shutil.copyfileobj(file.file, buffer)
        filenames.append(file.filename)
    return JSONResponse(content={"filenames": filenames})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Nuevo cliente conectado. Las sesiones se crearán por tarea.")

    async with AsyncSqliteSaver.from_conn_string(":memory:") as memory:
        langgraph_app = build_graph(checkpointer=memory)
        
        try:
            while True:
                data = await websocket.receive_json()
                print(f"Mensaje recibido del cliente: {data}")
                
                thread_id = str(uuid.uuid4())
                config = {"configurable": {"thread_id": thread_id}}
                print(f"Iniciando nueva tarea con sesión: {thread_id}")

                user_input = data.get("user_input")
                file_names = data.get("file_names", [])
                
                # <-- CAMBIO CLAVE: Recibimos el historial conversacional del frontend
                chat_history = data.get("chat_history", [])

                if not user_input and not file_names:
                    continue

                file_paths = [os.path.join("uploads", f) for f in file_names]
                
                # <-- CAMBIO CLAVE: Inyectamos el historial en el estado inicial de la nueva tarea
                inputs = {
                    "user_input": user_input,
                    "supervisor_iterations": 0,
                    "file_paths": file_paths,
                    "chat_history": chat_history 
                }

                print(f"Invocando el grafo con la entrada (con historial): {inputs}")
                
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

if __name__ == "__main__":
    if not os.path.exists("uploads"): os.makedirs("uploads")
    if not os.path.exists("outputs"): os.makedirs("outputs")
    uvicorn.run(app, host="127.0.0.1", port=8000)