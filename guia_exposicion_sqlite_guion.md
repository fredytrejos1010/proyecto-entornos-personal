# Guion literal de exposición: Conexión y sesiones con SQLite en FastAPI

**Archivo base:** `guia_exposicion_sqlite.md`
**Proyecto:** chatbot del curso (`main.py`, `index.html`)
**Duración:** 15 minutos
**Público:** estudiantes del curso, con el profesor supervisando
**Formato:** Guillermo explica el concepto y Jhon muestra el código y la demo

> Roles asignados: **Guillermo** explica el concepto y **Jhon** muestra el código y la demo.

---

## 0. Reglas para los dos expositores

1. Hablarle al salón, no al profesor ni a la pantalla.
2. No leer las diapositivas palabra por palabra: usarlas como apoyo.
3. Explicar los términos técnicos la primera vez que aparecen.
4. Hablar despacio y hacer pausas después de cada idea importante.
5. Si el profesor pide un cambio en vivo, **primero decir en voz alta qué se va a hacer y por qué**, y después escribirlo.
6. No modificar archivos que no sean `main.py` durante la exposición.
7. Antes de empezar, tener el servidor y la base de datos listos. No improvisar la instalación frente al salón.
8. Si algo falla, usar el plan B sin disculparse demasiado: explicar qué falló y continuar.

---

## 1. Antes de comenzar (checklist silencioso)

Jhon verifica:

- [ ] Entorno virtual activado.
- [ ] `GEMINI_API_KEY` exportada antes de arrancar el servidor.
- [ ] Servidor corriendo con `uvicorn main:app --reload --port 8000`.
- [ ] `http://localhost:8000/docs` abre correctamente.
- [ ] `chatbot.db` existe o se crea al arrancar.
- [ ] Hay al menos dos mensajes de prueba en la base.
- [ ] `index.html` abierto o listo para abrir.
- [ ] Terminal aparte para `sqlite3 chatbot.db`.
- [ ] Este guion visible solo para los expositores.

Guillermo verifica:

- [ ] Diapositivas abiertas en la primera slide.
- [ ] Cronómetro o reloj visible.
- [ ] Pregunta final elegida.
- [ ] Cambio en vivo elegido y practicado.

---

## 2. Reparto y cronómetro

| Tiempo | Quién | Qué hace |
|---|---|---|
| 0:00–0:50 | Guillermo | Saludo, tema y gancho. |
| 0:50–1:30 | Guillermo | Problema: sin base de datos no hay memoria. |
| 1:30–3:10 | Guillermo | SQLite, SQLModel y `engine`. |
| 3:10–5:10 | Guillermo | `Session`, `Depends`, `yield` y arranque. |
| 5:10–5:40 | Guillermo | Transición a Jhon. |
| 5:40–7:10 | Jhon | Modelo, conexión y creación de tablas. |
| 7:10–8:20 | Jhon | `get_session` y `SessionDep`. |
| 8:20–10:20 | Jhon | `POST /chat/` y el manejo del historial. |
| 10:20–11:20 | Jhon | `GET /mensajes/` y conexión con el frontend. |
| 11:20–14:10 | Jhon | Demo en vivo con `/docs`, `curl` y SQLite. |
| 14:10–15:00 | Guillermo | Cierre y pregunta para el salón. |

Si el tiempo se atrasa:

- Acortar la demo a `GET /health`, `POST /chat/` y `GET /mensajes/`.
- No omitir la pregunta final ni la idea central.

---

# 3. Guion literal

## 3.1. Apertura — Guillermo (0:00–0:50)

> [Guillermo se ubica al frente, mira al salón y comienza.]
>
> "Buenos días. Somos Guillermo y Jhon. Hoy les vamos a hablar de un tema que está detrás de casi cualquier aplicación con usuarios: **cómo FastAPI se conecta a una base de datos SQLite y cómo maneja las sesiones**."
>
> "Lo vamos a explicar con nuestro propio proyecto: un chatbot construido con FastAPI que recibe preguntas, responde usando Gemini y guarda toda la conversación en una base de datos."
>
> "La idea es que al final entiendan tres cosas: cómo se abre la conexión, cómo se usa una sesión y por qué cada petición debería tener la suya."

---

## 3.2. El problema — Guillermo (0:50–1:30)

> "Imaginen que el chatbot responde bien, pero cada vez que recargan la página se borra todo. El usuario tendría que empezar de cero una y otra vez."
>
> "Eso pasa si la información vive solo en la memoria del servidor o en el navegador."
>
> "Para que la conversación exista después de recargar, necesitamos guardarla en un lugar permanente. Ahí entra SQLite."

[SEÑALAR la diapositiva del problema: "sin base de datos vs. con base de datos".]

> "En nuestro proyecto, el frontend le pide el historial a FastAPI, y FastAPI se lo pide a la base de datos. El navegador nunca habla directamente con SQLite."

---

## 3.3. ¿Qué es SQLite? — Guillermo (1:30–2:10)

> "SQLite es una base de datos relacional que vive dentro de **un solo archivo**. En nuestro caso, el archivo se llama `chatbot.db`."
>
> "No necesitamos instalar un servidor de base de datos aparte, como sí pasaría con PostgreSQL o MySQL. Por eso es ideal para proyectos pequeños, prácticas y demos."
>
> "Y algo importante: el archivo se puede abrir, consultar y copiar como cualquier otro archivo."

[SEÑALAR la diapositiva de arquitectura.]

> "Nuestra arquitectura queda así: el navegador habla por HTTP con FastAPI, FastAPI usa SQLModel para hablar con SQLite, y SQLite guarda todo en `chatbot.db`."

---

## 3.4. ¿Qué es SQLModel y qué es el engine? — Guillermo (2:10–3:10)

> "Para no escribir SQL a mano en todo el proyecto usamos **SQLModel**. SQLModel combina dos ideas: por un lado, valida los datos como Pydantic; por el otro, mapea clases a tablas como SQLAlchemy."
>
> "En el código tenemos una clase llamada `Mensaje`. Esa clase no es solo una clase normal: **es la representación de una tabla**."
>
> "Sus campos son `id`, `rol`, `texto` y `fecha`. Cada fila de la tabla será un mensaje de la conversación."

[SEÑALAR la diapositiva con el código del modelo.]

> "Ahora, la conexión. En `main.py` aparece esto:"

```python
sqlite_file_name = "chatbot.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
```

> "El **engine** es el objeto que sabe cómo conectarse a la base de datos. Se crea una sola vez, cuando arranca la aplicación."
>
> "La URL `sqlite:///chatbot.db` significa: usa SQLite y abre el archivo `chatbot.db` que está en la carpeta del proyecto. Las tres barras indican una ruta relativa."
>
> "Y `check_same_thread=False` está ahí porque FastAPI puede atender una petición en un hilo distinto al que creó la conexión. SQLite por defecto bloquea eso. Lo desactivamos porque cada petición va a usar su propia sesión."

> [PAUSA breve.]
>
> "Si tuvieran que quedarse con una idea de este bloque, sería esta: **el engine se crea una sola vez y representa la conexión configurada a la base de datos**."

---

## 3.5. Sesión, `Depends` y ciclo de vida — Guillermo (3:10–5:10)

> "El engine no es lo que usamos directamente en los endpoints. Para trabajar usamos una **sesión**."
>
> "Piensen en la sesión como una hoja de trabajo: ahí hacemos las consultas, anotamos los cambios y al final decidimos si los confirmamos o no."

[SEÑALAR la diapositiva del ciclo de una petición.]

> "En el código hay una función pequeña que parece no hacer mucho, pero es clave:"

```python
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

> "`get_session` abre una sesión con `with`, la entrega con `yield` y, cuando el endpoint termina, el `with` se encarga de cerrarla."
>
> "`yield` es la pausa: entrega la sesión, el endpoint trabaja, y cuando termina, la ejecución continúa y se cierra la sesión."
>
> "`SessionDep` es un atajo de tipado. Gracias a `Depends`, FastAPI sabe que antes de ejecutar el endpoint debe llamar a `get_session` y pasarle la sesión como argumento."

> "Y esto es importante: **la sesión se crea por cada petición HTTP**, no una sola vez para toda la aplicación."
>
> "¿Por qué? Porque si todos los usuarios compartieran una sola sesión, se mezclarían estados y transacciones. Una sesión por petición aísla el trabajo de cada usuario."

[SEÑALAR la diapositiva de arranque.]

> "También hay una función que se ejecuta al arrancar:"

```python
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
```

> "`create_all` crea las tablas que faltan. Si `chatbot.db` no existe, lo crea. Si ya existe, no borra nada."
>
> "Ojo: `create_all` **no es un sistema de migraciones**. Si mañana agregamos una columna a la clase, no la va a agregar a una tabla que ya existe. Para eso se necesitan herramientas como Alembic."

> "Resumiendo esta primera parte: **engine una vez, sesión por petición, y `Depends` se encarga del ciclo de vida**."

---

## 3.6. Transición — Guillermo (5:10–5:40)

> "Hasta aquí el concepto. Ahora Jhon les va a mostrar cómo se ve todo esto en el código real y lo va a probar en vivo."
>
> "Presten atención a tres momentos: cuándo se abre la sesión, cuándo se confirma un cambio y cuándo se cierra."

[Guillermo pasa el control y se ubica al lado de la pantalla para apoyar.]

---

## 3.7. Modelo y conexión — Jhon (5:40–7:10)

> [Jhon comparte pantalla con `main.py` abierto.]
>
> "Gracias, Guillermo. Vamos a ver el código. Primero, el modelo y la conexión."

[SEÑALAR las líneas 12 a 22 de `main.py`.]

```python
class Mensaje(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    rol: str
    texto: str
    fecha: str

sqlite_file_name = "chatbot.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
```

> "Esta clase `Mensaje` es la tabla. El `table=True` le dice a SQLModel que no es una clase cualquiera: que se convierta en una tabla de la base de datos."
>
> "`id` es la clave primaria. SQLModel y SQLite se encargan de generarla automáticamente cuando insertamos un mensaje."
>
> "`rol`, `texto` y `fecha` son las columnas. `rol` distingue si el mensaje lo escribió el usuario o el bot."
>
> "Abajo creamos el engine. Repito lo que dijo Guillermo: se crea una sola vez y queda listo para que cada sesión lo use."

[SEÑALAR las líneas 24 y 39–41.]

> "Aquí está la creación de tablas. Se ejecuta en el arranque del servidor. Si la base no existe, se crea; si ya existe, se respeta."

---

## 3.8. La sesión y `Depends` — Jhon (7:10–8:20)

[SEÑALAR las líneas 27 a 32.]

```python
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

> "Esta es la pieza que conecta FastAPI con la base. `get_session` abre la sesión, la entrega con `yield` y la cierra al final."
>
> "El `with` garantiza el cierre incluso si el endpoint falla. Eso evita dejar conexiones abiertas."
>
> "`SessionDep` nos permite escribir `session: SessionDep` en cualquier endpoint y recibir la sesión automáticamente."

[Señalar un endpoint cualquiera.]

> "Fíjense que en ningún endpoint escribimos `Session(engine)`. No la abrimos a mano: se la pedimos a FastAPI con `Depends`."

> "Eso también hace que el código sea más fácil de probar: en una prueba se puede reemplazar la dependencia por una base de datos de prueba."

---

## 3.9. `POST /chat/`: consultar, agregar y confirmar — Jhon (8:20–10:20)

[SEÑALAR las líneas 62 a 94.]

> "Ahora el endpoint más importante: el que recibe la pregunta del usuario."

```python
@app.post("/chat/")
def llamar_ia(mensaje: MensajeEntrada, session: SessionDep):
    historial = session.exec(select(Mensaje).order_by(Mensaje.id)).all()
    ...
```

> "Lo primero que hace es traer el historial desde la base. `session.exec` ejecuta una consulta; `select(Mensaje)` significa 'traeme todos los mensajes'; `order_by(Mensaje.id)` los ordena del más antiguo al más nuevo."
>
> "El resultado se convierte en una lista de pasos que se le envía a Gemini. Así el modelo tiene contexto de la conversación."

> "Después guarda la pregunta del usuario:"

```python
pregunta = Mensaje(rol="usuario", texto=mensaje.texto, fecha=time_user)
session.add(pregunta)
```

> "`session.add` no guarda en ese instante: deja el objeto pendiente dentro de la sesión."

> "Luego llama a Gemini y guarda la respuesta:"

```python
respuesta = Mensaje(rol="bot", texto=inferencia.output_text, fecha=time_bot)
session.add(respuesta)

session.commit()
session.refresh(respuesta)
```

> "Aquí está el momento clave: `session.commit()`. Ese es el que confirma la transacción y escribe de verdad en `chatbot.db`."
>
> "Si no hiciéramos `commit`, los cambios se perderían al cerrar la sesión."
>
> "`session.refresh(respuesta)` vuelve a leer el objeto desde la base para traer el `id` que SQLite generó automáticamente."

> [PAUSA.]
>
> "Un detalle que suele preguntar el profesor: ¿por qué el historial se consulta antes de agregar la pregunta nueva?"
>
> "Porque una consulta puede provocar un *autoflush*: SQLAlchemy envía a la base los cambios pendientes para poder consultar de forma coherente. Si consultáramos después de `add(pregunta)`, la pregunta actual podría aparecer dos veces: una desde la base y otra cuando la agregamos manualmente a la lista que va a Gemini. Consultando antes, evitamos el duplicado."

---

## 3.10. `GET /mensajes/` y el frontend — Jhon (10:20–11:20)

[SEÑALAR las líneas 97 a 104.]

```python
@app.get("/mensajes/")
def leer_mensajes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Mensaje]:
    mensajes = session.exec(select(Mensaje).offset(offset).limit(limit)).all()
    return mensajes
```

> "Este endpoint devuelve el historial. FastAPI toma la lista de objetos `Mensaje` y la convierte automáticamente a JSON."
>
> "`offset` y `limit` permiten paginar. `limit` tiene un máximo de 100 para no devolver una cantidad enorme de datos de una sola vez."

[Cambiar a `index.html` y señalar el `fetch`.]

> "Y acá se ve la conexión con el frontend. Al cargar la página, `index.html` hace un `GET /mensajes/` y dibuja los mensajes que ya estaban guardados. Cuando el usuario envía uno nuevo, hace un `POST /chat/`."

> "El navegador nunca toca SQLite. Todo pasa por FastAPI. Esa es la separación que buscamos."

---

## 3.11. Demo en vivo — Jhon (11:20–14:10)

> "Vamos a probarlo. Primero, el endpoint de salud, que no depende de Gemini."

[Terminal.]

```bash
curl http://localhost:8000/health
```

> "Responde `status: ok`. Esto confirma que el servidor y la sesión están funcionando."

> "Ahora abrimos la documentación automática de FastAPI."

[Abrir `http://localhost:8000/docs`. Mostrar `POST /chat/`, `GET /mensajes/` y `GET /health`.]

> "FastAPI genera esta documentación a partir del código. Aquí podemos probar los endpoints sin escribir el frontend."

> "Vamos a enviar una pregunta."

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"texto": "Hola, me llamo Ana"}'
```

> "El servidor consulta el historial, guarda la pregunta, llama a Gemini, guarda la respuesta y confirma con `commit`."

> "Ahora consultamos el historial."

```bash
curl http://localhost:8000/mensajes/
```

> "Aparecen el mensaje del usuario y el del bot. Y como están en la base, van a seguir ahí aunque reiniciemos el servidor."

> "Ahora abrimos la base directamente para comprobar que no hay magia."

[Terminal aparte.]

```bash
sqlite3 chatbot.db
```

Dentro de SQLite:

```sql
.tables
SELECT * FROM mensaje;
.quit
```

> "La tabla se llama `mensaje`, en minúsculas. Cada fila es un mensaje real. Lo que vimos por HTTP es exactamente lo que está guardado acá."

[Volver al navegador y recargar `index.html`.]

> "Al recargar la página, el frontend vuelve a pedir `GET /mensajes/` y la conversación sigue apareciendo. Eso es la memoria persistente."

> "Y si ahora envían otra pregunta, el endpoint `POST /chat/` va a leer este historial y se lo va a pasar a Gemini como contexto. Por eso el bot puede recordar el nombre que le dijeron antes."

### Si la demo falla

Si `POST /chat/` falla por la API de Gemini:

> "La llamada a Gemini falló por la clave o la conexión. Lo importante es que el flujo de la sesión es el mismo: si la inferencia falla, no se hace `commit` y no se guarda nada. Vamos a mostrar la base directamente y el `GET /mensajes/` con los datos que ya tenemos."

[Usar el plan B de `guia_exposicion_sqlite.md`: mostrar `/docs`, `GET /mensajes/` y `sqlite3`.]

Si no hay datos:

```bash
sqlite3 chatbot.db
```

```sql
INSERT INTO mensaje (rol, texto, fecha) VALUES
('usuario', 'Hola, me llamo Ana', '2026-11-21T10:00:00+00:00'),
('bot', '¡Hola, Ana! ¿En qué puedo ayudarte?', '2026-11-21T10:00:01+00:00');
```

> "Insertamos datos de prueba directamente para demostrar que la sesión de FastAPI lee cualquier dato que esté en la base."

---

## 3.12. Cierre y pregunta para el salón — Guillermo (14:10–15:00)

> [Guillermo vuelve al frente.]

> "Para cerrar: el **engine** se crea una sola vez y sabe cómo conectarse a `chatbot.db`. La **sesión** se crea por cada petición gracias a `Depends(get_session)`. Dentro de esa sesión consultamos con `session.exec`, agregamos con `session.add` y confirmamos con `session.commit`."
>
> "Eso permite que el chatbot tenga memoria y que cada usuario trabaje con su propio estado, sin mezclarse con los demás."

> "Les dejamos una pregunta para pensar."

[Pausa de 5 segundos. Mostrar la pregunta en la diapositiva.]

> "**¿Qué pasaría si usáramos una sola sesión global para todos los requests?**"

[Esperar 10–15 segundos. Si nadie responde, dar una pista: "Piensen en dos usuarios escribiendo al mismo tiempo".]

> "La respuesta es que se compartiría estado entre usuarios. Una transacción podría mezclarse con otra, aparecerían datos de una conversación en otra y habría problemas de concurrencia. Por eso cada petición debe tener su propia sesión, y por eso la sesión se cierra al terminar."
>
> "Gracias."

---

# 4. Preguntas finales para el salón (con respuestas)

Usar **una** como pregunta principal. Las otras quedan como respaldo si el profesor pide más participación.

### Pregunta 1 (recomendada)

**¿Qué pasaría si usáramos una sola sesión global para todos los requests?**

**Respuesta:**

> Se compartiría el estado entre usuarios. Dos peticiones podrían modificar la misma sesión al mismo tiempo, mezclar transacciones y ver datos que no les corresponden. Además, una sesión de SQLAlchemy no está pensada para usarse desde varios hilos. Por eso se crea una sesión por petición y se cierra al final.

### Pregunta 2

**¿Cuál es la diferencia entre `session.add()` y `session.commit()`?**

**Respuesta:**

> `add()` deja el objeto pendiente dentro de la sesión, pero no lo escribe en la base. `commit()` confirma la transacción y guarda los cambios de forma permanente. Si se cierra la sesión sin `commit`, el cambio se descarta.

### Pregunta 3

**¿Qué ocurre si el servidor se cae después de `session.add()` pero antes de `session.commit()`?**

**Respuesta:**

> El cambio no se guarda. `add()` no confirma nada; la escritura real ocurre en el `commit`. Al perderse la sesión, la transacción pendiente se descarta. Eso es útil: evita guardar una conversación a medias si la llamada a Gemini falla.

### Pregunta 4

**¿Por qué `create_all()` no es suficiente para actualizar la base cuando cambia el modelo?**

**Respuesta:**

> Porque `create_all()` solo crea tablas que no existen. No compara columnas ni modifica tablas existentes. Si se agrega o cambia una columna, hay que usar una migración, por ejemplo con Alembic.

### Pregunta 5

**¿El frontend puede conectarse directamente a SQLite?**

**Respuesta:**

> No en esta arquitectura. El frontend solo habla HTTP con FastAPI. FastAPI es el que usa la sesión y accede a SQLite. Poner la base directamente en el navegador rompería la separación y la seguridad.

---

# 5. Preguntas sorpresa del profesor (con respuestas)

Estas son para la ronda individual. Responder corto, claro y sin leer.

### 5.1. ¿Qué es el engine?

> Es el objeto que administra la conexión a la base de datos. Se crea una sola vez con `create_engine` y las sesiones lo usan para conectarse. No es una sesión ni una transacción.

### 5.2. ¿Qué hace `Depends(get_session)`?

> Le dice a FastAPI que antes de ejecutar el endpoint llame a `get_session`, obtenga la sesión y se la pase como argumento. Al terminar la petición, la dependencia cierra la sesión.

### 5.3. ¿Qué hace `yield` en `get_session`?

> Entrega la sesión al endpoint y deja la función pausada. Cuando el endpoint termina, la ejecución continúa y el bloque `with` cierra la sesión.

### 5.4. ¿Por qué `check_same_thread=False`?

> Porque FastAPI puede ejecutar la función en un hilo distinto al que creó la conexión, y SQLite por defecto lo bloquea. Como cada petición usa su propia sesión, es seguro desactivarlo en este proyecto.

### 5.5. ¿Cada petición crea una sesión nueva?

> Sí. `Depends` ejecuta `get_session` una vez por petición. Eso aísla el trabajo de cada usuario y evita compartir estado.

### 5.6. ¿Qué pasa si no se hace `commit`?

> Los cambios quedan pendientes y se descartan al cerrar la sesión. No se escriben en la base.

### 5.7. ¿Qué hace `session.refresh()`?

> Vuelve a leer el objeto desde la base para actualizar sus valores, por ejemplo para obtener el `id` generado por SQLite.

### 5.8. ¿Qué diferencia hay entre `session.get()` y `session.exec(select(...))`?

> `session.get(Mensaje, id)` busca directamente por clave primaria. `session.exec(select(...))` permite consultas más flexibles con filtros, orden y paginación.

### 5.9. ¿Qué pasa si dos usuarios escriben al mismo tiempo en SQLite?

> Cada uno tiene su propia sesión. SQLite permite varias lecturas, pero las escrituras se serializan: una espera a la otra. Con transacciones cortas funciona bien; para mucha concurrencia se recomienda PostgreSQL.

### 5.10. ¿Dónde está la base de datos?

> En el archivo `chatbot.db`, en la carpeta desde donde se ejecuta el servidor. La URL `sqlite:///chatbot.db` es relativa.

### 5.11. ¿Cómo se evita la inyección SQL?

> Usando SQLModel/SQLAlchemy en lugar de concatenar strings. Los valores de `select`, `where` y los parámetros se envían de forma parametrizada.

### 5.12. ¿Por qué se consulta el historial antes de `session.add(pregunta)`?

> Para evitar un duplicado por *autoflush*. Si se consulta después de agregar, la pregunta nueva puede aparecer una vez desde la base y otra desde la lista que armamos manualmente.

### 5.13. ¿Qué hace `create_all()`?

> Crea las tablas que no existen. No modifica tablas existentes ni agrega columnas; para cambios de estructura se necesitan migraciones.

### 5.14. ¿Por qué se usa `@app.on_event("startup")`?

> Para ejecutar la creación de tablas cuando arranca la aplicación. En FastAPI moderno se recomienda `lifespan`, pero `on_event` sigue funcionando.

### 5.15. ¿La sesión se puede compartir entre endpoints?

> No. La sesión debe vivir lo que dura la petición. Compartirla entre peticiones o hilos puede mezclar transacciones y producir errores.

---

# 6. Cambios en vivo preparados

Si el profesor pide un cambio, elegir uno y decirlo en voz alta antes de escribir.

## 6.1. "Agregá un endpoint para obtener un mensaje por ID"

> "Voy a agregar una ruta que reciba un `id`, busque el mensaje con `session.get` y devuelva 404 si no existe."

```python
@app.get("/mensajes/{mensaje_id}")
def leer_mensaje(mensaje_id: int, session: SessionDep) -> Mensaje:
    mensaje = session.get(Mensaje, mensaje_id)
    if mensaje is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return mensaje
```

Probar:

```bash
curl http://localhost:8000/mensajes/1
```

Qué explicar:

> "`session.get` busca por clave primaria. Si no encuentra nada, devuelve `None`, y ahí respondemos 404."

## 6.2. "Filtrá los mensajes por rol"

> "Voy a agregar un parámetro opcional `rol` y, si viene, agrego un `where` a la consulta."

```python
@app.get("/mensajes/")
def leer_mensajes(
    session: SessionDep,
    rol: str | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Mensaje]:
    consulta = select(Mensaje)
    if rol is not None:
        consulta = consulta.where(Mensaje.rol == rol)
    return session.exec(consulta.offset(offset).limit(limit)).all()
```

Probar:

```bash
curl "http://localhost:8000/mensajes/?rol=usuario"
```

## 6.3. "Ordená los mensajes del más nuevo al más viejo"

> "Cambio el `order_by` a `desc`."

```python
mensajes = session.exec(
    select(Mensaje).order_by(Mensaje.id.desc()).offset(offset).limit(limit)
).all()
```

## 6.4. "Limitar el historial que se envía a Gemini"

> "Traigo solo los últimos 20 mensajes y los invierto para conservar el orden cronológico."

```python
historial = session.exec(
    select(Mensaje).order_by(Mensaje.id.desc()).limit(20)
).all()
historial.reverse()
```

## 6.5. "Agregá un endpoint para borrar un mensaje"

> "Busco el mensaje, lo marco con `delete` y confirmo con `commit`."

```python
@app.delete("/mensajes/{mensaje_id}")
def borrar_mensaje(mensaje_id: int, session: SessionDep):
    mensaje = session.get(Mensaje, mensaje_id)
    if mensaje is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    session.delete(mensaje)
    session.commit()
    return {"mensaje": "Eliminado"}
```

## 6.6. "Contá cuántos mensajes hay"

```python
from sqlmodel import func

@app.get("/mensajes/count")
def contar_mensajes(session: SessionDep) -> dict:
    total = session.exec(select(func.count()).select_from(Mensaje)).one()
    return {"total": total}
```

> "Esta ruta debe ir antes de `/mensajes/{mensaje_id}` para que `count` no se interprete como un ID."

---

# 7. Frases de emergencia

Si se olvida una idea:

- "Volviendo a lo importante: el engine se crea una vez, la sesión se crea por petición."
- "La sesión es la unidad de trabajo; el commit es lo que guarda de verdad."
- "FastAPI no guarda la conversación: la guarda SQLite a través de la sesión."
- "El frontend no habla con la base; habla con FastAPI."

Si una pregunta no se sabe:

> "No lo tenemos medido en este proyecto, pero lo que sí podemos afirmar es [idea segura]. Lo revisamos y les confirmamos."

No inventar. Es mejor reconocer el límite y responder con lo que sí se sabe.

---

# 8. Cierre en una frase

> "FastAPI se conecta a SQLite con un `engine` creado una sola vez, y trabaja con una `Session` nueva por cada petición gracias a `Depends(get_session)`; dentro de esa sesión consulta, agrega y confirma cambios con `commit`, y el frontend solo se comunica por HTTP."
