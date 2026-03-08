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


class CommandType(Enum):
    """Tipos de comandos suportados"""
    BUILTIN = 1
    EXTERNAL = 2


__all__ = [
    'InputShell', 'OutputShell', 'CommandType'
]
