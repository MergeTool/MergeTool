from clang.cindex import Cursor, CursorKind


def get_child(self: Cursor, n: int) -> Cursor:
    return list(self.get_children())[n]


def short_info(self: Cursor):
    return "%s at %d with %d kid(s)" % (self.kind.name, self.extent.start.line, len(list(self.get_children())))


Cursor.child = get_child
Cursor.__str__ = short_info

Cursor.start = property(lambda self: self.extent.start.line)
Cursor.end = property(lambda self: self.extent.end.line)
Cursor.is_compound = property(lambda self: self.kind == CursorKind.COMPOUND_STMT)
