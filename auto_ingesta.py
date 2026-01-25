import os
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Configuración de bibliotecas y rutas
LIBRARIES = {
    "aws": {"data": "./data/aws", "db": "./db_aws"},
    "debian": {"data": "./data/debian", "db": "./db_debian"},
    "cisco": {"data": "./data/cisco", "db": "./db_cisco"}
}

# Función para obtener lista de PDFs en una carpeta
def listar_pdfs(ruta):
    return [f for f in os.listdir(ruta) if f.lower().endswith(".pdf")]

# Función para obtener lista de archivos ya indexados (por nombre base)
def listar_indexados(db_path):
    index_file = os.path.join(db_path, "indexed_files.txt")
    if not os.path.exists(index_file):
        return set()
    with open(index_file, "r") as f:
        return set(line.strip() for line in f)

# Función para registrar un archivo como indexado
def registrar_indexado(db_path, filename):
    index_file = os.path.join(db_path, "indexed_files.txt")
    with open(index_file, "a") as f:
        f.write(filename + "\n")

# Auto-ingesta de PDFs nuevos
def auto_ingesta():
    for key, paths in LIBRARIES.items():
        data_dir = paths["data"]
        db_dir = paths["db"]
        os.makedirs(db_dir, exist_ok=True)
        pdfs = listar_pdfs(data_dir)
        indexados = listar_indexados(db_dir)
        nuevos = [pdf for pdf in pdfs if pdf not in indexados]
        if not nuevos:
            continue
        print(f"[Auto-Ingesta] {key.upper()}: {len(nuevos)} PDF(s) nuevo(s) detectado(s). Procesando...")
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        for pdf in nuevos:
            loader = PyPDFLoader(os.path.join(data_dir, pdf))
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
            chunks = splitter.split_documents(docs)
            # Crea o actualiza la base de datos vectorial
            Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=db_dir
            )
            registrar_indexado(db_dir, pdf)
            print(f"  - {pdf} indexado correctamente.")
    print("[Auto-Ingesta] Proceso completado.")

if __name__ == "__main__":
    auto_ingesta()
