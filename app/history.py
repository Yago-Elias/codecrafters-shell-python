import os, readline

from .config import HISTORY_LENGTH_MAX, HISTORY_PATH


def initialize_history() -> None:
    # if (os.path.isfile(history) == False):
    open(HISTORY_PATH, 'w').close()
    
    try:
        readline.read_history_file(HISTORY_PATH)
        readline.set_history_length(HISTORY_LENGTH_MAX)
    except (FileNotFoundError, OSError):
        pass


def append_history(num_itens: int=1, filename: str | None = None) -> None:
    if filename is None and os.path.isfile(HISTORY_PATH):
        readline.append_history_file(num_itens, HISTORY_PATH)
    elif filename and os.path.isfile(filename):
        readline.append_history_file(num_itens, filename)


__all__ = [
    'initialize_history',
    'append_history',
]