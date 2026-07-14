[![CI](https://github.com/Medalcode/DocuMind/actions/workflows/ci.yml/badge.svg)](https://github.com/Medalcode/DocuMind/actions/workflows/ci.yml)

# DocuMind 🧠

> **Plataforma de Gestión de Conocimiento e Inferencia basada en RAG (Retrieval-Augmented Generation).**  
> Diseñada con una arquitectura modular (React/FastAPI) y soporte para múltiples proveedores de IA, enfocada en la trazabilidad y la observabilidad del ciclo de vida del documento.

---

## ✨ Características Técnicas (v2.0)

- 🏗️ **Arquitectura Desacoplada:** Frontend SPA en React + Vite y un Backend robusto en FastAPI.
- 🖥️ **Interfaz Web Moderna (SPA):** Diseñada en React + Vite, con estética *Glassmorphism* y un diseño premium.
- 🤖 **Soporte Multi-IA:** Integración flexible con Ollama, OpenAI, Groq y Gemini.
- 📁 **Gestión Visual de Cerebros:** Crea y gestiona distintos "Cerebros de IA" (Espacios de nombres) directamente desde la interfaz.
- 📎 **Soporte Multimodal de Documentos (Sprint 3):** Sube archivos `.pdf`, `.docx` (Word), `.md` (Markdown) y `.txt`. La interfaz los procesa de forma agnóstica.
- 🌐 **Conector Web Inteligente (Sprint 4):** Pega cualquier URL (documentación, Wikipedia, artículos, o código raw de GitHub) y DocuMind hará web scraping en tiempo real, extraerá el texto limpio y lo integrará a tu base de conocimientos con un solo clic.
- 🔄 **Control de Versiones y Sincronización:** Si subes una versión actualizada de un documento existente, DocuMind detecta la nueva fecha de modificación, elimina los vectores obsoletos y reindexa el nuevo contenido automáticamente.
- ⚡ **Embeddings Nativos Optimizados:** Uso de `HuggingFaceEmbeddings` ejecutándose nativamente en CPU.

---

## 🔬 Decisiones de Arquitectura y Pipeline RAG

### 1. ¿Por qué ChromaDB + HuggingFace?
La combinación de **Chroma** como vectorstore local persistente junto con **HuggingFaceEmbeddings** permite indexar miles de páginas de PDFs en hardware de consumo sin saturar la memoria gráfica. Si usáramos embeddings del LLM local (ej. Ollama), el proceso competiría por recursos con el motor de inferencia.

### 2. Estrategia de Chunking
Se utiliza `RecursiveCharacterTextSplitter` con un `chunk_size` de 1200 caracteres y un `chunk_overlap` de 200. Esto asegura que el contexto semántico no se pierda en los límites de los párrafos, mejorando significativamente la precisión de la recuperación.

### 3. Historial y Memoria Conversacional
El frontend envía al backend el historial de mensajes recientes (ventana deslizante), el cual es formateado y entregado al LLM junto con los chunks recuperados. Esto permite preguntas de seguimiento y referencias a interacciones pasadas en la misma sesión.

### 4. Observabilidad y Métricas (Sprint 1)
El sistema ha migrado de ser una "caja negra" a proveer diagnóstico interno:
- **Trazabilidad de Tiempos:** Se mide de manera independiente el tiempo de recuperación (`retrieval_time_sec`) y el tiempo de inferencia (`generation_time_sec`).
- **Citaciones Detalladas:** Las respuestas incluyen evidencia explícita: documento de origen, número de página, fragmento de texto original (snippet) y su Score de Similitud (L2 distance).
- **Logging Persistente y Dashboard (Sprint 2):** Todas las consultas se registran en `backend/logs/chat_logs.jsonl`. La interfaz web incluye un "Panel de Diagnóstico" para visualizar promedios globales e historial de latencias.

### 5. Evaluación Automatizada (LLM-as-a-Judge)
Para evitar el sesgo de "parece que funciona", DocuMind incorpora una suite de *benchmarking* automatizado:
- **`backend/benchmark_dataset.json`**: Un dataset estándar de preguntas y respuestas esperadas.
- **`evaluate.py`**: Un script que ejecuta el pipeline RAG completo sobre el dataset y utiliza un LLM Juez para calcular la precisión semántica (Score 1 al 5) de las respuestas generadas, generando un reporte detallado de rendimiento y precisión.

---

## 🏗️ Arquitectura Cliente-Servidor

```
DocuMind/
├── frontend/                  # Interfaz gráfica moderna (React, Vite, Lucide Icons)
│   ├── src/
│   │   ├── App.jsx            # Lógica principal del chat y UI
│   │   └── index.css          # Estilos premium (Glassmorphism, animaciones)
├── backend/                   # Servidor API de alto rendimiento
│   ├── core/
│   │   └── engine.py          # Motor central (Langchain, ChromaDB, HuggingFace)
│   ├── main.py                # Endpoints FastAPI (/chat, /libraries, /upload)
│   └── config.yaml            # Configuración dinámica de los cerebros
├── data/                      # Donde se guardan físicamente tus PDFs
├── db/                        # Base de datos vectorial persistente (ChromaDB)
├── skills/                    # Módulo de skills del sistema
├── tests/                     # Test suite (conftest, ingestion, skill_handler)
├── graphify-out/              # Knowledge graph (57 nodos, 56 aristas)
├── .agents/                   # skills.sh skills (tdd)
├── requirements.txt           # Dependencias de Python
```

---

## 🛠️ Instalación y Uso

### 1. Requisitos Previos
- Python 3.11+
- Node.js y npm (para el frontend)

### 2. Configurar el Backend (FastAPI)
Abre tu terminal en la carpeta principal del proyecto:

```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt

# Iniciar el servidor
uvicorn backend.main:app --reload --port 8000
```

### 3. Configurar el Frontend (React)
Abre **otra ventana** de terminal y navega a la carpeta frontend:

```bash
cd frontend

# Instalar dependencias (solo la primera vez)
npm install

# Iniciar el servidor web
npm run dev
```

### 4. Ejecutar Pruebas de Calidad RAG (Opcional)
Para evaluar la precisión del motor de forma automatizada:
```bash
# Desde la raíz del proyecto
python backend/evaluate.py
```

### 4. A disfrutar 🚀
Abre tu navegador en `http://localhost:5173`. 
Puedes crear un "Cerebro" nuevo, hacer clic en el 📎 para subir un PDF y empezar a conversar inmediatamente. En la tuerca de configuración (⚙️) puedes poner tu API Key de OpenAI, Gemini o Groq y cambiar el modelo al instante.

---

## Knowledge Graph

`graphify-out/graph.json` contiene **57 nodos y 56 aristas** del AST del proyecto, permitiendo a agentes AI comprender la arquitectura sin escanear archivos.

## Skills

- **tdd** (skills.sh) — patrones de testing para mantener y expandir la cobertura

## 🧪 Tests y Extensibilidad

La arquitectura base soporta la integración con la suite original de Super-Skills.
```bash
# Ejecutar tests
pytest -v
```

---

## 📜 Licencia

MIT License — Medalcode © 2025
