import readline
from .types_shell import *
from .builtins_shell import *
from .completion_shell import *

def main():
    readline.set_completer(completer)
    readline.set_completion_display_matches_hook(list_commands_match)
    readline.set_completer_delims('\t')
    readline.parse_and_bind('tab: complete')
    run()

if __name__ == "__main__":
    main()
