from .builtins_shell import (
    input_handler, 
    _builtins_command_, 
    _external_command_
)
import os
import readline, sys


def list_path(path: str) -> tuple[str, list[str], str]:
    head, tail = os.path.split(path)
    if os.path.exists(head) == False:
        return ('', [], '')
    
    files = os.listdir(head)
    return head, files, tail


def completer(text: str, state: int):
    search = text
    matches = [cmd for cmd in _builtins_command_ if cmd.startswith(text)]
    path = ''
    if not matches:
        matches = [cmd for cmd in _external_command_ if cmd.startswith(text)]
    
    buffer = input_handler(readline.get_line_buffer())
    if len(buffer) > 1:
        if text.find('/') == -1:
            files = os.listdir()
        else:
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
    buffer = readline.get_line_buffer()
    print()
    basenames = list(map(lambda bn: bn[:-1] if bn[-1] == '/' else bn, matches))

    # print(f'debug\nbn: {basenames}', flush=True)
    basenames = list(map(os.path.split, basenames))
    # path = './' if basenames[0][0] == '' else basenames[0][0]
    # print(f'\npath: {path}', flush=True)
    basenames = list(
        map(
            lambda bn: bn[1] + '/' if os.path.isdir(os.path.join(*bn)) else bn[1],
            basenames
            )
        )

    # print(f'debug\nbn: {basenames}', flush=True)
    
    print(' '.join(basenames), flush=True)
    sys.stdout.write('\033[K')
    sys.stdout.write(f'$ {buffer}')
    sys.stdout.flush()
    readline.redisplay()
