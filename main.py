from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import List

app = FastAPI(title="Chatsito 💬")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Base de datos PostgreSQL con psycopg3 ---
DATABASE_URL = "postgresql+psycopg://postgres:Lunita48@db.yeheyhewslionqxzftji.supabase.co:5432/postgres"
engine = create_engine(DATABASE_URL, echo=False)

class Mensaje(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario: str
    texto: str

SQLModel.metadata.create_all(engine)

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
                await client.send_text(data)

    except:
        connected_clients.remove(websocket)
