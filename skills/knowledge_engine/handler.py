from core.engine import DocuMindEngine

engine = DocuMindEngine()

def handle(input_data: dict) -> dict:
    action = input_data.get("action", "search")
    corpus_name = input_data.get("corpus")
    query = input_data.get("query")

    # Mapeo simple de nombres a IDs de la engine
    corpus_map = {v["name"].lower(): k for k, v in engine.LIBRARIES.items()}
    lib_id = corpus_map.get(corpus_name.lower()) if corpus_name else None

    if action == "ingest":
        engine.auto_ingesta()
        return {"result": "Ingesta completada correctamente", "metadata": {}}

    if action == "search" and lib_id:
        qa = engine.get_qa_chain(lib_id)
        if qa:
            res = qa.invoke(query)
            return {
                "result": res["result"],
                "metadata": {"sources": [doc.metadata for doc in res["source_documents"]]}
            }

    return {"result": "Acción o corpus no reconocido", "metadata": {}}
