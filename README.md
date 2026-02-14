# DocuMind

Proyecto asistente RAG (Retrieval-Augmented Generation) para consultas sobre colecciones de PDFs.

## Resumen rápido

Este repositorio contiene herramientas para:

- Indexar PDFs en un vectorstore persistente (Chroma) mediante `auto_ingesta.py`.
- Realizar consultas RAG usando un LLM local vía Ollama con `rag_terminal.py`.
- Extender funcionalidad mediante `skills/` (plugins que exponen handlers y manifests).

## Instalación (entorno virtual)

1. Crear y activar un entorno virtual (Windows PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. (Opcional) Configurar variables de entorno copiando el ejemplo:

```powershell
copy .env.example .env
# editar .env según sea necesario
```

## Requisitos externos

- Ollama (modelo LLM local). Instalar y descargar modelos según necesites:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1
ollama pull nomic-embed-text
```

## Uso básico

1. Coloca tus PDFs en subcarpetas bajo la carpeta `data/`, por ejemplo `data/aws`.
2. Indexa documentos (opcional, `rag_terminal.py` puede iniciar ingesta automática):

```powershell
python auto_ingesta.py
```

3. Ejecuta la interfaz de consulta:

```powershell
python rag_terminal.py
```

## Desarrollo y pruebas

- Ejecutar tests:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

- Recomendación: usar `.venv` local y no commitearla (ya incluida en `.gitignore`).

## Docker (opcional)

Construir y ejecutar la imagen:

```bash
docker build -t documind .
docker run --rm -it -v $(pwd)/data:/app/data documind
```

## Contribuir

Para añadir una `skill`, crea una carpeta `skills/{nombre}/` con `manifest.yaml` y `handler.py` que implemente `handle(input: dict) -> dict`.

## Soporte

Si tienes problemas, abre un issue en el repositorio o revisa los archivos `auto_ingesta.py` y `rag_terminal.py` para entender los parámetros y el flujo.
