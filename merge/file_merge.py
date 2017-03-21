import re
from enum import Enum
from pathlib import Path

from clang.cindex import TranslationUnit, Index, TranslationUnitLoadError, Cursor, CursorKind
from io import TextIOBase

from .choice import Choice
from .conflict import ConflictBuilder, Conflict
from .file_bit import FileBit


class FileMerge:
    def __init__(self, path: Path, file_bits: [FileBit], conflicts: [Conflict]):
        self.path = path
        self.file_bits = file_bits
        self.conflicts = conflicts
        self._translation_unit = None
        self._translation_unit_choice = None

    def is_resolved(self):
        return len([c for c in self.conflicts if not c.is_resolved()]) == 0

    def select_all(self, choice: Choice):
        for conflict in self.conflicts:
            conflict.select(choice)

    def result(self, choice: Choice = None) -> str:
        if len(self.file_bits) == 1 and len(self.conflicts) == 0:
            return self.file_bits[0].text

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
        """
        AST of the `choice` version of this file or `None` if an error occurred

        The last result is cashed
        """
        if self._translation_unit and self._translation_unit_choice == choice:
            return self._translation_unit

        if not FileMerge.can_parse(self.path):
            raise RuntimeError("This file extension is not supported")

        text = self.result(choice)
        text = re.sub(r'#include((<\w+>)|("\w+"))', '', text)  # TODO: hack

        filename = str(self.path)
        index = Index.create()
        try:
            self._translation_unit_choice = choice
            self._translation_unit = index.parse(filename, unsaved_files=[(filename, text)])
        except TranslationUnitLoadError:
            pass

        return self._translation_unit

    def refactor_syntax_blocks(self):
        """ Only `if` is supported by now """

        if len(self.conflicts) == 0:
            return

        _choice = Choice.left
        ast = self.abstract_syntax_tree(_choice)
        if not ast:
            return

        if_statements = FileMerge.extract_children(ast.cursor, [CursorKind.IF_STMT])
        if_blocks = [b for stmt in if_statements for b in list(stmt.get_children())[1:]]
        all_blocks = FileMerge.extract_children(ast.cursor, [CursorKind.COMPOUND_STMT])

        blocks = if_statements + if_blocks

        # situation: `{ <<< } >>>`
        for block in blocks:
            intersecting_conflicts = [conflict for conflict in self.conflicts
                                      if block.extent.start.line < conflict.start(_choice) <=
                                      block.extent.end.line < conflict.end(_choice)]

            if len(intersecting_conflicts) > 0:
                conflict = intersecting_conflicts[0]
                i = self.conflicts.index(conflict)
                file_bit = self.file_bits[i]
                # assert file_bit.line_number + len(file_bit.text.splitlines()) == conflict.line_number

                num = conflict.start(_choice) - block.extent.start.line
                chunk = file_bit.shrink_bottom_up(num)
                conflict.extend_top_up(chunk)

        # situation: `<<< { >>> }`
        for block in blocks:
            intersecting_conflicts = [conflict for conflict in self.conflicts
                                      if conflict.start(_choice) <= block.extent.start.line <
                                      conflict.end(_choice) <= block.extent.end.line]

            if len(intersecting_conflicts) > 0:
                conflict = intersecting_conflicts[0]
                i = self.conflicts.index(conflict)
                file_bit = self.file_bits[i + 1]
                # assert file_bit.line_number == conflict.line_number + len(conflict.result(Choice.undecided).splitlines())

                num = block.extent.end.line - conflict.end(_choice) + 1
                chunk = file_bit.shrink_top_down(num)
                conflict.extend_bottom_down(chunk)

    @staticmethod
    def _get_children_recursive(cursor: Cursor):
        """ Returns a one-go iterator for efficiency """
        for ch in cursor.get_children():
            yield ch
            for r_ch in FileMerge._get_children_recursive(ch):
                yield r_ch

    @staticmethod
    def extract_children(root: Cursor, kind_list: [CursorKind]) -> [Cursor]:
        nodes = []

        for node in FileMerge._get_children_recursive(root):
            try:
                if node.kind in kind_list:
                    nodes.append(node)
            except ValueError:
                pass

        return nodes

    @staticmethod
    def parse(path: Path, stream: TextIOBase):  # -> FileMerge:
        """ Note that the number of the first line of a file is `1` """
        class State(Enum):
            text = 1
            left = 2
            base = 3
            right = 4

        assert stream.readable()

        if not FileMerge.can_parse(path):
            text = path.read_text(encoding="latin-1")
            return FileMerge(path, [FileBit(1, text)], [])

        fileobj_lines = stream.readlines()
        file_bits = []
        conflicts = []

        state = State.text
        file_bit = FileBit(1, "")
        conflict = ConflictBuilder()

        line_num_left = 1
        line_num_right = 1
        for index, line in enumerate(fileobj_lines):
            switch = line[0:7]

            line_number = index + 1  # the first line of a file is #1

            if state == State.text:
                if switch == ConflictBuilder.sep1_marker:
                    state = State.left
                    file_bits.append(file_bit)
                    file_bit = FileBit(-1, "")  # the `line_number` will be overridden
                    conflict.line_number = line_number
                    conflict.line_num_left = line_num_left
                    conflict.sep1 = line
                else:
                    file_bit.text += line
                    line_num_left += 1
                    line_num_right += 1

            elif state == State.left:
                if switch == ConflictBuilder.sep2_marker:
                    state = State.base
                    conflict.has_base = True
                    conflict.sep2 = line
                elif switch == ConflictBuilder.sep3_marker:
                    state = State.right
                    conflict.has_base = False
                    conflict.line_num_right = line_num_right
                    conflict.sep3 = line
                else:
                    conflict.left += line
                    line_num_left += 1

            elif state == State.base:
                if switch == ConflictBuilder.sep3_marker:
                    state = State.right
                    conflict.line_num_right = line_num_right
                    conflict.sep3 = line
                else:
                    conflict.base += line

            elif state == State.right:
                if switch == ConflictBuilder.sep4_marker:
                    state = State.text
                    conflict.sep4 = line
                    conflicts.append(conflict.build())
                    conflict = ConflictBuilder()
                    file_bit.line_number = line_number + 1
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
