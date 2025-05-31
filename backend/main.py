from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from backend.core.engine import DocuMindEngine
import os
import shutil

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

class LibraryCreateRequest(BaseModel):
    name: str
    folder_name: str

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
async def upload_files(lib_id: int, files: List[UploadFile] = File(...)):
    if lib_id not in engine.LIBRARIES:
        raise HTTPException(status_code=404, detail="Library not found")
        
    data_dir = engine.LIBRARIES[lib_id]["data"]
    os.makedirs(data_dir, exist_ok=True)
    
    saved_files = []
    for file in files:
        if file.filename.lower().endswith('.pdf'):
            file_path = os.path.join(data_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file.filename)
            
    return {"message": "Files uploaded successfully", "files": saved_files}

@app.post("/ingest")
def trigger_ingest(background_tasks: BackgroundTasks):
    background_tasks.add_task(engine.auto_ingesta)
    return {"message": "Ingesta iniciada en background"}

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
    
    res = chain.invoke(request.query)
    sources = list(set([str(doc.metadata.get('page', '?')) for doc in res['source_documents']]))
    return {
        "result": res["result"],
        "sources": sources
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
