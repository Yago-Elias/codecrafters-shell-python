from itertools import filterfalse
import os, sys, subprocess, select
from typing import IO, Any
from .types_shell import *


def find_path_command(paths: list[str], command: str) -> str | None:
    for path in paths:
        path_command = path + '/' + command
        if os.path.exists(path_command) and os.access(path_command, os.X_OK):
            return path_command
    return None


def get_commands_in_path(path: str) -> list[str]:
    if os.path.exists(path):
        return [cmd for cmd in os.listdir(path) if os.access(os.path.join(path, cmd), os.X_OK)]
    return []


def f_echo(input: InputShell) -> OutputShell:
    return OutputShell(bytes((' '.join(input.args) + '\n'), 'utf-8')) 


def f_type(input: InputShell) -> OutputShell:
    output = b''

    for arg in input.args:
        found = False
        output += bytes(f'{arg}', 'utf-8')

        if arg in _builtins_command_:
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


def input_shell() -> tuple[int | None, list[InputShell]]:
    line_command = input_handler(input('$ ').strip(' '))

    if not line_command or line_command[0] == '':
        return (None, [InputShell('', [])])
    
    input_sh = []
    redirect = None
    cmd_ind = 0

    for ind, arg in enumerate(line_command):
        # Detecta pipe
        if '|' == arg:
            command = line_command[cmd_ind]
            args = line_command[cmd_ind+1:ind]
            input_sh.append(InputShell(command, args))
            redirect = PIPE
            cmd_ind = ind + 1
        # Detecta redirecionamento
        elif arg in ('>', '>>', '1>', '1>>', '2>', '2>>'):
            command = line_command[cmd_ind]
            args = line_command[cmd_ind+1:ind]
            redirect = STDERR if arg in ('2>', '2>>') else STDOUT
            if ind + 1 > len(line_command):
                print('syntex error: expected filename')
                return (None, [InputShell('', [])])
            file_name = line_command[ind+1]
            opening_mode = 'w' if arg.count('>') == 1 else 'a'
            input_sh.append(InputShell(command, args, file_name, opening_mode))
            return (redirect, input_sh)
    
    # Adiciona o único ou último comando
    if cmd_ind < len(line_command):
        command = line_command[cmd_ind]
        args = line_command[cmd_ind+1:]
        input_sh.append(InputShell(command, args))
    
    return (redirect, input_sh)


def input_handler(args: str) -> list[str]:
    arg = []
    list_arg = []
    single_quotes = double_quotes = False
    char = iter(args)

    for c in char:
        # escapa o caractere fora de aspas simples e aspas duplas
        if c == "\\" and single_quotes == double_quotes == False:
            arg.append(next(char))
            continue
        
        # tratamento dos argumentos quando não há aspas simples e aspas duplas
        if c.isspace() and not (single_quotes or double_quotes):
            if arg:
                list_arg.append(''.join(arg))
                arg.clear()
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
                    arg.append(c)
                    continue
                else:
                    arg.append('\\')
        arg.append(c)
    
    list_arg.append(''.join(arg))
    return list_arg


def command_handler(input: InputShell) -> Any | None:
    if input.command == 'exit':
        exit()

    command = _commands_.get(input.command)
    if command is None and find_path_command(_path_, input.command):
        command = _commands_.get('external')
    return command


def pipe(*commands: InputShell) -> None:
    processes: list[OutputShell | subprocess.Popen] = []
    prev_stdout = None
    is_builtin = False

    for i, cmd in enumerate(commands):
        command = [cmd.command] + cmd.args[:]
        
        if cmd.command not in _builtins_command_:
            std_pipe = None if i == len(commands) - 1 else subprocess.PIPE
            proc = subprocess.Popen(
                command,
                stdin=prev_stdout,
                stdout=std_pipe,
                stderr=std_pipe
            )
            if isinstance(prev_stdout, IO):
                prev_stdout.close()
            
            prev_stdout = proc.stdout
            if processes and isinstance(processes[-1], OutputShell) and proc.stdin:
                proc.stdin.write(processes[-1].stdout)
                proc.stdin.close()
            processes.append(proc)
        else:
            prev_stdout = subprocess.PIPE
            if exec_command := command_handler(cmd):
                processes.append(exec_command(cmd))
            else:
                msg = f'{cmd.command}: command not found'
                processes.append(OutputShell(stderr=bytes(msg, encoding='utf-8')))

    proc = processes[-1]
    fds = []
    if isinstance(proc, OutputShell):
        sys.stdout.write(proc.stdout.decode())
        sys.stdout.flush()
        is_builtin = True
    else:
        fds = [file for file in [proc.stdout, proc.stderr] if file]
    
    ready_read: list[IO]
    try:
        if is_builtin:
            raise Exception
        while fds:
            ready_read, _, _ = select.select(fds, [], [])
            for fd in ready_read:
                while (out := fd.read(4096)):
                    if is_builtin: continue
                    sys.stdout.buffer.write(out)

                sys.stdout.buffer.flush()
                fd.close()
                fds.remove(fd)
    except (KeyboardInterrupt, Exception) as error:
        if isinstance(error, KeyboardInterrupt):
            sys.stdout.write('\n')
        for proc in processes:
            if isinstance(proc, OutputShell): continue
            proc.terminate()
    finally:
        for proc in processes:
            if isinstance(proc, OutputShell): continue
            proc.wait()


def run() -> None:
    while (True):
        try:
            input_sh = input_shell()
        except KeyboardInterrupt:
            break
        
        _redirect, _sh = input_sh

        if _redirect == PIPE:
            pipe(*_sh)
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
