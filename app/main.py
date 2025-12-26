import sys
import os
import subprocess
from typing import Any
from itertools import filterfalse


def find_path_command(paths: list[str], command: str) -> str | None:
    for path in paths:
        path_command = path + '/' + command
        if os.path.exists(path_command) and os.access(path_command, os.X_OK):
            return path_command
    return None


def f_echo(input: dict[str, Any]) -> None:
    print(' '.join(input['args']))


def f_type(input: dict[str, Any]) -> None:
    is_builtin = False
    print(f'{input['args'][0]}', end='')

    if input['args'][0] in list(builtin_commands.keys()) + ['exit']:
        is_builtin = True
        print(' is a shell builtin')
    else:
        path_command = find_path_command(path, input['args'][0])
        if path_command and os.path.exists(path_command) and os.access(path_command, os.X_OK):
            is_builtin = True
            print(f' is {path_command}')
    if not is_builtin:
        print(': not found')


def f_pwd(input: dict[str, Any]) -> None:
    print(os.getcwd())


def f_command(input: dict[str, Any]) -> None:
    command = [input['command']]
    if input['args']:
        command += input['args']
    result = subprocess.run(command, capture_output=True).stdout
    print(result.decode(), end='')


def handler(input: dict[str, Any]) -> Any | None:
    command = builtin_commands.get(input['command'])
    if command is None and find_path_command(path, input['command']):
        command = builtin_commands.get('external')
    return command


def f_cd(input: dict[str, Any]):
    pass


builtin_commands = {
    'echo': f_echo,
    'type': f_type,
    'pwd': f_pwd,
    'external': f_command,
    'cd': f_cd,
}

path = list(
    filterfalse(lambda p: '/mnt' in p or '/home' in p, os.get_exec_path())
)


def main():
    input_sh = {'command': str, 'args': list[str]}
    is_builtin = False
    while (True):
        sys.stdout.write("$ ")

        input_aux = input().split(' ')
        input_sh['command'] = input_aux[0]
        input_sh['args'] = input_aux[1:]
        
        if input_sh['command'] == 'exit':
            exit()
        
        if exec_command := handler(input_sh):
            exec_command(input_sh)
        else:
            print(f'{input_sh['command']}: command not found')

if __name__ == "__main__":
    main()
