# Estructura de diapositivas: Conexión y sesiones con SQLite en FastAPI

**Archivo de apoyo:** `guia_exposicion_sqlite_guion.md`
**Duración total:** 15 minutos
**Cantidad sugerida:** 10 diapositivas principales + 2 de respaldo
**Formato:** 16:9

> Regla de oro: la diapositiva no compite con el expositor. Debe tener poco texto, una idea por slide y código solo cuando sea indispensable.

---

## 1. Mapa general de la presentación

| # | Diapositiva | Quién | Tiempo | Función |
|---|---|---|---|---|
| 1 | Portada | Guillermo | 0:00–0:30 | Presentar el tema. |
| 2 | El problema: un chatbot sin memoria | Guillermo | 0:30–1:00 | Generar interés. |
| 3 | Arquitectura del proyecto | Guillermo | 1:00–2:00 | Ubicar las piezas. |
| 4 | Las tres piezas clave | Guillermo | 2:00–5:40 | Explicar engine, sesión y Depends. |
| 5 | El modelo es la tabla | Jhon | 5:40–6:30 | Mostrar `Mensaje`. |
| 6 | La conexión: engine + SQLite | Jhon | 6:30–7:10 | Mostrar `create_engine`. |
| 7 | Una sesión por petición | Jhon | 7:10–8:20 | Mostrar `get_session`. |
| 8 | Guardar y leer mensajes | Jhon | 8:20–10:20 | Mostrar `POST` y `GET`. |
| 9 | Demo en vivo | Jhon | 10:20–14:10 | Probar el flujo real. |
| 10 | La idea central y la pregunta | Guillermo | 14:10–15:00 | Cerrar y preguntar. |
| 11 | Respuesta a la pregunta | Guillermo | 14:40–15:00 | Revelar la respuesta. |
| R1 | Respaldo: definiciones | Ambos | — | Si el profesor pregunta. |
| R2 | Respaldo: cambios en vivo | Jhon | — | Si piden modificar código. |

Las diapositivas 4 a 8 se apoyan con el guion conceptual y el recorrido del código. Si el tiempo se acorta, saltar de la 4 a la 8 y hacer la demo más breve.

---

## 2. Diseño visual recomendado

- **Fondo:** claro, blanco o gris muy suave.
- **Texto:** oscuro, sin sombras ni efectos.
- **Color de acento:** uno solo, por ejemplo azul o verde.
- **Código:** fuente monoespaciada (Consolas, Fira Code o similar), mínimo 18 pt.
- **Texto normal:** mínimo 24 pt.
- **Títulos:** 32–40 pt.
- **Máximo por slide:** 6 líneas de texto o 10 líneas de código.
- **Una idea por slide.** Si hay dos ideas, dividir.
- **Resaltar una sola línea** del bloque de código por slide, por ejemplo `session.commit()`.
- **Sin animaciones** salvo la aparición de la respuesta en la slide 11.
- **Número de slide** discreto en una esquina.
- No incluir párrafos completos: el guion va en la cabeza o en notas del expositor.

---

## 3. Contenido de cada diapositiva

### Diapositiva 1 — Portada

**Texto en pantalla:**

> **Conexión y sesiones con SQLite en FastAPI**
>
> Cómo el chatbot del curso guarda su memoria
>
> [Nombre A] · [Nombre B]
>
> [Curso] · [Fecha]

**Elemento visual:**

- Un icono de base de datos y otro de servidor, unidos por una flecha.
- Alternativa: fondo limpio, sin imágenes.

**Notas para Guillermo:**

> No leer la portada. Mientras el salón se ubica, decir: "Buenos días, hoy les vamos a mostrar cómo nuestro chatbot guarda la conversación en SQLite".

**Evitar:** logos grandes, frases motivacionales, exceso de datos.

---

### Diapositiva 2 — El problema: un chatbot sin memoria

**Texto en pantalla:**

> **Sin base de datos**
> Recargar la página = perder la conversación.
>
> **Con base de datos**
> La conversación sobrevive al reinicio.
>
> **Pregunta guía:** ¿dónde vive la información?

**Elemento visual:**

- Dos paneles lado a lado: "Antes" y "Después".
- Antes: un chat que se borra.
- Después: el mismo chat que se conserva.

**Notas para Guillermo:**

> Explicar que la memoria no está en el navegador ni en la memoria del servidor, sino en un archivo. No entrar todavía en código.

**Evitar:** tecnicismos como "persistencia" sin explicarlos.

---

### Diapositiva 3 — Arquitectura del proyecto

**Texto en pantalla:**

> **Navegador** (`index.html`)
> ↓ HTTP
> **FastAPI** (`main.py`)
> ↓ Sesión SQLModel
> **SQLite** (`chatbot.db`)

**Texto pequeño al pie:**

> El frontend nunca toca la base de datos.

**Elemento visual:**

- Diagrama grande con tres cajas y dos flechas.
- Poner "HTTP" sobre la primera flecha y "Session" sobre la segunda.

**Notas para Guillermo:**

> "El navegador solo hace peticiones HTTP. FastAPI es el único que conoce la base de datos. SQLite es un archivo."

**Evitar:** mostrar todo el código de `main.py` en esta slide.

---

### Diapositiva 4 — Las tres piezas clave

**Texto en pantalla:**

> **Engine**
> La conexión configurada. Se crea una sola vez.
>
> **Session**
> La unidad de trabajo. Se crea por petición.
>
> **Depends(get_session)**
> Abre y cierra la sesión automáticamente.

**Texto pequeño al pie:**

> Engine una vez · Sesión por request · Depends se encarga del ciclo de vida.

**Elemento visual:**

- Tres tarjetas verticales u horizontales, cada una con su palabra clave.
- Opcional: analogía visual:
  - Engine = llave de la biblioteca.
  - Session = hoja de trabajo.
  - Depends = recepcionista que entrega y recoge la hoja.

**Notas para Guillermo:**

> Usar la analogía solo una vez. Si se extiende demasiado, perder tiempo. La frase del pie es la que debe quedar.

**Evitar:** explicar `commit` aquí; va en la slide 8.

---

### Diapositiva 5 — El modelo es la tabla

**Texto en pantalla:**

> **`SQLModel` = validación + mapeo a tabla**

**Código en pantalla:**

```python
class Mensaje(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    rol: str
    texto: str
    fecha: str
```

**Texto pequeño:**

> Tabla `mensaje`: una fila por cada mensaje de la conversación.

**Elemento visual:**

- Resaltar `table=True` y `primary_key=True`.
- A la derecha, una mini tabla de ejemplo con columnas `id | rol | texto | fecha`.

**Notas para Jhon:**

> "Esta clase es la tabla. `rol` distingue usuario de bot. `id` se genera solo."

**Evitar:** explicar Pydantic en profundidad.

---

### Diapositiva 6 — La conexión: engine + SQLite

**Texto en pantalla:**

> **Una sola conexión configurada**

**Código en pantalla:**

```python
sqlite_url = "sqlite:///chatbot.db"

engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
)
```

**Texto pequeño:**

> `create_all(engine)` al arrancar crea las tablas que faltan.

**Elemento visual:**

- Resaltar `sqlite:///chatbot.db`.
- Icono de archivo junto a `chatbot.db`.
- Una nota visual: "3 barras = ruta relativa".

**Notas para Jhon:**

> Explicar `check_same_thread=False` en una frase: FastAPI puede usar otro hilo y cada petición tiene su sesión. Mencionar que `create_all` no es migración.

**Evitar:** mostrar `connect_args` sin explicarlo; suele generar preguntas.

---

### Diapositiva 7 — Una sesión por petición

**Texto en pantalla:**

> **El ciclo de una petición**
>
> 1. Llega el request.
> 2. `Depends` llama a `get_session`.
> 3. La sesión se entrega al endpoint.
> 4. El endpoint consulta y confirma.
> 5. La sesión se cierra.

**Código en pantalla:**

```python
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

**Elemento visual:**

- Números del 1 al 5 alineados con una flecha.
- Resaltar `yield` y `with`.

**Notas para Jhon:**

> "El `with` garantiza el cierre. `yield` entrega la sesión y espera a que el endpoint termine. Cada request tiene su propia sesión."

**Evitar:** decir que la sesión se crea "una vez por usuario"; es por petición.

---

### Diapositiva 8 — Guardar y leer mensajes

**Texto en pantalla (dos columnas):**

> **Guardar** — `POST /chat/`
>
> ```python
> session.add(pregunta)
> session.add(respuesta)
> session.commit()
> session.refresh(respuesta)
> ```
>
> **Leer** — `GET /mensajes/`
>
> ```python
> mensajes = session.exec(
>     select(Mensaje).offset(offset).limit(limit)
> ).all()
> ```

**Texto pequeño al pie:**

> `add()` prepara · `commit()` guarda · `refresh()` trae el `id`

**Elemento visual:**

- Dos columnas bien separadas.
- Resaltar `session.commit()`.

**Notas para Jhon:**

> "`add` no guarda; `commit` sí. `refresh` trae el id generado. En `GET`, FastAPI convierte los objetos a JSON."
>
> Mencionar el detalle del historial: se consulta antes de agregar la pregunta nueva para evitar duplicados por autoflush.

**Evitar:** pegar el endpoint completo; solo las líneas clave.

---

### Diapositiva 9 — Demo en vivo

**Texto en pantalla:**

> **Demo**
>
> 1. `GET /health`
> 2. `POST /chat/`
> 3. `GET /mensajes/`
> 4. `sqlite3 chatbot.db`
> 5. Recargar `index.html`

**Código pequeño (opcional, en un recuadro tipo terminal):**

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"texto": "Hola, me llamo Ana"}'
```

**Elemento visual:**

- Recuadro oscuro tipo terminal, solo si se quiere mostrar el comando.
- Si se va a escribir en vivo, dejar la slide casi vacía para no distraer.

**Notas para Jhon:**

> No leer los comandos de la slide: ejecutarlos. Mientras corren, narrar qué está pasando: "consulta el historial, guarda, llama a Gemini, confirma".
>
> Tener el plan B listo si falla la API.

**Evitar:** mostrar la salida completa de `curl` en la slide; se ve en vivo.

---

### Diapositiva 10 — La idea central y la pregunta

**Texto en pantalla:**

> **Engine una vez.**
> **Sesión por petición.**
> **Commit para guardar.**
>
> **Para pensar:**
> ¿Qué pasaría si usáramos una sola sesión global para todos los requests?

**Elemento visual:**

- Fondo limpio.
- La pregunta en un recuadro de color, más grande que el resto.

**Notas para Guillermo:**

> Decir las tres frases. Hacer una pausa de 5 segundos. Leer la pregunta y esperar 10–15 segundos. Si nadie responde, dar la pista: "Piensen en dos usuarios escribiendo al mismo tiempo".

**Evitar:** responder inmediatamente. La pregunta debe quedar en el aire unos segundos.

---

### Diapositiva 11 — Respuesta a la pregunta

**Texto en pantalla:**

> Se compartiría el estado entre usuarios.
>
> Habría riesgo de mezclar transacciones y datos.
>
> Por eso: **una sesión por petición**.
>
> El `with` la cierra al terminar.

**Elemento visual:**

- La misma pregunta arriba, más pequeña y tachada o atenuada.
- La respuesta en el centro.

**Notas para Guillermo:**

> Leer la respuesta después de escuchar al salón. Cerrar con: "Gracias".

**Evitar:** dejar esta slide visible durante toda la exposición; solo al final.

---

## 4. Diapositivas de respaldo (no mostrar salvo que pregunten)

### R1 — Definiciones rápidas

**Texto en pantalla:**

> **Engine:** conexión configurada a la base.
>
> **Session:** unidad de trabajo por petición.
>
> **Depends:** inyecta y cierra la sesión.
>
> **Commit:** confirma la transacción.
>
> **Refresh:** relee el objeto desde la base.
>
> **create_all:** crea tablas faltantes, no migra.

**Uso:** si el profesor pide precisión conceptual.

---

### R2 — Cambios en vivo

**Texto en pantalla:**

> **Obtener por ID**
>
> ```python
> mensaje = session.get(Mensaje, mensaje_id)
> ```
>
> **Filtrar por rol**
>
> ```python
> consulta = select(Mensaje).where(Mensaje.rol == rol)
> ```
>
> **Borrar**
>
> ```python
> session.delete(mensaje)
> session.commit()
> ```

**Uso:** si piden modificar código en vivo. El código completo está en `guia_exposicion_sqlite_guion.md`, sección 6.

---

## 5. Texto exacto que NO debe ir en las diapositivas

Evitar estos bloques para no saturar:

- El código completo de `main.py`.
- Párrafos de más de dos líneas.
- La explicación de `check_same_thread` en texto largo.
- La lista completa de preguntas sorpresa.
- La teoría de SQLAlchemy o Pydantic.
- Capturas de pantalla ilegibles.
- Tablas comparativas de SQLite vs. PostgreSQL (no es el tema).

---

## 6. Diagrama listo para copiar en la slide 3

```text
┌─────────────────────┐
│  Navegador          │
│  index.html         │
└──────────┬──────────┘
           │ HTTP (fetch)
           ▼
┌─────────────────────┐
│  FastAPI            │
│  main.py            │
└──────────┬──────────┘
           │ Session (SQLModel)
           ▼
┌─────────────────────┐
│  SQLite             │
│  chatbot.db         │
└─────────────────────┘
```

---

## 7. Checklist de la presentación de diapositivas

- [ ] 10 slides principales, no más.
- [ ] Una idea por slide.
- [ ] Código con fuente legible desde el fondo del salón.
- [ ] Una sola línea resaltada por bloque de código.
- [ ] Pregunta final visible en la slide 10.
- [ ] Respuesta en la slide 11, solo para el cierre.
- [ ] Slides de respaldo ocultas al final.
- [ ] Número de slide y nombre de los expositores en la portada.
- [ ] Ensayo con cronómetro: no pasar de 15 minutos.
