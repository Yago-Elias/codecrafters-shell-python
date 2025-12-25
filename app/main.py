import sys


def main():
    while (True):
        sys.stdout.write("$ ")
        command = input().split(' ')

        if command[0] == 'exit':
            return
        elif command[0] == 'echo':
            print(' '.join(command[1:]))
        else:
            print(f'{command[0]}: command not found')


if __name__ == "__main__":
    main()
