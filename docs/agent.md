## Resumen arquitectural

Este documento describe la arquitectura del agente RAG del proyecto, sus componentes y las operaciones necesarias para su despliegue y escalado.

- Componentes clave: ingesta (PDF -> chunks), vectorstore (Chroma), embeddings, LLM (Ollama), capa de orquestación/skills y UI (terminal o servicio HTTP).
- Flujo de datos: PDFs -> KnowledgeEngine (Skill) -> Chroma persistente -> DocuMindGeneralist (Agente) realiza retrieval + LLM.

## Agente Generalista (DocuMindGeneralist)

Para evitar la fragmentación, el sistema utiliza un único **Agente Generalista** capaz de conmutar entre diferentes contextos de conocimiento (AWS, Debian, Cisco) mediante parámetros en lugar de tener agentes especializados redundantes.

- **Rol**: Orquestador universal de consultas RAG.
- **Capacidades**: Selección de corpus dinámica, auto-ingesta bajo demanda y validación de fuentes.
- **Ventaja**: Reduce el mantenimiento de lógica duplicada en un 80%.


## Requisitos y dependencias

- Ver `requirements.txt` para las dependencias Python.
- Requisitos externos: Ollama instalado y corriendo localmente, modelos descargados (ej. `llama3.1`, `nomic-embed-text`).
- Espacio en disco suficiente para índices y documentos (depende de corpus).

## Variables de entorno y configuración

Se recomienda usar un fichero `.env` y no almacenar secretos en el repo. Variables mínimas (ver `.env.example`):

- `OLLAMA_HOST`: URL del servicio Ollama (ej. `http://localhost:11434`).
- `LLM_MODEL`: nombre del modelo para generación (ej. `llama3.1`).
- `EMBED_MODEL`: modelo de embeddings (ej. `nomic-embed-text`).
- `DATA_ROOT`: ruta base donde están los PDF y datos (ej. `./data`).
- `CHROMA_DIR`: directorio de persistencia de Chroma (ej. `./db`).

Prioridad de configuración: variables de entorno > fichero de configuración > valores por defecto.

## Ingesta y persistencia

- `auto_ingesta.py` realiza:
  - lectura de PDFs
  - chunking (p. ej. RecursiveCharacterTextSplitter)
  - creación/actualización de índice Chroma
  - registro de archivos indexados (`indexed_files.txt`)

- Recomendaciones:
  - Proteger actualizaciones concurrentes con `filelock` durante la escritura del índice.
  - Evitar recargar toda la base en memoria en entorno multiusuario; usar namespaces o particiones por biblioteca.
  - Mantener registro de metadatos (hash de archivo, timestamp) para reindexaciones idempotentes.

## Despliegue y operaciones

- Modo local: ejecutar Ollama y usar `rag_terminal.py` para consultas ad-hoc.
- Docker: construir imagen con `Dockerfile` incluido y ejecutar contenedor para entornos reproducibles.
- Backup/restore: mantener copias periódicas del directorio `CHROMA_DIR` y de `indexed_files.txt`.

Ejemplo rápido (local):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python rag_terminal.py
```

## Observabilidad

- Logging: usar `logging_config.py` para logging estructurado. Registrar latencias de RAG (retrieval + generación).
- Métricas mínimas: QPS, latencia promedio, errores por endpoint, tamaño del índice.
- Tracing: si se usa en producción, propagar IDs de correlación en la pipeline (retrieval → LLM).

## Seguridad y secretos

- No incluir claves ni secretos en el repositorio. Usar `dotenv` o secret store en CI/CD.
- Restringir permisos de archivos que contienen índices y datos.

## Testing y CI

- Añadir tests unitarios para la ingesta (mock de archivos), y tests de integración para el flujo retrieval+LLM (mocks del LLM).
- Pipeline CI (GitHub Actions) debe instalar dependencias y ejecutar `pytest`.

## Checklist de mejoras futuras

- Soporte asíncrono/worker para ingesta masiva (Celery/RQ/asyncio).
- Servicio compartido para embeddings (si se distribuye en múltiples instancias).
- Monitoreo con Prometheus + alertas.
- Seguridad avanzada: cifrado en reposo para índices sensibles.
