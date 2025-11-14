from sqlmodel import SQLModel, Field
from datetime import datetime

class Mensaje(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario: str
    texto: str
    fecha: datetime = Field(default_factory=datetime.utcnow)
    
    """
    Modelo Mensaje:
    - Representa una fila en la tabla 'mensaje' en la base de datos.
    - Usamos nombres simples: usuario, texto y fecha.
    - Field(default_factory=...) crea la fecha automáticamente al insertar.
    """