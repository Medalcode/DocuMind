import os
import sys

# Asegura que la raíz del repositorio esté en sys.path durante las pruebas
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
