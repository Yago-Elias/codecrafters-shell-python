"""
Ponto de entrada do shell - Interface de linha de comando.
"""

from .completion_shell import configure_readline
from .builtins_shell import run


def main():
    configure_readline()
    run()


if __name__ == "__main__":
    main()
