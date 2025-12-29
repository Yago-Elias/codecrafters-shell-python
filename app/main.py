import sys
import os
import subprocess
from typing import Any
from itertools import filterfalse
from collections import namedtuple

InputShell = namedtuple('InputShell', ['command', 'args', 'redirect', 'file_name'])
OutputShell = namedtuple('OutputShell', ['stdout', 'stderr', 'returncode'], defaults=[b'', b'', 0])


def find_path_command(paths: list[str], command: str) -> str | None:
    for path in paths:
        path_command = path + '/' + command
        if os.path.exists(path_command) and os.access(path_command, os.X_OK):
            return path_command
    return None


def f_echo(input: InputShell) -> OutputShell:
    return OutputShell(bytes((' '.join(input.args) + '\n'), 'utf-8')) 


def f_type(input: InputShell) -> OutputShell:
    output = b''
    if not input.args: return OutputShell()

    for arg in input.args:
        found = False
        output += bytes(f'{arg}', 'utf-8')

        if arg in list(builtin_commands.keys()) + ['exit']:
            found = True
            output += bytes(' is a shell builtin\n', 'utf-8')
        else:
            path_command = find_path_command(path, arg)
            if path_command and os.path.exists(path_command) and os.access(path_command, os.X_OK):
                found = True
                output += bytes(f' is {path_command}\n', 'utf-8')
        if not found:
            output += bytes(': not found\n', 'utf-8')
    return OutputShell(output)


def f_pwd(input: InputShell) -> OutputShell:
    return OutputShell(bytes(os.getcwd() + '\n', 'utf-8'))


def f_command(input: InputShell) -> OutputShell:
    command = [input.command]
    if input.args:
        command += input.args
    result = subprocess.run(command, capture_output=True)
    return OutputShell(result.stdout, result.stderr, result.returncode)


def f_cd(input: InputShell) -> OutputShell:
    if input.args:
        path = input.args[0]
        if '~' == path and (home := os.getenv('HOME')):
            os.chdir(home)
        elif os.path.exists(path):
            os.chdir(path)
        else:
            return OutputShell(bytes(f'cd: {path}: No such file or directory\n', 'utf-8'))
    return OutputShell()


def input_shell() -> InputShell:
    line_command = input_handler(input().strip(' '))
    command = line_command[0]
    args = line_command[1:]
    redirect = False
    file_name = ''
    args_aux = []

    for ind, arg in enumerate(args):
        if '>' == arg or '1>' == arg:
            args_aux = args[:ind]
            redirect = True
            file_name = args[ind+1]
    args = args_aux if args_aux else args

    return InputShell(command, args, redirect, file_name)


def input_handler(args: str) -> list[str]:
    arg = ''
    list_arg = []
    single_quotes = double_quotes = False
    char = iter(args)

    for c in char:
        # escapa o caractere fora de aspas simples e aspas duplas
        if c == "\\" and single_quotes == double_quotes == False:
            arg += next(char)
            continue
        
        # tratamento dos argumentos quando não há aspas simples e aspas duplas
        if c.isspace() and not (single_quotes or double_quotes):
            if arg:
                list_arg.append(arg)
                arg = ''
            continue

        # trata o caractere se estiver dentro ou fora de aspas SIMPLES
        if not double_quotes:
            if c == "'":
                single_quotes = not single_quotes
                continue

        # trata o caractere se estiver dentro ou fora de aspas DUPLAS
        if not single_quotes:
            if c == '"':
                double_quotes = not double_quotes
                continue
            elif c == '\\' and double_quotes:
                c = next(char)
                if c in ['\\', '"']:
                    arg += c
                    continue
                else:
                    arg += '\\'
        arg += c
    
    list_arg.append(arg)
    return list_arg


def command_handler(input: InputShell) -> Any | None:
    if input.command == 'exit':
        exit()

    command = builtin_commands.get(input.command)
    if command is None and find_path_command(path, input.command):
        command = builtin_commands.get('external')
    return command


def run() -> None:
    while (True):
        sys.stdout.write("$ ")
        input_sh = input_shell()

        if input_sh.command == '':
            continue
        if exec_command := command_handler(input_sh):
            output_sh: OutputShell = exec_command(input_sh)

            if input_sh.redirect:
                with open(input_sh.file_name, 'w', encoding='utf-8') as file:
                    file.write(output_sh.stdout.decode())
                    if output_sh.returncode:
                        print(output_sh.stderr.decode(), end='')
            else:
                print(output_sh.stdout.decode() + output_sh.stderr.decode(), end='')
        else:
            print(f'{input_sh.command}: command not found')


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
    run()

if __name__ == "__main__":
    main()
