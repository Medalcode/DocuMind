import os
import time
import logging
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import yaml

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger("DocuMindEngine")

class CustomQAChain:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.prompt = PromptTemplate.from_template(
            "Use the following pieces of context to answer the question at the end.\n"
            "If you don't know the answer, just say that you don't know, don't try to make up an answer.\n\n"
            "Context: {context}\n\n"
            "Question: {question}\n\n"
            "Helpful Answer:"
        )
    
    def invoke(self, query):
        docs = self.retriever.invoke(query)
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt_val = self.prompt.format(context=context, question=query)
        res = self.llm.invoke(prompt_val)
        return {
            "result": res.content,
            "source_documents": docs
        }

class DocuMindEngine:
    def __init__(self, config_path="backend/config.yaml", embed_model="all-MiniLM-L6-v2"):
        self.LIBRARIES = self._load_config(config_path)
        self.embed_model = embed_model
        # Usamos HuggingFaceEmbeddings para no depender de que Ollama esté corriendo localmente.
        self.embeddings = HuggingFaceEmbeddings(model_name=embed_model)

    def _load_config(self, config_path):
        if not os.path.exists(config_path):
            return {}
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            return config.get("libraries", {}) if config else {}

    def _save_config(self, config_path="backend/config.yaml"):
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        config["libraries"] = self.LIBRARIES
        with open(config_path, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

    def add_library(self, name: str, folder_name: str, config_path="backend/config.yaml"):
        new_id = 1
        if self.LIBRARIES:
            new_id = max(int(k) for k in self.LIBRARIES.keys()) + 1
            
        data_dir = f"data/{folder_name}"
        db_dir = f"db/{folder_name}"
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(db_dir, exist_ok=True)
        
        self.LIBRARIES[new_id] = {
            "name": name,
            "data": data_dir,
            "db": db_dir
        }
        self._save_config(config_path)
        return {"id": new_id, "name": name}

    def delete_library(self, lib_id: int, config_path="backend/config.yaml"):
        if lib_id in self.LIBRARIES:
            del self.LIBRARIES[lib_id]
            self._save_config(config_path)
            return True
        return False

    def _listar_pdfs(self, ruta):
        if not os.path.exists(ruta):
            return []
        return [f for f in os.listdir(ruta) if f.lower().endswith(".pdf")]

    def _listar_indexados(self, db_path):
        index_file = os.path.join(db_path, "indexed_files.txt")
        if not os.path.exists(index_file):
            return set()
        with open(index_file, "r") as f:
            return set(line.strip() for line in f)

    def _registrar_indexado(self, db_path, filename):
        index_file = os.path.join(db_path, "indexed_files.txt")
        with open(index_file, "a") as f:
            f.write(filename + "\n")

    def auto_ingesta(self):
        """Procesa archivos nuevos en todas las bibliotecas."""
        for key, paths in self.LIBRARIES.items():
            data_dir = paths["data"]
            db_dir = paths["db"]
            os.makedirs(db_dir, exist_ok=True)
            
            pdfs = self._listar_pdfs(data_dir)
            indexados = self._listar_indexados(db_dir)
            nuevos = [pdf for pdf in pdfs if pdf not in indexados]
            
            if not nuevos:
                continue
                
            logger.info(f"Ingestando {len(nuevos)} PDF(s) en {paths['name']}...")
            for pdf in nuevos:
                try:
                    loader = PyPDFLoader(os.path.join(data_dir, pdf))
                    docs = loader.load()
                    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
                    chunks = splitter.split_documents(docs)
                    Chroma.from_documents(
                        documents=chunks,
                        embedding=self.embeddings,
                        persist_directory=db_dir
                    )
                    self._registrar_indexado(db_dir, pdf)
                    logger.info(f"OK: {pdf}")
                except Exception as e:
                    logger.error(f"Error indexando {pdf}: {str(e)}. Saltando archivo y continuando...")

    def get_qa_chain(self, lib_id, provider="ollama", model_name="llama3.1", api_key=None):
        if lib_id not in self.LIBRARIES:
            return None
            
        db_path = self.LIBRARIES[lib_id]["db"]
        if not os.path.exists(db_path):
            return None
            
        vectorstore = Chroma(persist_directory=db_path, embedding_function=self.embeddings)
        
        if provider == "openai":
            llm = ChatOpenAI(model_name=model_name, temperature=0.1, api_key=api_key)
        elif provider == "gemini":
            llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.1, google_api_key=api_key)
        elif provider == "groq":
            llm = ChatGroq(model_name=model_name, temperature=0.1, api_key=api_key)
        else:
            llm = ChatOllama(model=model_name, temperature=0.1)
        
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        return CustomQAChain(llm, retriever)
