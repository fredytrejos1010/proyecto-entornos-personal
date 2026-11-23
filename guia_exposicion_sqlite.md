# Guía de exposición: Conexión y sesiones con SQLite en FastAPI

**Tema:** cómo FastAPI se conecta a la base de datos SQLite y cómo maneja las sesiones.
**Proyecto:** chatbot del curso (`main.py`, `index.html`).
**Duración:** 15 minutos.
**Formato:** una persona explica el concepto y la otra lo muestra funcionando en el código. Al final se deja una pregunta corta para el salón.

---

## 1. Objetivo de la exposición

Al terminar, el salón debe entender:

1. Cómo se conecta FastAPI a una base de datos SQLite.
2. Qué papel cumplen `engine`, `Session` y `Depends`.
3. Cuándo se abre y se cierra una sesión.
4. Cómo se guardan y consultan los mensajes del chatbot.
5. Por qué cada petición HTTP usa su propia sesión.

Idea central para repetir varias veces:

> **El `engine` es la conexión configurada a la base de datos; la `Session` es la unidad de trabajo de una petición; `Depends` se encarga de abrirla y cerrarla automáticamente.**

---

## 2. Reparto sugerido

| Integrante | Rol | Tiempo aproximado |
|---|---|---|
| Guillermo | Explica el concepto: SQLite, `engine`, sesión y dependencias. | 5–6 min |
| Jhon | Muestra el código y hace la demo en vivo. | 7–8 min |
| Ambos | Cierre y pregunta para el salón. | 1–2 min |

Sugerencia: Guillermo habla primero y Jhon va señalando en pantalla las líneas de `main.py` a medida que se mencionan.

---

## 3. Guion con tiempos

### 0:00–1:00 — Introducción y gancho

Guillermo:

> "Nuestro chatbot recibe una pregunta, llama a Gemini y devuelve una respuesta. Pero si no guardáramos nada, al recargar la página se perdería toda la conversación. Hoy vamos a ver cómo FastAPI se conecta a SQLite y cómo maneja las sesiones para que esos mensajes queden guardados."

Mostrar rápidamente `index.html` y decir que la conversación se recupera con `GET /mensajes/`.

### 1:00–5:30 — Concepto (Guillermo)

Explicar en este orden:

1. **¿Qué es SQLite?**
   - Base de datos relacional que vive en un solo archivo: `chatbot.db`.
   - No necesita servidor aparte.
   - Ideal para proyectos pequeños y demos.

2. **¿Qué es SQLModel?**
   - Librería que combina SQLAlchemy (base de datos) con Pydantic (validación).
   - Una clase con `table=True` se convierte en una tabla.

3. **El modelo `Mensaje`**
   - Representa la tabla.
   - Campos: `id`, `rol`, `texto`, `fecha`.

4. **El `engine`**
   - Es el objeto que sabe cómo conectarse a la base.
   - `sqlite:///chatbot.db` significa archivo relativo a la carpeta del proyecto.
   - Se crea una sola vez al iniciar la aplicación.

5. **La sesión**
   - Es la unidad de trabajo: se hacen consultas, se agregan objetos y se confirma con `commit`.
   - No debe ser global ni compartida entre peticiones.

6. **`Depends` y el ciclo de vida**
   - FastAPI llama a `get_session()` por cada petición.
   - El `yield` entrega la sesión al endpoint.
   - Al terminar la petición, el bloque `with` cierra la sesión.

7. **Creación de tablas**
   - `create_db_and_tables()` se ejecuta al arrancar.
   - `create_all` crea las tablas que faltan; **no** actualiza tablas existentes (no es una migración).

Frase para cerrar esta parte:

> "El engine se crea una vez; la sesión se crea por petición; y `Depends` es el puente entre FastAPI y esa sesión."

### 5:30–11:30 — Código y demo (Jhon)

Recorrer `main.py` en este orden, señalando cada bloque:

#### a) Modelo y conexión (líneas 12–22)

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

Explicar:

- `table=True` convierte la clase en tabla.
- `primary_key=True` genera el `id` automático.
- `check_same_thread=False` permite que FastAPI use la conexión desde distintos hilos. Es seguro porque cada petición usa su propia sesión.

#### b) Creación de tablas (líneas 24–25 y 39–41)

```python
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
```

Explicar:

- Se ejecuta una vez cuando arranca el servidor.
- Si `chatbot.db` no existe, se crea.
- Si ya existe, no borra datos.

#### c) La dependencia de sesión (líneas 27–32)

```python
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

Explicar:

- `yield` entrega la sesión y deja el `with` abierto.
- Al terminar el endpoint, se ejecuta el cierre del `with`.
- `SessionDep` es un atajo de tipado para no repetir `Depends(get_session)`.

#### d) Endpoint `POST /chat/` (líneas 62–94)

Mostrar especialmente:

```python
def llamar_ia(mensaje: MensajeEntrada, session: SessionDep):
    historial = session.exec(select(Mensaje).order_by(Mensaje.id)).all()
    ...
    pregunta = Mensaje(rol="usuario", texto=mensaje.texto, fecha=time_user)
    session.add(pregunta)
    ...
    respuesta = Mensaje(rol="bot", texto=inferencia.output_text, fecha=time_bot)
    session.add(respuesta)
    session.commit()
    session.refresh(respuesta)
```

Explicar:

- La sesión llega inyectada por FastAPI.
- `session.exec(select(...))` consulta la base.
- `session.add()` deja el objeto pendiente.
- `session.commit()` confirma y guarda de verdad.
- `session.refresh()` vuelve a leer el objeto para obtener el `id` generado.
- El historial se consulta **antes** de agregar la pregunta nueva para no duplicarla.

#### e) Endpoint `GET /mensajes/` (líneas 97–104)

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

Explicar:

- Cada petición recibe una sesión nueva.
- `offset` y `limit` permiten paginar.
- El resultado se convierte automáticamente a JSON.

### 11:30–13:30 — Demo en vivo

Orden recomendado:

1. Abrir dos terminales.

2. Terminal 1: activar entorno y arrancar el servidor.

```bash
source .venv/bin/activate
export GEMINI_API_KEY="tu_clave"
uvicorn main:app --reload --port 8000
```

3. Abrir `http://localhost:8000/docs` y mostrar los endpoints.

4. Probar salud:

```bash
curl http://localhost:8000/health
```

5. Enviar un mensaje:

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"texto": "Hola, me llamo Ana"}'
```

6. Consultar el historial:

```bash
curl http://localhost:8000/mensajes/
```

7. Terminal 2: abrir la base directamente.

```bash
sqlite3 chatbot.db
```

Dentro de SQLite:

```sql
.tables
SELECT * FROM mensaje;
.quit
```

8. Recargar `index.html` y mostrar que la conversación se carga desde `GET /mensajes/`.

### 13:30–15:00 — Cierre y pregunta para el salón

Jhon:

> "Entonces, el engine se crea una sola vez, pero la sesión se crea por cada petición. Eso evita compartir estado entre usuarios y mantiene las transacciones cortas."

Pregunta corta para el salón (elegir una):

- **¿Qué pasaría si usáramos una sola sesión global para todos los requests?**
- **¿Qué diferencia hay entre `session.add()` y `session.commit()`?**
- **¿Qué ocurre si se cae el servidor justo después de `session.add()` pero antes de `session.commit()`?**
- **¿Por qué `create_all()` no sirve como sistema de migraciones?**

Respuesta esperada de la primera:

> "Se compartiría estado entre usuarios, habría riesgo de mezclar transacciones y problemas de concurrencia. La sesión debe ser por petición."

---

## 4. Demo de respaldo si falla la API de Gemini

El endpoint `POST /chat/` depende de la API externa. Si falla la clave o la conexión, la demo puede quedar en blanco.

Plan B:

1. Mostrar `GET /health` y `GET /docs`, que no dependen de Gemini.
2. Mostrar el código de `get_session` y del endpoint.
3. Insertar datos de prueba directamente en SQLite:

```bash
sqlite3 chatbot.db
```

```sql
INSERT INTO mensaje (rol, texto, fecha) VALUES
('usuario', 'Hola, me llamo Ana', '2026-11-21T10:00:00+00:00'),
('bot', '¡Hola, Ana! ¿En qué puedo ayudarte?', '2026-11-21T10:00:01+00:00');
```

4. Consultar `GET /mensajes/` y mostrar que la sesión lee esos datos.

Esto además demuestra que la base es independiente del chatbot: es un archivo SQLite normal.

---

## 5. Posibles preguntas sorpresa y respuestas

### Sobre conexión

**1. ¿Qué significa `sqlite:///chatbot.db`?**
Es una URL de SQLAlchemy. Tres barras indican una ruta relativa; el archivo `chatbot.db` se crea en el directorio desde donde se ejecuta el servidor. Con cuatro barras (`sqlite:////ruta/absoluta/chatbot.db`) se usa una ruta absoluta.

**2. ¿Por qué `check_same_thread=False`?**
Porque FastAPI puede ejecutar la función en un hilo distinto al que creó la conexión. SQLite por defecto bloquea eso. Como cada petición tiene su propia sesión, desactivar esa verificación es seguro en este contexto.

**3. ¿Qué pasa si no pongo `check_same_thread=False`?**
Puede aparecer un error del tipo `SQLite objects created in a thread can only be used in that same thread`.

**4. ¿El `engine` se crea por cada petición?**
No. Se crea una vez al importar el módulo. Lo que se crea por petición es la `Session`.

**5. ¿La `Session` es segura para usarse entre hilos o peticiones?**
No. Por eso se crea una por petición y se cierra al finalizar.

### Sobre sesiones

**6. ¿Qué hace exactamente `yield` en `get_session`?**
Entrega la sesión al endpoint y mantiene el contexto abierto. Cuando el endpoint termina, la ejecución continúa después del `yield` y el `with` cierra la sesión.

**7. ¿Qué diferencia hay entre `session.add()` y `session.commit()`?**
`add()` deja el objeto en la sesión, pendiente. `commit()` confirma la transacción y lo escribe en la base.

**8. ¿Qué hace `session.refresh()`?**
Vuelve a leer el objeto desde la base para traer valores generados, como el `id` automático.

**9. ¿Qué pasa si se hace `add()` pero no `commit()`?**
El cambio no se guarda. Al cerrarse la sesión, la transacción pendiente se descarta.

**10. ¿Por qué el historial se consulta antes de agregar la pregunta nueva?**
Porque una consulta puede provocar un *autoflush* y enviar a la base los cambios pendientes. Si se consultara después de `add(pregunta)`, la pregunta actual podría aparecer dos veces: una desde la base y otra al agregarla manualmente a `entrada`.

**11. ¿Qué pasa si dos usuarios escriben al mismo tiempo?**
Cada uno tiene su sesión. SQLite permite varias lecturas, pero las escrituras se serializan. Con transacciones cortas como las de este proyecto funciona bien. Para alta concurrencia se recomienda PostgreSQL.

**12. ¿Qué diferencia hay entre `select(Mensaje)` y una consulta SQL escrita a mano?**
SQLModel construye la consulta y parametriza los valores, lo que evita inyección SQL y aprovecha el tipado.

**13. ¿Qué hace `create_all()`?**
Crea las tablas que no existen. No modifica tablas existentes ni agrega columnas nuevas; para eso se necesitan migraciones (por ejemplo, Alembic).

**14. ¿Por qué se usa `@app.on_event("startup")`?**
Para ejecutar la creación de tablas al arrancar. En versiones modernas de FastAPI se recomienda `lifespan`, pero `on_event` sigue funcionando.

### Sobre el proyecto

**15. ¿Dónde está la base de datos?**
En el archivo `chatbot.db`, en la carpeta desde donde se inicia el servidor.

**16. ¿Cómo se ve la tabla?**
La tabla se llama `mensaje` porque SQLModel usa el nombre de la clase en minúsculas.

**17. ¿Por qué hay dos `from fastapi import FastAPI`?**
Es un detalle de estilo: se importa dos veces y la segunda reemplaza a la primera. No rompe nada, pero se puede limpiar.

**18. ¿Cómo se conecta el frontend con la base?**
El frontend nunca toca SQLite. Llama a FastAPI (`POST /chat/`, `GET /mensajes/`) y es FastAPI quien usa la sesión y la base.

---

## 6. Cambios en vivo para tener preparados

Estos cambios son pequeños, seguros y demuestran dominio del tema. Tenerlos escritos o memorizados.

### Cambio A: obtener un mensaje por ID

Agregar antes de `GET /mensajes/`:

```python
@app.get("/mensajes/{mensaje_id}")
def leer_mensaje(mensaje_id: int, session: SessionDep) -> Mensaje:
    mensaje = session.get(Mensaje, mensaje_id)
    if mensaje is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return mensaje
```

Qué explicar: `session.get()` busca por clave primaria; no hace falta escribir un `select`.

### Cambio B: filtrar por rol

Modificar `leer_mensajes`:

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

### Cambio C: ordenar del más reciente al más antiguo

```python
mensajes = session.exec(
    select(Mensaje).order_by(Mensaje.id.desc()).offset(offset).limit(limit)
).all()
```

### Cambio D: limitar el historial que se envía al modelo

En `POST /chat/`, cambiar la consulta del historial por las últimas 10 conversaciones:

```python
historial = session.exec(
    select(Mensaje).order_by(Mensaje.id.desc()).limit(20)
).all()
historial.reverse()
```

Qué explicar: se piden los últimos 20 mensajes y luego se invierten para conservar el orden cronológico.

### Cambio E: borrar un mensaje

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

Qué explicar: `delete()` marca el objeto y `commit()` confirma el borrado.

### Cambio F: contar mensajes

Requiere importar `func`:

```python
from sqlmodel import func

@app.get("/mensajes/count")
def contar_mensajes(session: SessionDep) -> dict:
    total = session.exec(select(func.count()).select_from(Mensaje)).one()
    return {"total": total}
```

Nota: si se agrega esta ruta, debe ir **antes** de `GET /mensajes/{mensaje_id}` para que `count` no se interprete como un ID.

---

## 7. Estructura visual sugerida para las diapositivas

Solo si se usan diapositivas. Con 4 o 5 es suficiente:

1. **Título:** Conexión y sesiones con SQLite en FastAPI.
2. **Arquitectura:** `index.html → FastAPI → SQLModel/Session → chatbot.db`.
3. **Tres piezas clave:** `engine`, `Session`, `Depends`.
4. **Ciclo de una petición:** llega request → `get_session` → endpoint → `commit` → cierre.
5. **Demo / pregunta final.**

Diagrama de texto para la diapositiva 2:

```
Navegador (index.html)
        |
        | HTTP (fetch)
        v
FastAPI (main.py)
        |
        | Session (SQLModel)
        v
SQLite (chatbot.db)
```

---

## 8. Frases clave para la exposición

- "El `engine` se crea una sola vez; la sesión se crea por cada petición."
- "`Depends` no crea la sesión por magia: llama a `get_session`, que la abre y la cierra."
- "`add()` prepara el cambio; `commit()` lo confirma."
- "`create_all()` crea tablas faltantes, no migra tablas existentes."
- "El frontend no habla con SQLite; habla con FastAPI."
- "Cada petición tiene su propia sesión para evitar compartir estado entre usuarios."

---

## 9. Checklist antes de exponer

- [ ] Tener el entorno virtual activado.
- [ ] Tener `GEMINI_API_KEY` exportada **antes** de arrancar el servidor.
- [ ] Probar `uvicorn main:app --reload --port 8000`.
- [ ] Probar `GET /health`, `GET /docs`, `POST /chat/` y `GET /mensajes/`.
- [ ] Tener `sqlite3` instalado o una alternativa para mostrar la base.
- [ ] Tener datos previos en `chatbot.db` por si falla Gemini.
- [ ] Abrir `index.html` con el servidor corriendo.
- [ ] Tener el cambio en vivo (por ejemplo, `GET /mensajes/{id}`) listo para escribir.
- [ ] Ensayar la división de tiempos al menos una vez.

---

## 10. Resumen de una frase

> FastAPI se conecta a SQLite mediante un `engine` creado una sola vez, y usa una `Session` nueva por cada petición gracias a `Depends(get_session)`; el endpoint consulta, agrega y confirma cambios con `commit`, y el frontend solo se comunica por HTTP con FastAPI.
