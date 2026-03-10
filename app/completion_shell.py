import os, readline, sys, atexit

from .builtins_shell import get_builtins_commands
from .config import get_external_commands
from .utils import input_handler


def list_path(path: str) -> tuple[str, list[str], str]:
    """
    Extrai informações sobre um caminho de arquivo.
    
    Args:
        path: Caminho para processar
        
    Returns:
        Tupla (diretório, lista_de_arquivos, nome_procurado)
    """
    head, tail = os.path.split(path)
    if os.path.exists(head) == False:
        return ('', [], '')
    
    files = os.listdir(head)
    return head, files, tail


def completer(text: str, state: int):
    """
    Função de completar chamada pelo readline.
    
    Args:
        text: Texto a completar
        state: Estado da completação (0, 1, 2, ...)
        
    Returns:
        Próxima sugestão de completação ou None
    """
    search = text
    matches = [cmd for cmd in get_builtins_commands() if cmd.startswith(text)]
    path = ''
    
    if not matches:
        external_commands = get_external_commands()
        matches = [cmd for cmd in external_commands if cmd.startswith(text)]
    
    buffer = input_handler(readline.get_line_buffer())
    if len(buffer) > 1:
        if text.find('/') == -1:
            files = os.listdir()
        else:
            # resgata o último argumento da linha de comando
            path, files, search = list_path(buffer[-1])
        
        matches = [file for file in files if file.startswith(search)]

    try:
        path_name = os.path.join(path, matches[state])
        if os.path.isdir(path_name):
            return  path_name + '/'
        return path_name + ' '
    except IndexError:
        return None


def list_commands_match(substituition, matches, longest) -> None:
    """
    Exibe sugestões de completação de forma customizada.
    
    Args:
        substitution: Texto a substituir
        matches: Lista de correspondências
        longest: Maior comprimento de correspondência
    """
    buffer = readline.get_line_buffer()
    print()
    # remove a barra (/) se houver
    basenames = list(map(lambda bn: bn[:-1] if bn[-1] == '/' else bn, matches))
    # separa o dirtório do arquivo ou último nível do diretório
    basenames = list(map(os.path.split, basenames))
    # adiciona a barra (/) se for um diretório
    basenames = list(
        map(
            lambda bn: bn[1] + '/' if os.path.isdir(os.path.join(*bn)) else bn[1],
            basenames
            )
        )
    
    print(' '.join(basenames), flush=True)
    sys.stdout.write('\033[K')
    sys.stdout.write(f'$ {buffer}')
    sys.stdout.flush()
    readline.redisplay()


def configure_readline() -> None:
    """Configura a biblioteca readline com as funções customizadas."""
    readline.set_completer(completer)
    readline.set_completion_display_matches_hook(list_commands_match)
    readline.set_completer_delims(' \t')
    readline.parse_and_bind('tab: complete')


__all__ = [
    'configure_readline',
    'completer',
    'list_commands_match',
    'list_path',
]
