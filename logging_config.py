import logging


def configure_logging(level: int = logging.INFO):
    fmt = '%(asctime)s %(levelname)s %(name)s %(message)s'
    logging.basicConfig(level=level, format=fmt)


def get_logger(name: str):
    configure_logging()
    return logging.getLogger(name)
