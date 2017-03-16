from enum import Enum
from pathlib import Path

from .choice import Choice
from .conflict import Conflict, ConflictBuilder
from .conflict import Conflict3Way
from .file_bit import FileBit


class FileMergeChoice:
    pass


class FileMerge:
    def __init__(self, path: Path, file_bits: [FileBit], conflicts: [Conflict]):
        self.path = path
        self.file_bits = file_bits
        self.conflicts = conflicts

    def is_resolved(self):
        return len([c for c in self.conflicts if not c.is_resolved()]) == 0

    def select_all(self, choice: Choice):
        for conflict in self.conflicts:
            conflict.select(choice)

    def result(self) -> str:
        _file_bits = self.file_bits[:]
        _conflicts = self.conflicts[:]
        bits = []
        for i in range(len(_file_bits) + len(_conflicts)):
            if i % 2 == 0:
                bits += _file_bits.pop(0).text
            else:
                bits += _conflicts.pop(0).result()

        return "".join(bits)

    @staticmethod
    def parse(path: Path):  # -> FileMerge:
        class State(Enum):
            text = 1
            base = 2
            left = 3
            right = 4

        stream = path.open('r', encoding="latin-1")

        fileobj_lines = stream.readlines()
        file_bits = []
        conflicts = []

        state = State.text
        file_bit = FileBit(0, "")
        conflict = ConflictBuilder()

        for index, line in enumerate(fileobj_lines):
            switch = line[0:7]

            if State.text == state:
                if switch == ConflictBuilder.sep1_marker:
                    state = State.left
                    file_bits.append(file_bit)
                    file_bit = FileBit(0, "")
                    conflict.line_number = index
                    conflict.sep1 = line
                else:
                    file_bit.text += line

            elif State.left == state:
                if switch == ConflictBuilder.sep_base_marker:
                    state = State.base
                    conflict.has_base = True
                    conflict.sep_base = line
                elif switch == ConflictBuilder.sep2_marker:
                    state = State.right
                    conflict.sep2 = line
                else:
                    conflict.left += line

            elif State.base == state:
                if switch == ConflictBuilder.sep2_marker:
                    state = State.right
                    conflict.sep2 = line
                else:
                    conflict.base += line

            elif State.right == state:
                if switch == ConflictBuilder.sep3_marker:
                    state = State.text
                    conflict.sep3 = line
                    conflicts.append(conflict.build())
                    conflict = ConflictBuilder()
                    file_bit.line_number = index + 1
                else:
                    conflict.right += line

            else:
                raise ValueError

        file_bits.append(file_bit)

        return FileMerge(path, file_bits, conflicts)
