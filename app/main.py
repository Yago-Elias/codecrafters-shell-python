import sys, os, subprocess, readline
from typing import Any
from itertools import filterfalse
from collections import namedtuple

InputShell = namedtuple('InputShell', ['command', 'args', 'redirect', 'file_name', 'opening_mode'])
OutputShell = namedtuple('OutputShell', ['stdout', 'stderr', 'returncode'], defaults=[b'', b'', 0])
STDOUT = 1
STDERR = 2


def find_path_command(paths: list[str], command: str) -> str | None:
    for path in paths:
        path_command = path + '/' + command
        if os.path.exists(path_command) and os.access(path_command, os.X_OK):
            return path_command
    return None


def completer(text, state):
    hit = [cmd for cmd in _builtins_command_ if cmd.startswith(text)]
    if not hit:
        hit = [cmd for cmd in _external_command_ if cmd.startswith(text)]

    try:
        return hit[state] + ' '
    except IndexError:
        return None

def list_commands_match(substituition, matches, longest) -> None:
    buffer = readline.get_line_buffer()
    print()
    print(' '.join(matches))
    sys.stdout.write('\033[K')
    sys.stdout.write(f'$ {buffer}')
    sys.stdout.flush()
    readline.redisplay()


def get_commands_in_path(path: str) -> list[str]:
    if os.path.exists(path):
        return [cmd for cmd in os.listdir(path) if os.access(os.path.join(path, cmd), os.X_OK)]
    return []


def f_echo(input: InputShell) -> OutputShell:
    return OutputShell(bytes((' '.join(input.args) + '\n'), 'utf-8')) 


def f_type(input: InputShell) -> OutputShell:
    output = b''
    if not input.args: return OutputShell()

    for arg in input.args:
        found = False
        output += bytes(f'{arg}', 'utf-8')

        if arg in list(_commands_.keys()) + ['exit']:
            found = True
            output += bytes(' is a shell builtin\n', 'utf-8')
        else:
            path_command = find_path_command(_path_, arg)
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
    line_command = input_handler(input('$ ').strip(' '))
    command = line_command[0]
    args = line_command[1:]
    redirect = None
    file_name = ''
    opening_mode = ''
    args_aux = []

    for ind, arg in enumerate(args):
        if '>' in arg:
            args_aux = args[:ind]
            redirect = STDERR if arg in ('2>', '2>>') else STDOUT
            file_name = args[ind+1]
            opening_mode = 'w' if arg.count('>') == 1 else 'a'
            break
    args = args_aux if args_aux else args

    return InputShell(command, args, redirect, file_name, opening_mode)


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

    command = _commands_.get(input.command)
    if command is None and find_path_command(_path_, input.command):
        command = _commands_.get('external')
    return command


def run() -> None:
    while (True):
        # sys.stdout.write("$ ")
        try:
            input_sh = input_shell()
        except KeyboardInterrupt:
            break

        if input_sh.command == '':
            continue
        if exec_command := command_handler(input_sh):
            output_sh: OutputShell = exec_command(input_sh)
            output: bytes = output_sh.stdout + output_sh.stderr

            if input_sh.redirect:
                with open(input_sh.file_name, input_sh.opening_mode, encoding='utf-8') as file:
                    redirect_output = output_sh.stdout
                    if input_sh.redirect == STDERR:
                        redirect_output = output_sh.stderr
                    
                    file.write(redirect_output.decode())

                if output_sh.returncode and input_sh.redirect == STDERR:
                    output = output_sh.stdout
                elif input_sh.redirect == STDOUT:
                    output = output_sh.stderr
            print(output.decode(), end='')
        else:
            print(f'{input_sh.command}: command not found')


_commands_ = {
    'echo': f_echo,
    'type': f_type,
    'pwd': f_pwd,
    'external': f_command,
    'cd': f_cd,
}
_path_ = list(
    filterfalse(lambda p: '/mnt' in p or '/home' in p, os.get_exec_path())
)
_builtins_command_ = ['echo', 'type', 'pwd', 'exit', 'cd']
_external_command_ = {cmd for p in _path_ for cmd in get_commands_in_path(p)}


def main():
    readline.set_completer(completer)
    readline.set_completion_display_matches_hook(list_commands_match)
    readline.set_completer_delims('\t')
    readline.parse_and_bind('tab: complete')
    run()

if __name__ == "__main__":
    main()
