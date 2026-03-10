"""
Ponto de entrada do shell - Interface de linha de comando.
"""

from .completion_shell import configure_readline
from .builtins_shell import run
from .history import initialize_history


def main():
    configure_readline()
    initialize_history()
    run()


if __name__ == "__main__":
    main()
