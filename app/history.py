import os, readline

from .config import HISTORY_LENGTH_MAX, HISTFILE


def initialize_history() -> None:
    if HISTFILE is None: return
    # if os.path.isfile(HISTFILE):
    #     open(HISTFILE, 'w').close()
    
    try:
        readline.read_history_file(HISTFILE)
        readline.set_history_length(HISTORY_LENGTH_MAX)
    except (FileNotFoundError, OSError):
        pass


def append_history(num_itens: int=1, filename: str | None = None) -> None:
    if filename is None and HISTFILE:
        readline.append_history_file(num_itens, HISTFILE)
    elif filename and os.path.isfile(filename):
        readline.append_history_file(num_itens, filename)


__all__ = [
    'initialize_history',
    'append_history',
]