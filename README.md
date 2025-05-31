[![CI](https://github.com/Medalcode/DocuMind/actions/workflows/ci.yml/badge.svg)](https://github.com/Medalcode/DocuMind/actions/workflows/ci.yml)

# DocuMind 🧠

> **Asistente RAG (Retrieval-Augmented Generation) de alto rendimiento para consultas sobre colecciones de PDFs.**  
> Ahora con una arquitectura Web Moderna, soporte Multi-IA y gestión de documentos desde el navegador.

---

## ✨ ¿Qué es DocuMind?

DocuMind es un sistema RAG (Retrieval-Augmented Generation) avanzado que te permite conversar con tus documentos PDF usando Inteligencia Artificial. Ya sea para estudiar certificaciones técnicas, buscar en manuales o leer reportes extensos, DocuMind funciona como tu "Cerebro" personal.

### 🌟 Nuevas Características (v2.0)
- 🖥️ **Interfaz Web Moderna (SPA):** Diseñada en React + Vite, con estética *Glassmorphism* y un diseño premium. Olvídate de la terminal.
- 🤖 **Soporte Multi-IA:** No estás limitado a un solo motor. Puedes usar:
  - **Ollama (Local)**: Privacidad absoluta y 100% offline.
  - **Groq**: Inferencia ultrarrápida usando Llama 3.1.
  - **OpenAI (GPT-4o)**: Toda la potencia de ChatGPT.
  - **Google Gemini**: Excelente rendimiento y contexto amplio.
  - *(Auto-detección inteligente de API Keys integrada en la interfaz).*
- 📁 **Gestión Visual de Cerebros:** Crea, elimina y gestiona distintos "Cerebros de IA" directamente desde la interfaz, sin tocar archivos de código.
- 📎 **Subida de PDFs Integrada:** Selecciona tus PDFs desde la interfaz y se subirán e indexarán automáticamente en segundo plano.
- ⚡ **Embeddings Nativos:** Desacoplamos la indexación usando `HuggingFaceEmbeddings`, permitiendo crear la base de datos vectorial de forma ultrarrápida y 100% local en CPU, sin necesidad de tener un LLM local corriendo para este proceso.

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

### 4. A disfrutar 🚀
Abre tu navegador en `http://localhost:5173`. 
Puedes crear un "Cerebro" nuevo, hacer clic en el 📎 para subir un PDF y empezar a conversar inmediatamente. En la tuerca de configuración (⚙️) puedes poner tu API Key de OpenAI, Gemini o Groq y cambiar el modelo al instante.

---

## 🧪 Tests y Extensibilidad

La arquitectura base soporta la integración con la suite original de Super-Skills.
```bash
# Ejecutar tests
pytest -v
```

---

## 📜 Licencia

MIT License — Medalcode © 2025
