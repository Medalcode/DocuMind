import json
import os
import time
from core.engine import DocuMindEngine
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

# Configuración del juez
JUDGE_MODEL = "llama3.1"

judge_prompt = PromptTemplate.from_template(
    "Eres un juez imparcial evaluando un sistema de IA (RAG). "
    "Se te dará una pregunta, la respuesta esperada correcta, y la respuesta generada por el sistema.\n"
    "Tu tarea es evaluar qué tan bien la respuesta generada coincide semánticamente con la respuesta esperada.\n"
    "Asigna un puntaje del 1 al 5, donde:\n"
    "1 = Completamente incorrecta o irrelevante.\n"
    "3 = Parcialmente correcta, le falta información clave.\n"
    "5 = Totalmente correcta y cubre la respuesta esperada.\n\n"
    "Pregunta: {pregunta}\n"
    "Respuesta Esperada: {respuesta_esperada}\n"
    "Respuesta Generada: {respuesta_generada}\n\n"
    "Solo devuelve un número entero del 1 al 5 como tu puntaje final. No escribas ninguna otra palabra."
)

def evaluate():
    print("🚀 Iniciando Benchmark RAG Automatizado...")
    
    # 1. Cargar dataset
    dataset_path = "backend/benchmark_dataset.json"
    if not os.path.exists(dataset_path):
        print(f"❌ No se encontró {dataset_path}")
        return
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    print(f"📚 Dataset cargado con {len(dataset)} preguntas.")
    
    # 2. Iniciar motor
    engine = DocuMindEngine()
    if not engine.LIBRARIES:
        print("❌ No hay ningún 'Cerebro' (Librería) configurado. Crea uno en la interfaz e ingesta el README.pdf para correr esta prueba.")
        return
        
    # Usaremos el primer cerebro disponible
    lib_id = list(engine.LIBRARIES.keys())[0]
    print(f"🧠 Usando Cerebro ID: {lib_id} - '{engine.LIBRARIES[lib_id]['name']}'")
    
    # Obtener la cadena de QA (Probamos el RAG con Ollama por defecto)
    qa_chain = engine.get_qa_chain(lib_id=lib_id, provider="ollama", model_name=JUDGE_MODEL)
    if not qa_chain:
        print("❌ No se pudo crear la cadena QA. ¿Has indexado algún documento en este cerebro?")
        return
        
    # Juez LLM
    judge_llm = ChatOllama(model=JUDGE_MODEL, temperature=0.0)
    
    total_score = 0
    total_time = 0
    results = []
    
    print("\n" + "="*50)
    for i, item in enumerate(dataset, 1):
        pregunta = item["pregunta"]
        esperada = item["respuesta_esperada"]
        
        print(f"\n[{i}/{len(dataset)}] Q: {pregunta}")
        
        # Ejecutar consulta
        t0 = time.time()
        res = qa_chain.invoke(pregunta)
        t_total = time.time() - t0
        
        generada = res["result"]
        metrics = res["metrics"]
        
        # Evaluar con el Juez
        prompt_val = judge_prompt.format(
            pregunta=pregunta, 
            respuesta_esperada=esperada, 
            respuesta_generada=generada
        )
        judge_res = judge_llm.invoke(prompt_val)
        
        # Limpiar output del juez (solo obtener el número)
        try:
            score_str = ''.join(filter(str.isdigit, judge_res.content))
            score = int(score_str) if score_str else 1
        except:
            score = 1
            
        print(f"   A: {generada[:100]}...")
        print(f"   ⏱️ Tiempo: {metrics['total_time_sec']}s | 🤖 Juez Score: {score}/5")
        
        total_score += score
        total_time += metrics['total_time_sec']
        
        results.append({
            "pregunta": pregunta,
            "generada": generada,
            "score": score,
            "tiempo": metrics['total_time_sec']
        })
        
    print("\n" + "="*50)
    print("📊 RESULTADOS FINALES DEL BENCHMARK")
    print("="*50)
    print(f"Preguntas evaluadas: {len(dataset)}")
    print(f"Tiempo total ejecución: {round(total_time, 2)}s")
    print(f"Tiempo promedio por consulta: {round(total_time/len(dataset), 2)}s")
    print(f"Precisión Promedio (LLM-as-a-Judge): {round(total_score/len(dataset), 2)} / 5.0")
    
if __name__ == "__main__":
    evaluate()
