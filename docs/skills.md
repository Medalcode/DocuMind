## ¿Qué es una skill?

Una *skill* es una unidad funcional autocontenida que expone una responsabilidad concreta (p. ej. búsqueda en PDFs, resumen, ejecución de acciones). Las skills deben tener un contrato claro de entrada/salida y ser detectables por el agente.

## Estructura recomendada de `skills/`

- `skills/{skill_name}/manifest.yaml` — metadata y contrato.
- `skills/{skill_name}/handler.py` — implementa `handle(input: dict) -> dict`.
- `skills/{skill_name}/tests/` — pruebas unitarias de la skill.

## Super-Skills Paramétricas (Recomendado)

En lugar de crear múltiples skills para tareas similares, se deben consolidar en **Super-Skills** que reciben un parámetro `action` o `task`. Esto maximiza la reutilización de la lógica de conexión a bases de datos y LLMs.

### Skill: KnowledgeEngine

Consolida: `pdf_finder`, `pdf_summarizer`, `data_ingestor`.

```yaml
name: knowledge_engine
version: 1.0
description: Motor universal para gestión de conocimiento (RAG + Ingesta)
entrypoint: handler.py
inputs:
  - action: enum [search, summarize, ingest]
  - corpus: str (ej. "aws", "debian")
  - query: str (opcional para ingest)
outputs:
  - result: str
  - metadata: dict
permissions:
  - read: data
  - write: vectorstore
```


## Registro y descubrimiento

- El agente puede descubrir skills buscando `skills/*/manifest.yaml`.
- El manifest indica el `entrypoint` relativo. El agente debe importar el módulo y llamar `handle()`.

## Interfaz de invocación

- Handler: `def handle(input: dict) -> dict`.
- Convención de respuesta: `{'answer': str, 'sources': List[dict]}` donde cada fuente tiene al menos `{'id', 'score', 'cursor'}`.

## Ejemplo de skill simple

- `handler.py` mínimo que devuelve respuesta y fuentes.

## Buenas prácticas

- Validar inputs y retornar errores claros.
- Implementar timeouts y límites de recursos.
- Ser idempotente cuando aplique.
- Incluir tests unitarios y mocks del LLM/vectorstore.

## Seguridad

- Declarar permisos en `manifest.yaml` y validar antes de ejecutar.
- Evitar que las skills carguen secretos desde el repo.
