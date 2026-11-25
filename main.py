from fastapi import FastAPI
from google import genai
from fastapi.middleware.cors import CORSMiddleware

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Modelos y conexión a la base de datos
# ---------------------------------------------------------------------------

class Mensaje(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    rol: str
    texto: str
    fecha: str
    conversacion_id: int | None = Field(default=None, foreign_key="conversacion.id")


class Conversacion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre_conversacion: str = "Nueva Conversación"
    # mensajes: list[Mensaje] = Relationship(back_populates="conversacion")

sqlite_file_name = "chatbot.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


# ---------------------------------------------------------------------------
# Creación de tablas y sesión por petición
# ---------------------------------------------------------------------------

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# ---------------------------------------------------------------------------
# Aplicación
# ---------------------------------------------------------------------------

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Configurar el middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Permite todos los orígenes
    allow_credentials=False,   # ¡Ojo! Debe ser False si usas "*"
    allow_methods=["*"],      # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],      # Permite todos los encabezados
)


client = genai.Client()


# ---------------------------------------------------------------------------
# Endpoints principales (recorrido de la exposición)
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/conversaciones/")
def listar_conversaciones(session: SessionDep) -> list[Conversacion]:
    return session.exec(select(Conversacion).order_by(Conversacion.id)).all()


@app.post("/conversaciones/")
def crear_conversacion(conversacion: Conversacion, session: SessionDep):
    nombre = conversacion.nombre_conversacion or "Nueva Conversación"
    nueva = Conversacion(nombre_conversacion=nombre)
    session.add(nueva)
    session.commit()
    session.refresh(nueva)
    return nueva


class MensajeEntrada(SQLModel):
    texto: str
    conversacion_id: int


@app.post("/chat/")
def llamar_ia(mensaje: MensajeEntrada, session: SessionDep):
    # la conversación debe existir para poder guardar y consultar su contexto
    conversacion = session.get(Conversacion, mensaje.conversacion_id)
    if not conversacion:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    # historial SOLO de la conversación actual: el agente no ve otras conversaciones
    historial = session.exec(
        select(Mensaje)
        .where(Mensaje.conversacion_id == mensaje.conversacion_id)
        .order_by(Mensaje.id)
    ).all()
    entrada = [
        {
            "type": "user_input" if m.rol == "usuario" else "model_output",
            "content": [{"type": "text", "text": m.texto}],
        }
        for m in historial
    ]

    # en esta linea deberíamos guardar el mensaje que llega del humano
    time_user = datetime.now(timezone.utc).isoformat()
    pregunta = Mensaje(rol="usuario", texto=mensaje.texto, fecha=time_user, conversacion_id=mensaje.conversacion_id)
    session.add(pregunta)

    entrada.append(
        {"type": "user_input", "content": [{"type": "text", "text": mensaje.texto}]}
    )

    inferencia = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=entrada
    )
    time_bot = datetime.now(timezone.utc).isoformat()
    respuesta = Mensaje(rol="bot", texto=inferencia.output_text, fecha=time_bot, conversacion_id=mensaje.conversacion_id)
    session.add(respuesta)

    # En esta linea guardamos el mensaje de la IA
    session.commit()
    session.refresh(respuesta)
    return {"Respuesta": inferencia.output_text }


@app.get("/conversaciones/{conversacion_id}/mensajes/")
def mensajes_conversacion(conversacion_id: int, session: SessionDep):
    return session.exec(
        select(Mensaje).where(Mensaje.conversacion_id == conversacion_id)
    ).all()


# va a ser necesario definir un endpoint GET que me permita obtener TODOS los mensajes
@app.get("/mensajes/")
def leer_mensajes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Mensaje]:
    mensajes = session.exec(select(Mensaje).offset(offset).limit(limit)).all()
    return mensajes


# ---------------------------------------------------------------------------
# Material de respaldo: endpoints adicionales de la interfaz
# (no forman parte del recorrido principal de la exposición)
# ---------------------------------------------------------------------------

class ConversacionActualizacion(SQLModel):
    nombre_conversacion: str
    conversacion_id: int


@app.patch("/conversaciones/")
def renombrar_conversacion(conversacion_name: ConversacionActualizacion, session: SessionDep):
    conversacion_db = session.get(Conversacion, conversacion_name.conversacion_id)
    if not conversacion_db:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    conversacion = Conversacion(id=conversacion_name.conversacion_id, nombre_conversacion=conversacion_name.nombre_conversacion)
    conversacion_data = conversacion.model_dump(exclude_unset=True)
    conversacion_db.sqlmodel_update(conversacion_data)
    session.add(conversacion_db)
    session.commit()
    session.refresh(conversacion_db)
    return conversacion_db


@app.delete("/conversaciones/{conversacion_id}")
def eliminar_conversacion(conversacion_id: int, session: SessionDep):
    conversacion = session.get(Conversacion, conversacion_id)
    if not conversacion:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    # Primero se eliminan los mensajes para no dejar registros huérfanos.
    mensajes = session.exec(
        select(Mensaje).where(Mensaje.conversacion_id == conversacion_id)
    ).all()
    for mensaje in mensajes:
        session.delete(mensaje)

    session.delete(conversacion)
    session.commit()
    return {"detail": "Conversación eliminada", "id": conversacion_id}
