import os, subprocess, readline
from typing import Literal

from .types_shell import InputShell, OutputShell
from .config import (
    BUILTINS_COMMANDS,
    SYSTEM_PATHS,
    STDOUT,
    STDERR,
    PIPE,
    HISTFILE,
    HIST_SIZE_LAST_ADD,
)
from .utils import (
    find_path_command,
    get_commands_in_path,
    input_shell,
    pipe_execution,
)
from .history import append_history

# Dicionário de comandos
COMMANDS_MAP = dict()

BUILTINS_COMMANDS.add('exit')


def register_command(function):
    """Decorator para registrar os comandos do shell"""
    global BUILTINS_COMMANDS
    COMMANDS_MAP[function.__name__[2:]] = function
    BUILTINS_COMMANDS.add(function.__name__[2:])
    return function


@register_command
def f_echo(input: InputShell) -> OutputShell:
    """Implementa comando echo."""
    return OutputShell(bytes((' '.join(input.args) + '\n'), 'utf-8')) 


@register_command
def f_type(input: InputShell) -> OutputShell:
    """Implementa comando type - mostra tipo do comando."""
    output = b''

    for arg in input.args:
        found = False
        output += bytes(f'{arg}', 'utf-8')

        if arg in get_builtins_commands():
            found = True
            output += bytes(' is a shell builtin\n', 'utf-8')
        else:
            path_command = find_path_command(SYSTEM_PATHS, arg)
            if path_command and os.path.exists(path_command) and os.access(path_command, os.X_OK):
                found = True
                output += bytes(f' is {path_command}\n', 'utf-8')
        if not found:
            output += bytes(': not found\n', 'utf-8')
    return OutputShell(output)


@register_command
def f_pwd(input: InputShell | None = None) -> OutputShell:
    """Implementa comando pwd - mostra diretório atual."""
    return OutputShell(bytes(os.getcwd() + '\n', 'utf-8'))


@register_command
def f_cd(input: InputShell) -> OutputShell:
    """Implementa comando cd - muda diretório."""
    if input.args:
        path = input.args[0]
        if '~' == path and (home := os.getenv('HOME')):
            os.chdir(home)
        elif os.path.exists(path):
            os.chdir(path)
        else:
            return OutputShell(stderr=bytes(f'cd: {path}: No such file or directory\n', 'utf-8'))
    return OutputShell()


def read_file(filename: str | None) -> list[str] | Literal['']:
    if filename is None: return ''
    try:
        with open(filename) as fn:
            data = fn.read()
    except FileNotFoundError:
        return ''
    data = data.split('\n')
    data.pop()
    # from .utils import log
    # log(f'<data read_file> {data!r}')
    return data


def get_arg(args: list[str] | None, index: int=0) -> None | str:
    try:
        return args[index] if args else None
    except IndexError:
        return None


def read_history(args: list[str] | None) -> OutputShell:
    filename = get_arg(args, 1)
    if not filename: return OutputShell()

    data = read_file(filename)
    if not data: return OutputShell()
    count = 0

    for d in data:
        if d:
            readline.add_history(d)
            count += 1
    
    append_history(count)
    return OutputShell()


def write_history(args: list[str] | None) -> OutputShell:
    filename = get_arg(args, 1)
    if not filename: return OutputShell()

    readline.write_history_file(filename)
    return OutputShell()


def add_history(args: list[str] | None) -> OutputShell:
    filename = get_arg(args, 1)
    if not filename: return OutputShell()
    hist_len = readline.get_current_history_length()
    global HIST_SIZE_LAST_ADD

    if not os.path.isfile(filename):
        open(filename, 'w').close()

    if HIST_SIZE_LAST_ADD == 0:
        append_history(hist_len, filename)
    else:
        append_history(hist_len - HIST_SIZE_LAST_ADD, filename)
    HIST_SIZE_LAST_ADD = hist_len

    return OutputShell()


@register_command
def f_history(input: InputShell) -> OutputShell:
    """Implementa comando history (placeholder)."""
    data = ''
    ind = number = 0
    from .utils import log

    def enumerate_history(h: str) -> str:
        nonlocal number
        number += 1
        return f'    {number}  {h}'
    
    from .utils import log

    arg = get_arg(input.args)
    # f = get_arg(input.args, 1)
    # log(f'<command> history {arg if arg else ''} {f if f else ''}')
    match arg:
        case '-r':
            return read_history(input.args)
        case '-w':
            return write_history(input.args)
        case '-a':
            return add_history(input.args)
        case _:
            # log(f'<command> history')
            # log(f'<HISTFILE> {get_env_hist_file()}')
            if data := read_file(HISTFILE):
                data = list(map(enumerate_history, data))
                # log(f'<data> {data!r}')
            if arg:
                if not arg.isnumeric():
                    return OutputShell()
                ind = int(arg) * -1
                ind = 0 if abs(ind) > len(data) else ind
            data = '\n'.join(data[ind:]) + '\n'
            
    return OutputShell(bytes(data, encoding='utf-8'))


def external_command(input: InputShell) -> OutputShell:
    """Executa comando externo."""
    command = input.command
    if input.args:
        command = [command] + input.args
    result = subprocess.run(command, capture_output=True)
    return OutputShell(result.stdout, result.stderr, result.returncode)


def command_handler(input: InputShell):
    """
    Resolve e retorna a função de comando apropriada.
    
    Args:
        input: Estrutura com informações do comando
        
    Returns:
        Função do comando ou None se não encontrado
    """
    if input.command == '':
        return None
    
    append_history()

    if input.command == 'exit':
        exit()

    command = COMMANDS_MAP.get(input.command)
    if command is None and find_path_command(SYSTEM_PATHS, input.command):
        command = external_command
    
    return command


def get_builtins_commands() -> set:
    return BUILTINS_COMMANDS


def get_commands_map() -> dict:
    return COMMANDS_MAP


def run() -> None:
    """Loop principal do shell."""
    
    while (True):
        try:
            input_sh = input_shell()
        except KeyboardInterrupt:
            break
        else:
            _redirect, _sh = input_sh
            if _sh[0].command == '':
                continue
        

        if _redirect == PIPE:
            pipe_execution(_sh, COMMANDS_MAP, command_handler)
        elif _redirect in (STDOUT, STDERR):
            if (exec_command := command_handler(_sh[0])) == None:
                print(f'{_sh[0].command}: command not found')
                continue

            output: OutputShell = exec_command(_sh[0])

            with open(_sh[0].file_name, _sh[0].opening_mode, encoding='utf-8') as file:
                to_redirect = output.stderr if _redirect == STDERR else output.stdout
                file.write(to_redirect.decode())

            if _redirect == STDERR:
                print(output.stdout.decode(), end='')
            else:
                print(output.stderr.decode(), end='')
        else:
            if (exec_command := command_handler(_sh[0])) == None:
                print(f'{_sh[0].command}: command not found')
                continue
            output: OutputShell = exec_command(_sh[0])
            print((output.stdout + output.stderr).decode(), end='', flush=True)


__all__ = [
    'run',
    'command_handler',
    'get_commands_map',
    'get_builtins_commands',
]
