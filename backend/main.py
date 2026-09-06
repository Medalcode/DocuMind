import json
import os
import shutil

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.core.engine import DocuMindEngine

app = FastAPI(title="DocuMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = DocuMindEngine()

class ChatRequest(BaseModel):
    query: str
    library_id: int
    provider: str = "ollama"  # ollama, openai, gemini, groq
    model_name: str = "llama3.1"
    api_key: str = None
    chat_history: list[dict] = []

class LibraryCreateRequest(BaseModel):
    name: str
    folder_name: str

class UrlRequest(BaseModel):
    url: str

@app.get("/libraries")
def get_libraries():
    return [{"id": k, "name": v["name"]} for k, v in engine.LIBRARIES.items()]

@app.post("/libraries")
def create_library(request: LibraryCreateRequest):
    res = engine.add_library(request.name, request.folder_name)
    return res

@app.delete("/libraries/{lib_id}")
def delete_library(lib_id: int):
    success = engine.delete_library(lib_id)
    if not success:
        raise HTTPException(status_code=404, detail="Library not found")
    return {"message": "Deleted successfully"}

@app.post("/libraries/{lib_id}/upload")
async def upload_files(lib_id: int, files: list[UploadFile] = File(...)):
    if lib_id not in engine.LIBRARIES:
        raise HTTPException(status_code=404, detail="Library not found")

    data_dir = engine.LIBRARIES[lib_id]["data"]
    os.makedirs(data_dir, exist_ok=True)

    saved_files = []
    for file in files:
        if file.filename.lower().endswith(('.pdf', '.docx', '.txt', '.md')):
            file_path = os.path.join(data_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file.filename)

    return {"message": "Files uploaded successfully", "files": saved_files}

@app.post("/ingest")
def trigger_ingest():
    engine.auto_ingesta()
    return {"message": "Ingesta completada"}

@app.post("/libraries/{lib_id}/url")
async def ingest_url(lib_id: str, payload: UrlRequest):
    if lib_id not in engine.LIBRARIES:
        raise HTTPException(status_code=404, detail="Librería no encontrada")

    success, msg = engine.ingestar_url(lib_id, payload.url)
    if not success:
        raise HTTPException(status_code=500, detail=msg)

    return {"message": msg}

@app.post("/chat")
def chat(request: ChatRequest):
    chain = engine.get_qa_chain(
        lib_id=request.library_id,
        provider=request.provider,
        model_name=request.model_name,
        api_key=request.api_key
    )
    if not chain:
        raise HTTPException(status_code=404, detail="Library not found or config error")

    res = chain.invoke(request.query, request.chat_history)

    return {
        "result": res["result"],
        "sources": res.get("detailed_sources", []),
        "metrics": res.get("metrics", {})
    }

@app.get("/logs")
def get_logs(limit: int = 50):
    log_file = "backend/logs/chat_logs.jsonl"
    if not os.path.exists(log_file):
        return []

    logs = []
    with open(log_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))

    # Devolver los últimos X logs invertidos (más recientes primero)
    return logs[-limit:][::-1]

@app.get("/stats")
def get_stats():
    log_file = "backend/logs/chat_logs.jsonl"
    if not os.path.exists(log_file):
        return {
            "total_queries": 0,
            "avg_retrieval_time": 0.0,
            "avg_generation_time": 0.0,
            "avg_total_time": 0.0
        }

    total_q = 0
    sum_retrieval = 0
    sum_gen = 0
    sum_total = 0

    with open(log_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line)
                    m = entry.get("metrics", {})
                    total_q += 1
                    sum_retrieval += m.get("retrieval_time_sec", 0)
                    sum_gen += m.get("generation_time_sec", 0)
                    sum_total += m.get("total_time_sec", 0)
                except Exception:
                    pass

    if total_q == 0:
        return {"total_queries": 0, "avg_retrieval_time": 0, "avg_generation_time": 0, "avg_total_time": 0}

    return {
        "total_queries": total_q,
        "avg_retrieval_time": round(sum_retrieval / total_q, 3),
        "avg_generation_time": round(sum_gen / total_q, 3),
        "avg_total_time": round(sum_total / total_q, 3)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
