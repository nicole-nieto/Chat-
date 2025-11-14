from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, create_engine, Session, select
from typing import List
import os
from models import Mensaje 

app = FastAPI(title="Chatsito 💬")
# --- Archivos estáticos y templates ---
# FastAPI servirá: /static/* y las plantillas en /templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Configuración de la DB desde variable de entorno ---
#  (Environment > Variables).
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL no está definida")

# Agregar sslmode=require si no está presente
if "sslmode" not in DATABASE_URL:
    if "?" in DATABASE_URL:
        DATABASE_URL += "&sslmode=require"
    else:
        DATABASE_URL += "?sslmode=require"

# Creamos el engine (no hace la creación de tablas aún)
engine = create_engine(DATABASE_URL, echo=False)

# --- Crear tablas al iniciar la aplicación (solo una vez por arranque) ---
# Esto asegura que, cuando la app arranque en Render, la tabla Mensaje exista.
@app.on_event("startup")
def on_startup():
    # Crea las tablas que no existan, no modifica tablas ya existentes.
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

# --- WebSocket management ---
# Lista de websockets conectados. Guardamos objetos WebSocket para reenviar mensajes.
connected_clients: List[WebSocket] = []

# Ruta principal que sirve el HTML (usa Jinja2Templates)
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    - Acepta la conexión WebSocket.
    - Envia el historial de mensajes almacenado en DB.
    - Recibe mensajes nuevos y los guarda en DB, luego los reenvía a todos.
    """
    await websocket.accept()
    connected_clients.append(websocket)

    # cargar historial, Enviar historial al nuevo cliente (si hay mensajes en DB)
    with Session(engine) as session:
        mensajes = session.exec(select(Mensaje)).all()
        # Enviamos en el formato "usuario: texto" para que el frontend solo muestre.
        for m in mensajes:
            await websocket.send_text(f"{m.usuario}: {m.texto}")

    try:
        # Bucle de lectura de mensajes del cliente
        while True:
            data = await websocket.receive_text()

            if ":" in data:
                usuario, texto = data.split(":", 1)
                with Session(engine) as session:
                    nuevo = Mensaje(usuario=usuario.strip(), texto=texto.strip())
                    session.add(nuevo)
                    session.commit()
        # Reenviar a todos los clientes conectados
            for client in connected_clients:
                await client.send_text(data)
                # Si el envío falla, lo ignoramos aquí; la excepción principal se maneja abajo.

    except:
        connected_clients.remove(websocket)
 # Si el socket cierra o hay error, lo removemos de la lista para no enviarle más.