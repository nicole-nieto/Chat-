from sqlmodel import SQLModel, Field
from datetime import datetime

class Mensaje(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario: str
    texto: str
    fecha: datetime = Field(default_factory=datetime.utcnow)
