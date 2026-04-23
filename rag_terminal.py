import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from core.engine import DocuMindEngine

console = Console()
engine = DocuMindEngine()

def mostrar_menu():
    console.clear()
    table = Table(title="SISTEMA RAG MULTI-BIBLIOTECA (LEAN)", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Especialidad", min_width=20)
    for key, value in engine.LIBRARIES.items():
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
    with console.status("[bold yellow]Iniciando Auto-Ingesta...", spinner="bouncingBar"):
        engine.auto_ingesta()
    
    while True:
        mostrar_menu()
        opcion = IntPrompt.ask("Seleccione una opción (0 para salir)", choices=[str(k) for k in engine.LIBRARIES.keys()] + ["0"])
        if opcion == 0:
            break
        
        with console.status("[bold green]Cargando base de conocimientos...", spinner="aesthetic"):
            chain = engine.get_qa_chain(opcion)
        
        if chain:
            chat_loop(chain, engine.LIBRARIES[opcion]["name"])
        else:
            console.print("[bold red]Error:[/bold red] No se pudo cargar la base de datos.")

if __name__ == "__main__":
    main()
