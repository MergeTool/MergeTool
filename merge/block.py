from clang.cindex import Cursor, CursorKind
from .cursor_utils import *


class Block:
    """ A block of code which should not be mixed up """

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    @staticmethod
    def from_cursor(cursor: Cursor):
        return Block(cursor.start, cursor.end)

    @staticmethod
    def structure_of_IF(cursor: Cursor):  # -> [Block]
        assert cursor.kind == CursorKind.IF_STMT

        children = list(cursor.get_children())
        ch1 = children[1]

        if len(children) > 2:
            ch2 = children[2]

            if ch1.is_compound and ch2.is_compound:         # if {} else {} ;
                return [Block.from_cursor(ch1), Block.from_cursor(ch2),
                        Block(cursor.start, ch1.end), Block(cursor.start, ch2.end)]

            elif not ch1.is_compound and ch2.is_compound:   # if ... else {} ;
                return [Block.from_cursor(ch2), Block(cursor.start, ch1.end), Block(cursor.start, ch2.end)]

            elif ch1.is_compound and not ch2.is_compound:   # if {} else ... ;
                return [Block.from_cursor(ch1), Block(cursor.start, ch1.end), Block(cursor.start, ch2.end)]

            else:                                           # if ... else ... ;
                return [Block(cursor.start, ch1.end), Block(cursor.start, ch2.end)]
        else:
            if ch1.is_compound:   # if {} ;
                return [Block(ch1.start, ch1.end), Block(cursor.start, ch1.end)]
            else:                 # if ... ;
                return [Block(cursor.start, ch1.end)]
