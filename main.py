import os
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, create_engine, select
from typing import List

from models import Mensaje

app = FastAPI(title="Chatsito 💬")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Base de datos PostgreSQL ---
DATABASE_URL = os.getenv("DATABASE_URL")  # Leer de variable de entorno
if not DATABASE_URL:
    raise Exception("Variable de entorno DATABASE_URL no definida")

# Agregar sslmode=require para Supabase
if "sslmode" not in DATABASE_URL:
    if "?" in DATABASE_URL:
        DATABASE_URL += "&sslmode=require"
    else:
        DATABASE_URL += "?sslmode=require"

engine = create_engine(DATABASE_URL, echo=True)

# Crear tablas
SQLModel.metadata.create_all(engine)

# --- WebSocket ---
connected_clients: List[WebSocket] = []

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    # Enviar historial
    with Session(engine) as session:
        mensajes = session.exec(select(Mensaje)).all()
        for m in mensajes:
            await websocket.send_text(f"{m.usuario}: {m.texto}")

    try:
        while True:
            data = await websocket.receive_text()
            if ":" in data:
                usuario, texto = data.split(":", 1)
                with Session(engine) as session:
                    nuevo = Mensaje(usuario=usuario.strip(), texto=texto.strip())
                    session.add(nuevo)
                    session.commit()

            for client in connected_clients:
                if client.client_state.value == 1:  # solo enviar a clientes conectados
                    await client.send_text(data)

    except Exception:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
