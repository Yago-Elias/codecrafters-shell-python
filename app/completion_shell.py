from .builtins_shell import (
    input_handler, 
    _builtins_command_, 
    _external_command_
)
import os
import readline, sys


def list_path(path: str) -> tuple[str, list[str], str]:
    dir = os.path.dirname(path)
    prefix = os.path.basename(path)
    # print(f'debug: path<{dir}/{prefix}>', flush=True)
    if os.path.exists(dir) == False:
        return ('', [], '')
    
    files = os.listdir(dir)
    # print(f'debug: files<{files}>', flush=True)
    return dir, files, prefix


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
            # print(path, files, search, flush=True)
        
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

    if os.path.commonpath(matches): 
        basenames = list(map(os.path.basename, basenames))
    
    print(' '.join(basenames), flush=True)
    sys.stdout.write('\033[K')
    sys.stdout.write(f'$ {buffer}')
    sys.stdout.flush()
    readline.redisplay()
