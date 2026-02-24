# DocuMind

Asistente RAG (Retrieval-Augmented Generation) de alto rendimiento para consultas sobre colecciones de PDFs, diseñado con una arquitectura **Lean** y modular.

## 🚀 Arquitectura "Lean"

DocuMind ha sido refactorizado para eliminar la fragmentación y la sobreingeniería, centralizando su inteligencia en un motor core y utilizando Super-Skills paramétricas.

- **`core/engine.py`**: Motor centralizado que gestiona múltiples bibliotecas (AWS, Debian, Cisco), la ingesta y el retrieval.
- **`rag_terminal.py`**: Interfaz de usuario optimizada (Thin UI) que interactúa con el motor central.
- **`skills/knowledge_engine`**: Super-Skill paramétrica que consolida búsqueda, resumen e ingesta en un solo componente.

## 🛠️ Instalación

1. **Entorno Virtual (Windows PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Requisitos de Modelos (Ollama):**
   Asegúrate de tener [Ollama](https://ollama.com/) instalado y los modelos descargados:
   ```bash
   ollama pull llama3.1
   ollama pull nomic-embed-text
   ```

## 📖 Uso

### Interfaz del Terminal
Ejecuta la interfaz interactiva para consultar cualquiera de las bases de conocimiento:
```powershell
python rag_terminal.py
```
*El sistema detectará automáticamente nuevos PDFs en la carpeta `data/` al iniciar.*

### Extensibilidad (Skills)
Para extender la funcionalidad, usa la arquitectura de **Super-Skills**. La `knowledge_engine` acepta acciones como `search` e `ingest` mediante parámetros, evitando la creación de múltiples plugins redundantes.

## 🧪 Desarrollo y Pruebas

Ejecutar la suite de tests unitarios e integración:
```powershell
pytest -v
```

## 🐳 Docker
```bash
docker build -t documind .
docker run --rm -it -v ${PWD}/data:/app/data documind
```

## 📜 Licencia e Información
Este proyecto sigue los principios de **Agentes de IA Generalistas** para minimizar el mantenimiento y maximizar la reutilización del código.
