import sys


def main():
    commands = ['exit', 'echo', 'type']

    while (True):
        sys.stdout.write("$ ")
        command = input().split(' ')

        if command[0] == 'exit':
            return
        elif command[0] == 'echo':
            print(' '.join(command[1:]))
        elif command[0] == 'type':
            print(f'{command[1]}', end='')
            print(' is a shell builtin' if command[1] in commands else ': not found')
        else:
            print(f'{command[0]}: command not found')


if __name__ == "__main__":
    main()
