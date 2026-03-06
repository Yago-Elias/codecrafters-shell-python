from collections import namedtuple
from enum import Enum


InputShell = namedtuple('InputShell', [
    'command', 
    'args', 
    'file_name', 
    'opening_mode' 
    ], 
    defaults=['', None, '', ''])

OutputShell = namedtuple('OutputShell', [
    'stdout', 
    'stderr', 
    'returncode' 
    ], 
    defaults=[b'', b'', 0])

STDIN = 0
STDOUT = 1
STDERR = 2
PIPE = 3


class Type(Enum):
    BUILTIN = 1
    EXTERNAL = 2
