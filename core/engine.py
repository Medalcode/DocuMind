import os
import time
import logging
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger("DocuMindEngine")

class DocuMindEngine:
    LIBRARIES = {
        1: {"name": "AWS Cloud & AI", "data": "./data/aws", "db": "./db_aws"},
        2: {"name": "Debian SysAdmin", "data": "./data/debian", "db": "./db_debian"},
        3: {"name": "Cisco Networking", "data": "./data/cisco", "db": "./db_cisco"}
    }

    def __init__(self, model_name="llama3.1", embed_model="nomic-embed-text"):
        self.model_name = model_name
        self.embed_model = embed_model
        self.embeddings = OllamaEmbeddings(model=embed_model)

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
                    logger.error(f"Error indexando {pdf}: {e}")

    def get_qa_chain(self, lib_id):
        if lib_id not in self.LIBRARIES:
            return None
            
        db_path = self.LIBRARIES[lib_id]["db"]
        if not os.path.exists(db_path):
            return None
            
        vectorstore = Chroma(persist_directory=db_path, embedding_function=self.embeddings)
        llm = ChatOllama(model=self.model_name, temperature=0.1)
        
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
