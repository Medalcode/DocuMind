from typing import Dict, Any


def handle(input: Dict[str, Any]) -> Dict[str, Any]:
    """Handler de ejemplo para la skill `pdf_finder`.

    input: {'query': str}
    output: {'answer': str, 'sources': list}
    """
    query = input.get('query', '')
    # Implementación mínima: devolver respuesta de ejemplo.
    # Integración real: usar vectorstore + retrieval + resumidor.
    answer = f"Respuesta de ejemplo para: {query}"
    sources = []
    return {"answer": answer, "sources": sources}
