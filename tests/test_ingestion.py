from core.engine import DocuMindEngine


def test_engine_init():
    engine = DocuMindEngine()
    assert len(engine.LIBRARIES) == 3
    assert engine.model_name == "llama3.1"

def test_engine_library_data():
    engine = DocuMindEngine()
    for lib_id, cfg in engine.LIBRARIES.items():
        assert "name" in cfg
        assert "data" in cfg
        assert "db" in cfg
