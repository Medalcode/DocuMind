from skills.pdf_finder import handler


def test_handler_basic():
    res = handler.handle({'query': 'hola'})
    assert isinstance(res, dict)
    assert 'answer' in res
