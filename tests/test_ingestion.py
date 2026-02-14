import importlib


def test_auto_ingesta_importable():
    # Comprobar que el módulo principal de ingesta puede importarse
    mod = importlib.import_module('auto_ingesta')
    assert mod is not None
