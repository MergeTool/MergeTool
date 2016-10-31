import re
from enum import Enum
from pathlib import Path

from clang.cindex import TranslationUnit, Index, TranslationUnitLoadError, Cursor, CursorKind, SourceLocation

from .choice import Choice
from .conflict import Conflict
from .file_bit import FileBit


class FileMergeChoice:
    pass


class FileMerge:
    def __init__(self, path: Path, file_bits: [FileBit], conflicts: [Conflict]):
        self.path = path
        self.file_bits = file_bits
        self.conflicts = conflicts
        self._translation_unit = None

    def is_resolved(self):
        return len([c for c in self.conflicts if not c.is_resolved()]) == 0

    def select_all(self, choice: Choice):
        for conflict in self.conflicts:
            conflict.select(choice)

    def result(self, choice: Choice = None) -> str:
        _file_bits = self.file_bits[:]
        _conflicts = self.conflicts[:]
        bits = []
        for i in range(len(_file_bits) + len(_conflicts)):
            if i % 2 == 0:
                bits += _file_bits.pop(0).text
            else:
                bits += _conflicts.pop(0).result(choice)

        return "".join(bits)

    @property
    def abstract_syntax_tree(self) -> TranslationUnit:
        """ AST of the `left` version of this file or `None` if a error occurred """
        """ The result is cashed """
        if self._translation_unit:
            return self._translation_unit

        text = self.result(Choice.left)
        text = re.sub(r'#include((<\w+>)|("\w+"))', '', text)  # TODO: hack

        filename = str(self.path)
        index = Index.create()
        try:
            self._translation_unit = index.parse(filename, unsaved_files=[(filename, text)])
        except TranslationUnitLoadError:
            pass

        return self._translation_unit

    def refactor_syntax_blocks(self):
        """ Only `if` is supported by now """
        ast = self.abstract_syntax_tree
        if not ast:
            return

        ifs = FileMerge.extract_children(ast.cursor, [CursorKind.IF_STMT])

        print(ifs)

    @staticmethod
    def extract_children(root: Cursor, kind_list: [CursorKind] = []) -> [Cursor]:
        nodes = []
        try:
            if root.kind in kind_list:
                nodes.append(root)
        except ValueError:
            pass

        for ch in root.get_children():
            nodes.extend(FileMerge.extract_children(ch))

        return nodes

    @staticmethod
    def parse(path: Path):  # -> FileMerge:
        class State(Enum):
            text = 1
            left = 2
            right = 3

        stream = path.open('r', encoding="latin-1")

        fileobj_lines = stream.readlines()
        file_bits = []
        conflicts = []

        state = State.text
        file_bit = FileBit(0, "")
        conflict = Conflict(-1, "", "")

        for index, line in enumerate(fileobj_lines):
            switch = line[0:3]

            if State.text == state:
                if switch == "<<<":
                    state = State.left
                    file_bits.append(file_bit)
                    file_bit = FileBit(0, "")
                    conflict.line_number = index
                    conflict.sep1 = line
                else:
                    file_bit.text += line

            elif State.left == state:
                if switch == "===":
                    state = State.right
                    conflict.sep2 = line
                else:
                    conflict.left += line

            elif State.right == state:
                if switch == ">>>":
                    state = State.text
                    conflict.sep3 = line
                    conflicts.append(conflict)
                    conflict = Conflict(-1, "", "")
                    file_bit.line_number = index + 1
                else:
                    conflict.right += line

            else:
                raise ValueError

        file_bits.append(file_bit)

        return FileMerge(path, file_bits, conflicts)
