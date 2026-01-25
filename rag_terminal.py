import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# --- Auto-ingesta ---
def listar_pdfs(ruta):
    return [f for f in os.listdir(ruta) if f.lower().endswith(".pdf")]

def listar_indexados(db_path):
    index_file = os.path.join(db_path, "indexed_files.txt")
    if not os.path.exists(index_file):
        return set()
    with open(index_file, "r") as f:
        return set(line.strip() for line in f)

def registrar_indexado(db_path, filename):
    index_file = os.path.join(db_path, "indexed_files.txt")
    with open(index_file, "a") as f:
        f.write(filename + "\n")

def auto_ingesta(console, libraries):
    for key, paths in libraries.items():
        data_dir = paths["data"]
        db_dir = paths["db"]
        os.makedirs(db_dir, exist_ok=True)
        pdfs = listar_pdfs(data_dir)
        indexados = listar_indexados(db_dir)
        nuevos = [pdf for pdf in pdfs if pdf not in indexados]
        if not nuevos:
            continue
        console.print(f"[Auto-Ingesta] {key.upper()}: {len(nuevos)} PDF(s) nuevo(s) detectado(s). Procesando...")
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        for pdf in nuevos:
            loader = PyPDFLoader(os.path.join(data_dir, pdf))
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
            chunks = splitter.split_documents(docs)
            Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=db_dir
            )
            registrar_indexado(db_dir, pdf)
            console.print(f"  - {pdf} indexado correctamente.")
    console.print("[Auto-Ingesta] Proceso completado.\n")

# --- Interfaz principal ---
console = Console()
LIBRARIES = {
    1: {"name": "AWS Cloud & AI", "data": "./data/aws", "db": "./db_aws"},
    2: {"name": "Debian SysAdmin", "data": "./data/debian", "db": "./db_debian"},
    3: {"name": "Cisco Networking", "data": "./data/cisco", "db": "./db_cisco"}
}

def obtener_qa_chain(lib_id):
    db_path = LIBRARIES[lib_id]["db"]
    if not os.path.exists(db_path):
        console.print(f"[bold red]Error:[/bold red] La base de datos en {db_path} no existe. Primero debes indexar los documentos.")
        return None
    with console.status("[bold green]Cargando base de conocimientos...", spinner="aesthetic"):
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        llm = ChatOllama(model="llama3.1", temperature=0.1)
        vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )

def mostrar_menu():
    console.clear()
    table = Table(title="SISTEMA RAG MULTI-BIBLIOTECA", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Especialidad", min_width=20)
    for key, value in LIBRARIES.items():
        table.add_row(str(key), value["name"])
    console.print(Panel.fit("Seleccione el cerebro de IA que desea consultar", border_style="blue"))
    console.print(table)

def chat_loop(qa_chain, lib_name):
    console.print(f"\n[bold cyan]Conectado a: {lib_name}[/bold cyan] (Escribe 'volver' para ir al menú)\n")
    while True:
        query = Prompt.ask("[bold green]Consulta[/bold green]")
        if query.lower() == "volver":
            break
        with console.status("[italic]Buscando en documentos locales...[/italic]", spinner="dots"):
            start_time = time.time()
            res = qa_chain.invoke(query)
            end_time = time.time()
        console.print(Panel(res["result"], title="Respuesta", border_style="green"))
        paginas = set([str(doc.metadata.get('page', '?')) for doc in res['source_documents']])
        console.print(f"[dim]Fuentes: {lib_name} - Pág(s): {', '.join(paginas)} | Tiempo: {end_time - start_time:.2f}s[/dim]\n")

def main():
    auto_ingesta(console, LIBRARIES)
    while True:
        mostrar_menu()
        opcion = IntPrompt.ask("Seleccione una opción", choices=[str(k) for k in LIBRARIES.keys()] + ["0"])
        if opcion == 0:
            break
        chain = obtener_qa_chain(opcion)
        if chain:
            chat_loop(chain, LIBRARIES[opcion]["name"])

if __name__ == "__main__":
    main()
