import sys
import os
import subprocess
from typing import Any
from itertools import filterfalse
from collections import namedtuple

InputSh = namedtuple('InputSh', ['command', 'args'])


def find_path_command(paths: list[str], command: str) -> str | None:
    for path in paths:
        path_command = path + '/' + command
        if os.path.exists(path_command) and os.access(path_command, os.X_OK):
            return path_command
    return None


def f_echo(input: InputSh) -> None:
    print(' '.join(input.args))


def f_type(input: InputSh) -> None:
    if not input.args: print()

    for arg in input.args:
        found = False
        print(f'{arg}', end='')

        if arg in list(builtin_commands.keys()) + ['exit']:
            found = True
            print(' is a shell builtin')
        else:
            path_command = find_path_command(path, arg)
            if path_command and os.path.exists(path_command) and os.access(path_command, os.X_OK):
                found = True
                print(f' is {path_command}')
        if not found:
            print(': not found')


def f_pwd(input: InputSh) -> None:
    print(os.getcwd())


def f_command(input: InputSh) -> None:
    command = [input.command]
    if input.args:
        command += input.args
    result = subprocess.run(command, capture_output=True)
    if result.stdout:
        print(result.stdout.decode(), end='')
    else:
        print(result.stderr.decode(), end='')


def f_cd(input: InputSh) -> None:
    if input.args:
        path = input.args[0]
        if '~' == path and (home := os.getenv('HOME')):
            os.chdir(home)
        elif os.path.exists(path):
            os.chdir(path)
        else:
            print(f'cd: {path}: No such file or directory')


def input_sh() -> InputSh:
    input_aux = input().strip(' ')

    ind = input_aux.find(' ')
    command = input_aux[:ind] if ind != -1 else input_aux
    args  = handler_args(input_aux[ind+1:]) if ind != -1 else []
    
    return InputSh(command, args)


def handler_args(args: str) -> list[str]:
    arg = ''
    list_arg = []
    single_quotes = double_quotes = False
    char = iter(args)

    for c in char:
        if c == "\\" and not (single_quotes or double_quotes):
            arg += next(char)
            continue
        if not double_quotes:
            if c.isspace() and not single_quotes:
                if arg:
                    list_arg.append(arg)
                    arg = ''
                continue
            elif c == "'":
                single_quotes = not single_quotes
                continue

        if not single_quotes:
            if c.isspace() and not double_quotes:
                if arg:
                    list_arg.append(arg)
                    arg = ''
                continue
            elif c == '"':
                double_quotes = not double_quotes
                continue
        arg += c
    
    list_arg.append(arg)
    return list_arg


def handler(input: InputSh) -> Any | None:
    if input.command == 'exit':
        exit()

    command = builtin_commands.get(input.command)
    if command is None and find_path_command(path, input.command):
        command = builtin_commands.get('external')
    return command


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
    while (True):
        sys.stdout.write("$ ")
        shell_command = input_sh()

        if shell_command.command == '':
            continue
        if exec_command := handler(shell_command):
            exec_command(shell_command)
        else:
            print(f'{shell_command.command}: command not found')

if __name__ == "__main__":
    main()
