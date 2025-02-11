import logging

from rich.console import Console
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

LOGGER_PREFIX = "pizza_gen"


def enable_debug_log():
    logging.getLogger().setLevel(logging.DEBUG)


def get_logger(name: str):
    return logging.getLogger(f"{LOGGER_PREFIX}." + name)


console = Console(stderr=True)
