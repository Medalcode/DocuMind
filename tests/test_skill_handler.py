from skills.knowledge_engine import handler

def test_knowledge_engine_search_fallback():
    # Test fallback para parámetros no existentes
    res = handler.handle({'action': 'search', 'corpus': 'inexistente', 'query': 'hola'})
    assert res['result'] == "Acción o corpus no reconocido"

def test_knowledge_engine_ingest_structure():
    # Test de estructura de respuesta de ingesta
    res = handler.handle({'action': 'ingest'})
    assert 'result' in res
    assert "Ingesta" in res['result']
