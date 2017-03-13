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

    def abstract_syntax_tree(self, choice: Choice = Choice.left) -> TranslationUnit:
        """ AST of the `choice` version of this file or `None` if a error occurred """
        """ The result is cashed """
        if self._translation_unit:
            return self._translation_unit

        text = self.result(choice)  # TODO: generalise to left and right
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
        _choice = Choice.left
        ast = self.abstract_syntax_tree(_choice)
        if not ast:
            return

        if_blocks = FileMerge.extract_children(ast.cursor, [CursorKind.IF_STMT])

        print(if_blocks)

        for block in if_blocks:
            intersecting_conflicts = [conflict for conflict in self.conflicts
                                      if block.extent.start.line <= conflict.start(_choice) <=
                                      block.extent.end.line <= conflict.end(_choice)]

            if len(intersecting_conflicts) > 0:
                conflict = intersecting_conflicts[0]
                i = self.conflicts.index(conflict)
                file_bit = self.file_bits[i]
                # assert file_bit.line_number + len(file_bit.text.splitlines()) == conflict.line_number

                num = conflict.start(_choice) - block.extent.start.line + 1
                chunk = file_bit.shrink_bottom_up(num)
                conflict.extend_top_up(chunk)

        for block in if_blocks:
            intersecting_conflicts = [conflict for conflict in self.conflicts
                                      if conflict.start(_choice) <= block.extent.start.line <=
                                      conflict.end(_choice) <= block.extent.end.line]

            if len(intersecting_conflicts) > 0:
                conflict = intersecting_conflicts[0]
                i = self.conflicts.index(conflict)
                file_bit = self.file_bits[i + 1]
                # assert file_bit.line_number == conflict.line_number + len(conflict.result(Choice.undesided).splitlines())

                num = block.extent.end.line - conflict.end(_choice)
                chunk = file_bit.shrink_top_down(num)
                conflict.extend_bottom_down(chunk)


    @staticmethod
    def extract_children(root: Cursor, kind_list: [CursorKind]) -> [Cursor]:
        nodes = []
        try:
            if root.kind in kind_list:
                nodes.append(root)
        except ValueError:
            pass

        for ch in root.get_children():
            nodes.extend(FileMerge.extract_children(ch, kind_list))

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
        conflict = Conflict(-1, -1, -1, "", "")

        line_num_left = 0
        line_num_right = 0
        for index, line in enumerate(fileobj_lines):
            switch = line[0:3]

            if state == State.text:
                if switch == "<<<":
                    state = State.left
                    file_bits.append(file_bit)
                    file_bit = FileBit(0, "")
                    conflict.line_number = index
                    conflict.line_num_left = line_num_left
                    conflict.sep1 = line
                else:
                    file_bit.text += line
                    line_num_left += 1
                    line_num_right += 1

            elif state == State.left:
                if switch == "===":
                    state = State.right
                    conflict.line_num_right = line_num_right
                    conflict.sep2 = line
                else:
                    conflict.left += line
                    line_num_left += 1

            elif state == State.right:
                if switch == ">>>":
                    state = State.text
                    conflict.sep3 = line
                    conflicts.append(conflict)
                    conflict = Conflict(-1, -1, -1, "", "")
                    file_bit.line_number = index + 1
                else:
                    conflict.right += line
                    line_num_right += 1

            else:
                raise ValueError

        file_bits.append(file_bit)

        return FileMerge(path, file_bits, conflicts)

    @staticmethod
    def can_parse(path: Path) -> bool:
        allowed_extensions = [".cpp", ".c", ".hpp", ".h"]
        return path.suffix in allowed_extensions
