import os, subprocess, select, sys, readline
from typing import IO
from datetime import datetime

from .types_shell import InputShell, OutputShell
from .config import STDIN, STDOUT, STDERR, PIPE


def path_exists(path: str) -> bool:
    """Verifica se um caminho existe"""
    return os.path.exists(path)


def find_path_command(paths: list[str], command: str) -> str | None:
    """
    Procura um comando nos caminhos fornecidos.

    Args:
        paths: Lista de caminhos para buscar
        command: Nome do comando
    
    Returns:
        str|None: Caminho completo do comando ou None se não encontrado
    """
    for path in paths:
        path_command = path + '/' + command
        if os.path.exists(path_command) and os.access(path_command, os.X_OK):
            return path_command
    return None


def get_commands_in_path(path: str) -> list[str]:
    """
    Lista todos os comandos executáveis em um caminho.
    
    Args:
        path: Caminho do diretório
        
    Returns:
        Lista de nomes de comandos encontrados
    """
    if os.path.exists(path):
        return [cmd for cmd in os.listdir(path) if os.access(os.path.join(path, cmd), os.X_OK)]
    return []


def input_shell(prompt: str = '$ ') -> tuple[int | None, list[InputShell]]:
    """
    Processa string de entrada, tratando aspas e escapos.
    
    Args:
        args: String bruta de entrada
        
    Returns:
        Lista de argumentos processados
    """
    line_command = input_handler(input(prompt).strip(' '))

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
    """
    Processa string de entrada, tratando aspas e escapos.
    
    Args:
        args: String bruta de entrada
        
    Returns:
        Lista de argumentos processados
    """
    readline.add_history(args)
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


def pipe_execution(commands: list[InputShell], builtin_commands: dict, fn_command_handler) -> None:
    """
    Executa uma sequência de comandos conectados por pipe.
    
    Args:
        commands: Lista de comandos a executar
        builtin_commands: Dicionário de funções de comandos built-in
        fn_command_handler: Função para resolver comandos
    """
    processes: list[OutputShell | subprocess.Popen] = []
    prev_stdout = None
    is_builtin = False

    for i, cmd in enumerate(commands):
        command = [cmd.command] + cmd.args[:]
        builtins = list(builtin_commands.keys())
        
        if cmd.command not in builtins:
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
            if exec_command := fn_command_handler(cmd):
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


def log(text: str, level: str = 'info', sep: str = ' '):
    """
    Envia mensagem de log para o stderr
    """
    from sys import stderr
    t = datetime.now()
    t_exec = f'{t.hour:0>2}:{t.minute:0>2}:{t.second:0>2}'
    print(f'{t_exec} [{level}]{sep}{text}', file=stderr, flush=True)
