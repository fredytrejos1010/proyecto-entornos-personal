from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, timezone


class Mensaje(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    rol: str
    texto: str
    fecha: str


sqlite_file_name = "chatbot.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

# Code above omitted 👆

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Endpoint de creación de mensajes
@app.post("/mensajes/")
def crear_mensaje(mensaje: Mensaje, session: SessionDep) -> Mensaje:
    session.add(mensaje)
    session.commit()
    session.refresh(mensaje)
    return mensaje

# Code above omitted 👆

@app.get("/mensajes/")
def leer_mensajes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Mensaje]:
    mensajes = session.exec(select(Mensaje).offset(offset).limit(limit)).all()
    return mensajes

# Code below omitted 👇





