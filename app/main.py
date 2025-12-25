import sys
import os
from itertools import filterfalse


def main():
    commands = ['exit', 'echo', 'type']
    
    path = list(
        filterfalse(lambda p: '/mnt' in p or '/home' in p, os.get_exec_path())
    )


    while (True):
        sys.stdout.write("$ ")
        command = input().split(' ')
        is_builtin = False

        if command[0] == 'exit':
            return
        elif command[0] == 'echo':
            print(' '.join(command[1:]))
        elif command[0] == 'type':
            print(f'{command[1]}', end='')

            if command[1] in commands:
                is_builtin = True
                print(' is a shell builtin')
            else:
                for p in path:
                    path_command = '/'.join([p, command[1]])
                    if os.path.exists(path_command) and os.access(path_command, os.X_OK):
                        is_builtin = True
                        print(f' is {path_command}')
                        break
            if not is_builtin:
                print(': not found')
        else:
            print(f'{command[0]}: command not found')


if __name__ == "__main__":
    main()
