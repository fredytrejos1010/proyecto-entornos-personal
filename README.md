# Chatbot personal

## Preparar el entorno en WSL (Ubuntu)

Desde la carpeta del proyecto, instala Python y el soporte para entornos virtuales si aún no los tienes:

```bash
sudo apt update
sudo apt install -y python3 python3-venv
```

Crea y activa el entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala las dependencias:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configurar la clave de Gemini

Establece tu clave en la terminal donde ejecutarás el servidor:

```bash
export GEMINI_API_KEY="TU_CLAVE_DE_GEMINI"
```

No compartas ni subas tu clave al repositorio. Si abres otra terminal, activa de nuevo el entorno virtual y establece la variable otra vez.

## Iniciar el servidor

Con el entorno virtual activado y la clave configurada:

```bash
fastapi dev main.py
```

La API estará disponible en <http://127.0.0.1:8000>. Puedes consultar y probar sus endpoints en <http://127.0.0.1:8000/docs>.

## Abrir la interfaz

Deja el servidor ejecutándose y abre `index.html` en tu navegador. Puedes hacerlo desde el explorador de archivos.
