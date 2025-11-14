import os
from sqlmodel import SQLModel, create_engine
from models import Mensaje

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("Variable de entorno DATABASE_URL no definida")

# sslmode requerido para Supabase
if "sslmode" not in DATABASE_URL:
    if "?" in DATABASE_URL:
        DATABASE_URL += "&sslmode=require"
    else:
        DATABASE_URL += "?sslmode=require"

engine = create_engine(DATABASE_URL, echo=True)
SQLModel.metadata.create_all(engine)
print("Tablas creadas correctamente")
