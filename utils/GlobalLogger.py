import sys

from fastapi.logger import logger
import logging
import threading


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]


class GlobalLogger(metaclass=SingletonMeta):

    def __new__(cls, *args, **kwargs):
        return cls.set_up_logging()

    @staticmethod
    def set_up_logging():
        gunicorn_logger = logging.getLogger('gunicorn.error')
        logger.addHandler(gunicorn_logger.handlers)
        logger.setLevel(gunicorn_logger.level)
        return logger


def log_info(message, setup_logging=False):
    if setup_logging:
        global_logger = GlobalLogger().set_up_logging()
    else:
        global_logger = GlobalLogger()

    # log locally and to gunicorn logger
    print(message)
    global_logger.info(message)
    sys.stdout.flush()
