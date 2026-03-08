import os, subprocess

from .types_shell import InputShell, OutputShell
from .config import (
    BUILTINS_COMMANDS,
    SYSTEM_PATHS,
    STDOUT,
    STDERR,
    PIPE,
)
from .utils import (
    find_path_command,
    get_commands_in_path,
    input_shell,
    pipe_execution,
)


def f_echo(input: InputShell) -> OutputShell:
    """Implementa comando echo."""
    return OutputShell(bytes((' '.join(input.args) + '\n'), 'utf-8')) 


def f_type(input: InputShell) -> OutputShell:
    """Implementa comando type - mostra tipo do comando."""
    output = b''

    for arg in input.args:
        found = False
        output += bytes(f'{arg}', 'utf-8')

        if arg in BUILTINS_COMMANDS:
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


def f_pwd(input: InputShell | None = None) -> OutputShell:
    """Implementa comando pwd - mostra diretório atual."""
    return OutputShell(bytes(os.getcwd() + '\n', 'utf-8'))


def f_command(input: InputShell) -> OutputShell:
    """Executa comando externo."""
    command = [input.command]
    if input.args:
        command += input.args
    result = subprocess.run(command, capture_output=True)
    return OutputShell(result.stdout, result.stderr, result.returncode)


def f_cd(input: InputShell) -> OutputShell:
    """Implementa comando cd - muda diretório."""
    if input.args:
        path = input.args[0]
        if '~' == path and (home := os.getenv('HOME')):
            os.chdir(home)
        elif os.path.exists(path):
            os.chdir(path)
        else:
            return OutputShell(bytes(f'cd: {path}: No such file or directory\n', 'utf-8'))
    return OutputShell()


def f_history():
    """Implementa comando history (placeholder)."""
    pass


# Dicionário de comandos
COMMANDS_MAP = {
    'echo': f_echo,
    'type': f_type,
    'pwd': f_pwd,
    'external': f_command,
    'cd': f_cd,
    'history': f_history
}


def command_handler(input: InputShell):
    """
    Resolve e retorna a função de comando apropriada.
    
    Args:
        input: Estrutura com informações do comando
        
    Returns:
        Função do comando ou None se não encontrado
    """
    if input.command == 'exit':
        exit()

    command = COMMANDS_MAP.get(input.command)
    if command is None and find_path_command(SYSTEM_PATHS, input.command):
        command = COMMANDS_MAP.get('external')
    
    return command


def run() -> None:
    """Loop principal do shell."""
    
    while (True):
        try:
            input_sh = input_shell()
        except KeyboardInterrupt:
            break
        
        _redirect, _sh = input_sh

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
            print((output.stdout + output.stderr).decode(), end='')


__all__ = [
    'run',
    'command_handler',
    'COMMANDS_MAP',
    'BUILTINS_COMMANDS',
]
