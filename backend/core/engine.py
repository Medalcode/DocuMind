import json
import logging
import os
import time
from datetime import datetime

import yaml
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    WebBaseLoader,
)
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger("DocuMindEngine")


class CustomQAChain:
    def __init__(self, llm, vectorstore):
        self.llm = llm
        self.vectorstore = vectorstore
        self.prompt = PromptTemplate.from_template(
            "Eres un asistente técnico útil y preciso. Usa el siguiente contexto (y el historial de chat si aplica) para responder a la pregunta del usuario.\n"
            "Si no sabes la respuesta, di claramente que no la sabes, no inventes información.\n\n"
            "Historial de Chat:\n{chat_history}\n\n"
            "Contexto recuperado:\n{context}\n\n"
            "Pregunta: {question}\n\n"
            "Respuesta:"
        )

    def invoke(self, query, chat_history_list=None):
        if chat_history_list is None:
            chat_history_list = []

        # Formatear el historial
        chat_history_str = ""
        for msg in chat_history_list:
            role = "Usuario" if msg.get("role") == "user" else "DocuMind"
            chat_history_str += f"{role}: {msg.get('text')}\n"

        # 1. Medir Retrieval
        t0 = time.time()
        docs_and_scores = self.vectorstore.similarity_search_with_score(query, k=3)
        retrieval_time = time.time() - t0

        # Preparar contexto y fuentes detalladas
        context_parts = []
        detailed_sources = []
        for doc, score in docs_and_scores:
            context_parts.append(doc.page_content)
            source_info = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)  # L2 distance en Chroma por defecto
            }
            detailed_sources.append(source_info)

        context = "\n\n".join(context_parts)

        # 2. Medir Generación
        prompt_val = self.prompt.format(
            chat_history=chat_history_str,
            context=context,
            question=query
        )
        t1 = time.time()
        res = self.llm.invoke(prompt_val)
        generation_time = time.time() - t1

        total_time = time.time() - t0

        metrics = {
            "retrieval_time_sec": round(retrieval_time, 3),
            "generation_time_sec": round(generation_time, 3),
            "total_time_sec": round(total_time, 3),
            "chunks_retrieved": len(docs_and_scores)
        }

        # Loggear internamente
        self._log_interaction(query, res.content, detailed_sources, metrics)

        return {
            "result": res.content,
            "detailed_sources": detailed_sources,
            "metrics": metrics
        }

    def _log_interaction(self, query, result, sources, metrics):
        try:
            log_dir = "backend/logs"
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "chat_logs.jsonl")

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "result": result,
                "metrics": metrics,
                "sources_summary": [
                    {
                        "source": s["metadata"].get("source", "Unknown"),
                        "page": s["metadata"].get("page", "?"),
                        "score": round(s["score"], 4)
                    } for s in sources
                ]
            }
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Error guardando logs: {e}")

class DocuMindEngine:
    def __init__(self, config_path="backend/config.yaml", embed_model="all-MiniLM-L6-v2"):
        self.LIBRARIES = self._load_config(config_path)
        self.embed_model = embed_model
        # Usamos HuggingFaceEmbeddings para no depender de que Ollama esté corriendo localmente.
        self.embeddings = HuggingFaceEmbeddings(model_name=embed_model)

    def _load_config(self, config_path):
        if not os.path.exists(config_path):
            return {}
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config.get("libraries", {}) if config else {}

    def _save_config(self, config_path="backend/config.yaml"):
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        config["libraries"] = self.LIBRARIES
        with open(config_path, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

    def add_library(self, name: str, folder_name: str, config_path="backend/config.yaml"):
        new_id = 1
        if self.LIBRARIES:
            new_id = max(int(k) for k in self.LIBRARIES) + 1

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

    def _listar_documentos(self, ruta):
        if not os.path.exists(ruta):
            return []
        valid_extensions = (".pdf", ".docx", ".txt", ".md")
        return [f for f in os.listdir(ruta) if f.lower().endswith(valid_extensions)]

    def _listar_indexados(self, db_path):
        index_file = os.path.join(db_path, "indexed_files.json")
        if not os.path.exists(index_file):
            return {}
        try:
            with open(index_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _registrar_indexados(self, db_path, index_dict):
        index_file = os.path.join(db_path, "indexed_files.json")
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_dict, f, ensure_ascii=False, indent=2)

    def _get_loader(self, file_path):
        ext = file_path.lower().split('.')[-1]
        if ext == 'pdf':
            return PyPDFLoader(file_path)
        elif ext == 'docx':
            return Docx2txtLoader(file_path)
        elif ext in ['txt', 'md']:
            return TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError(f"Extensión no soportada: {ext}")

    def auto_ingesta(self):
        """Procesa archivos nuevos o modificados en todas las bibliotecas."""
        for _key, paths in self.LIBRARIES.items():
            data_dir = paths["data"]
            db_dir = paths["db"]
            os.makedirs(db_dir, exist_ok=True)

            documentos = self._listar_documentos(data_dir)
            indexados = self._listar_indexados(db_dir)

            docs_a_procesar = []

            for doc in documentos:
                file_path = os.path.join(data_dir, doc)
                mtime = os.path.getmtime(file_path)

                # Es nuevo o ha sido modificado
                if doc not in indexados or indexados[doc] < mtime:
                    docs_a_procesar.append((doc, file_path, mtime, doc in indexados))

            if not docs_a_procesar:
                continue

            logger.info(f"Ingestando {len(docs_a_procesar)} documento(s) en {paths['name']}...")

            # Instanciar el vectorstore una sola vez para borrar si es necesario
            vectorstore = Chroma(persist_directory=db_dir, embedding_function=self.embeddings)

            for doc, file_path, mtime, is_update in docs_a_procesar:
                try:
                    # Si es una actualización, borramos los chunks antiguos
                    if is_update:
                        logger.info(f"Actualizando {doc} (borrando versión anterior)...")
                        # Buscar los IDs de los chunks que tienen este 'source'
                        existing_data = vectorstore.get(where={"source": file_path})
                        if existing_data and existing_data.get('ids'):
                            vectorstore.delete(ids=existing_data['ids'])

                    loader = self._get_loader(file_path)
                    docs = loader.load()
                    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
                    chunks = splitter.split_documents(docs)

                    vectorstore.add_documents(documents=chunks)

                    # Actualizar registro
                    indexados[doc] = mtime
                    self._registrar_indexados(db_dir, indexados)

                    logger.info(f"OK: {doc}")
                except Exception as e:
                    logger.error(f"Error indexando {doc}: {str(e)}. Saltando archivo y continuando...")

    def ingestar_url(self, lib_id, url):
        """Descarga e indexa el contenido de una URL web."""
        if lib_id not in self.LIBRARIES:
            raise ValueError(f"Librería {lib_id} no existe.")

        db_dir = self.LIBRARIES[lib_id]["db"]
        os.makedirs(db_dir, exist_ok=True)

        logger.info(f"Scrapeando e ingestando URL: {url} en {lib_id}...")

        try:
            loader = WebBaseLoader(url)
            docs = loader.load()

            # Asegurar que el metadata source sea la url para futuras referencias
            for doc in docs:
                if 'source' not in doc.metadata:
                    doc.metadata['source'] = url

            splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
            chunks = splitter.split_documents(docs)

            vectorstore = Chroma(persist_directory=db_dir, embedding_function=self.embeddings)
            vectorstore.add_documents(documents=chunks)

            logger.info(f"URL ingestada exitosamente: {url}")
            return True, f"URL indexada correctamente ({len(chunks)} fragmentos generados)."
        except Exception as e:
            logger.error(f"Error ingestando URL {url}: {str(e)}")
            return False, str(e)

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

        # retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        # Pasamos el vectorstore directamente para poder usar similarity_search_with_score
        return CustomQAChain(llm, vectorstore)
