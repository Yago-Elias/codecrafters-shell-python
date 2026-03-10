import os
from itertools import filterfalse

# ============= COMANDOS BUILT-IN =============
BUILTINS_COMMANDS = set()

# ============= CAMINHOS DO SISTEMA =============
SYSTEM_PATHS = list(
    filterfalse(lambda p: '/mnt' in p or '/home' in p, os.get_exec_path())
)

# ============= VARIÁVEIS GLOBAIS =============
# Cache dos comandos externos (lazy loading)
_external_commands = None


def get_external_commands() -> set[str]:
    """
    Obtém o conjunto de comandos externos disponíveis no PATH.
    
    Usa cache para evitar rescans do filesystem.
    
    Returns:
        Set com nomes dos comandos externos encontrados
    """
    global _external_commands

    if _external_commands is None:
        from .utils import get_commands_in_path
        _external_commands = {
            cmd for p in SYSTEM_PATHS
            for cmd in get_commands_in_path(p)
        }
    
    return _external_commands

# ============= CONSTANTES DE REDIRECIONAMENTO =============
STDIN = 0
STDOUT = 1
STDERR = 2
PIPE = 3

# ============= CONSTANTEs DO HISTÓRICO =============
HISTORY_PATH = os.path.join(os.path.expanduser('~'), '.shell_history')
HISTORY_LENGTH_MAX = 1000
HIST_SIZE_LAST_ADD = 0

__all__ = [
    'BUILTINS_COMMANDS',
    'SYSTEM_PATHS',
    'get_external_commands',
    'STDIN',
    'STDOUT',
    'STDERR',
    'PIPE',
    'HISTORY_LENGTH_MAX',
    'HISTORY_PATH',
    'HIST_SIZE_LAST_ADD',
]