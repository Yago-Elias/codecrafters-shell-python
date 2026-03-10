import os, readline

from .config import HISTORY_LENGTH_MAX


def initialize_history() -> None:
    history = os.path.join(os.path.expanduser('~'), '.shell_history')

    if (os.path.isfile(history) == False):
        open(history, 'w').close()
    
    try:
        readline.read_history_file(history)
        readline.set_history_length(HISTORY_LENGTH_MAX)
    except (FileNotFoundError, OSError):
        pass


def append_history() -> None:
    history = os.path.join(os.path.expanduser('~'), '.shell_history')
    
    if (os.path.isfile(history)):
        readline.append_history_file(1, history)


__all__ = [
    'initialize_history',
    'append_history',
]