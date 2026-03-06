from .builtins_shell import _builtins_command_, _external_command_
import readline, sys


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