FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DATA_ROOT=/app/data
ENV CHROMA_DIR=/app/db
CMD ["python", "rag_terminal.py"]
