# DocuMind 🧠

> **Asistente RAG (Retrieval-Augmented Generation) de alto rendimiento para consultas sobre colecciones de PDFs.**  
> Arquitectura **Lean** y modular — sin sobreingeniería, máxima reutilización.

---

## ✨ ¿Qué es DocuMind?

DocuMind es un sistema de inteligencia artificial local que permite consultar colecciones de documentos PDF usando lenguaje natural. Funciona completamente **offline** gracias a [Ollama](https://ollama.com/), sin enviar tus datos a ningún servidor externo.

Ideal para equipos técnicos que trabajan con documentación masiva de:
- ☁️ **AWS** — Cloud & AI
- 🐧 **Debian** — Administración de sistemas
- 🌐 **Cisco** — Redes y networking

---

## 🏗️ Arquitectura Lean

DocuMind centraliza su inteligencia en un motor core reutilizable y usa **Super-Skills paramétricas** para evitar la fragmentación de plugins.

```
DocuMind/
├── core/
│   └── engine.py              # Motor central: ingesta, retrieval y QA
├── skills/
│   └── knowledge_engine/
│       ├── handler.py         # Super-Skill: search, ingest (paramétrico)
│       └── manifest.yaml      # Descriptor de la skill
├── docs/
│   ├── agent.md               # Documentación del agente
│   └── skills.md              # Guía de extensibilidad con Skills
├── tests/                     # Suite de tests (pytest)
├── rag_terminal.py            # Interfaz TUI (Thin UI) con Rich
├── Dockerfile                 # Contenedor listo para producción
├── requirements.txt           # Dependencias Python
└── .env.example               # Variables de entorno de ejemplo
```

### Componentes clave

| Componente | Rol |
|---|---|
| `core/engine.py` | Motor centralizado. Gestiona múltiples bibliotecas, auto-ingesta y retrieval con ChromaDB. |
| `rag_terminal.py` | Interfaz de usuario en terminal (TUI) con menú interactivo y spinners. |
| `skills/knowledge_engine` | Super-Skill paramétrica. Consolida búsqueda e ingesta en un solo componente reutilizable. |

---

## 🛠️ Instalación

### Requisitos previos

- Python 3.11+
- [Ollama](https://ollama.com/) instalado y en ejecución
- Modelos descargados:

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

### Setup del proyecto

```bash
# 1. Clonar el repositorio
git clone https://github.com/Medalcode/DocuMind.git
cd DocuMind

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows PowerShell

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (opcional)
cp .env.example .env
```

---

## 📖 Uso

### Interfaz de Terminal (TUI)

```bash
python rag_terminal.py
```

Al iniciar, el sistema realiza **auto-ingesta** automática: detecta y procesa cualquier PDF nuevo en las carpetas `data/` de cada biblioteca.

Luego se presenta el menú interactivo:

```
┌──────────────────────────────────────────────────────┐
│     Seleccione el cerebro de IA que desea consultar  │
└──────────────────────────────────────────────────────┘
 ID  Especialidad
 1   AWS Cloud & AI
 2   Debian SysAdmin
 3   Cisco Networking
```

Escribe `volver` en cualquier consulta para regresar al menú principal.

### Estructura de datos

Coloca tus PDFs en las carpetas correspondientes:

```
data/
├── aws/      → Documentación AWS, guías de certificación, whitepapers
├── debian/   → Manuales Debian, páginas man, guías de administración
└── cisco/    → Documentación Cisco, guías de laboratorio, RFCs
```

Los PDFs son indexados automáticamente en la primera ejecución. Los re-inicios posteriores solo procesan archivos **nuevos**.

---

## 🧩 Extensibilidad (Skills)

La arquitectura de **Super-Skills** permite extender DocuMind sin crear plugins redundantes.  
La `knowledge_engine` acepta acciones como `search` e `ingest` mediante parámetros:

```python
# Ejemplo de uso de la skill
from skills.knowledge_engine.handler import run

# Buscar en una biblioteca
result = run(action="search", library_id=1, query="¿Cómo funciona S3?")

# Ingestar un nuevo PDF
result = run(action="ingest", library_id=2, file_path="./data/debian/nuevo.pdf")
```

Consulta [`docs/skills.md`](docs/skills.md) para la guía completa de extensibilidad.

---

## 🧪 Tests

```bash
# Ejecutar toda la suite de tests
pytest -v

# Solo tests de ingesta
pytest tests/test_ingestion.py -v

# Solo tests de la skill handler
pytest tests/test_skill_handler.py -v
```

La suite incluye tests unitarios e integración para el motor de ingesta y el handler de Skills.

---

## 🐳 Docker

```bash
# Construir la imagen
docker build -t documind .

# Ejecutar con volumen de datos local
docker run --rm -it \
  -v ${PWD}/data:/app/data \
  -v ${PWD}/db_aws:/app/db_aws \
  -v ${PWD}/db_debian:/app/db_debian \
  -v ${PWD}/db_cisco:/app/db_cisco \
  documind
```

> **Nota:** Ollama debe estar accesible desde el contenedor. Usa `--network host` si Ollama corre localmente en el host.

---

## ⚙️ CI/CD

El proyecto incluye un workflow de GitHub Actions (`.github/workflows/ci.yml`) que ejecuta automáticamente la suite de tests en cada push o Pull Request a `main`.

---

## 🔧 Stack Tecnológico

| Herramienta | Uso |
|---|---|
| [LangChain](https://python.langchain.com/) | Orquestación de cadenas RAG |
| [Ollama](https://ollama.com/) | Inferencia local de LLMs |
| [ChromaDB](https://www.trychroma.com/) | Vector store para embeddings |
| [Rich](https://github.com/Textualize/rich) | Interfaz TUI en terminal |
| [PyPDF](https://github.com/py-pdf/pypdf) | Carga y parseo de PDFs |
| [pytest](https://pytest.org/) | Testing |

---

## 📜 Licencia

Este proyecto sigue los principios de **Agentes de IA Generalistas**: mínimo mantenimiento, máxima reutilización del código.

MIT License — Medalcode © 2026
