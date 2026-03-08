"""
Shell customizado - Módulo principal do pacote.

Este pacote implementa um shell Unix-like com suporte a:
- Comandos built-in (echo, cd, pwd, type)
- Redirecionamento de saída (>, >>, 2>, 2>>)
- Pipes (|)
- Auto-completar com Tab
- Histórico de comandos
"""

# Importações de configurações
from .config import (
    BUILTINS_COMMANDS,
    SYSTEM_PATHS,
    STDOUT,
    STDERR,
    STDIN,
    PIPE,
)

# Importações de tipos
from .types_shell import (
    InputShell,
    OutputShell,
    CommandType,
)

# Importações de utilitários
from .utils import (
    path_exists,
    find_path_command,
    get_commands_in_path,
    input_handler,
    input_shell,
    pipe_execution,
)

# Importações de comandos
from .builtins_shell import (
    run,
    command_handler,
    COMMANDS_MAP,
)

# Importações de completion
from .completion_shell import (
    completer,
    configure_readline,
)

# Ponto de entrada
from .cli import main

# from app impot *
__all__ = [
    # config
    'BUILTINS_COMMANDS',
    'SYSTEM_PATHS',
    'STDOUT',
    'STDERR',
    'STDIN',
    'PIPE',

    # tipos
    'InputShell',
    'OutputShell',
    'CommandType',

    # utils
    'path_exists',
    'find_path_command',
    'get_commands_in_path',
    'input_handler',
    'input_shell',
    'pipe_execution',

    # builtins
    'run',
    'command_handler',
    'COMMANDS_MAP',

    # completion
    'completer',
    'configure_readline',

    # main
    'main',
]

__version__ = '0.1.0'
__author__ = 'Yago Elias'
__description__ = 'Shell customizado em Python'
