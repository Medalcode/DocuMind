# Bitácora de desarrollo

## Tareas realizadas

- Crear estructura de carpetas para bibliotecas y bases de datos (data/aws, data/debian, data/cisco, db_aws, db_debian, db_cisco)
- Crear script de auto-ingesta de PDFs nuevos (auto_ingesta.py)
- Integrar auto-ingesta al script principal de consola (rag_terminal.py)
- Agregar instrucciones de uso y ejecución al README

## Tareas pendientes

- Mejorar la gestión de errores y mensajes amigables en la interfaz
- Añadir historial de consultas por usuario
- Permitir selección dinámica de modelos Ollama
- Implementar soporte para otros tipos de documentos (Markdown, TXT)
- Agregar tests automáticos y documentación técnica avanzada
# Instrucciones para ejecutar tu asistente RAG local

1. Instala las dependencias necesarias (si no lo has hecho):

```
pip install langchain langchain-community langchain-ollama chromadb pypdf rich
```

2. Asegúrate de tener Ollama instalado y los modelos descargados:

```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1
ollama pull nomic-embed-text
```

3. Coloca tus archivos PDF en las carpetas:
	- data/aws/
	- data/debian/
	- data/cisco/

4. Ejecuta el asistente desde la terminal:

```
python rag_terminal.py
```

El sistema indexará automáticamente los nuevos PDFs y te permitirá consultar cada biblioteca desde una interfaz profesional en la terminal.

---

¿Dudas o problemas? Revisa los mensajes de error en la terminal o consulta el código fuente para personalizarlo a tus necesidades.
# DocuMind