from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, create_engine, Session, select
from typing import List
import os

from models import Mensaje   # <-- Import correcto

app = FastAPI(title="Chatsito 💬")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Tomar la URL desde Render ---
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL no está definida")

# Agregar sslmode=require si no está presente
if "sslmode" not in DATABASE_URL:
    if "?" in DATABASE_URL:
        DATABASE_URL += "&sslmode=require"
    else:
        DATABASE_URL += "?sslmode=require"

engine = create_engine(DATABASE_URL, echo=False)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


connected_clients: List[WebSocket] = []


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    # cargar historial
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
                await client.send_text(data)

    except:
        connected_clients.remove(websocket)
