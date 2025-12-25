import sys
import os
import subprocess
from itertools import filterfalse


def find_path_command(paths: list[str], command: str) -> str | None:
    for path in paths:
        path_command = path + '/' + command
        if os.path.exists(path_command) and os.access(path_command, os.X_OK):
            return path_command
    return None


def main():
    builtin_commands = ['exit', 'echo', 'type']
    input_sh = {'command': '', 'args': ''}
    path = list(
        filterfalse(lambda p: '/mnt' in p or '/home' in p, os.get_exec_path())
    )
    is_builtin = False

    while (True):
        sys.stdout.write("$ ")

        input_aux = input().split(' ')
        input_sh['command'] = input_aux[0]
        input_sh['args'] = ' '.join(input_aux[1:])
        is_builtin = False

        if input_sh['command'] == 'exit':
            return
        elif input_sh['command'] == 'echo':
            print(input_sh['args'])
        elif input_sh['command'] == 'type':
            print(f'{input_sh['args']}', end='')

            if input_sh['args'] in builtin_commands:
                is_builtin = True
                print(' is a shell builtin')
            else:
                path_command = find_path_command(path, input_sh['args'])
                if path_command and os.path.exists(path_command) and os.access(path_command, os.X_OK):
                    is_builtin = True
                    print(f' is {path_command}')
            if not is_builtin:
                print(': not found')
        elif find_path_command(path, input_sh['command']):
            command = [input_sh['command']]
            if input_sh['args']:
                command.append(input_sh['args'])
            result = subprocess.run(command, capture_output=True).stdout
            print(result.decode(), end='')
        else:
            print(f'{input_sh['command']}: command not found')


if __name__ == "__main__":
    main()
