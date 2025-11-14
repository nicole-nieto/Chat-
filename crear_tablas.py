from sqlmodel import SQLModel, create_engine
from models import Mensaje

DATABASE_URL = "postgresql://postgres:tu_contraseña@localhost:5432/tu_db"

engine = create_engine(DATABASE_URL)

print(" Creando tablas...")
SQLModel.metadata.create_all(engine)
print(" Tablas listas.")
