from enum import Enum
from pathlib import Path

from merge.Conflict import Conflict
from merge.FileBit import FileBit


class FileMerge:
    def __init__(self, path: Path, file_bits: [FileBit], conflicts: [Conflict]):
        self.path = path
        self.file_bits = file_bits
        self.conflicts = conflicts

    def is_resolved(self):
        return len([c for c in self.conflicts if not c.is_resolved()]) == 0

    def select_all_left(self):
        for conflict in self.conflicts:
            conflict.select_left()

    def select_all_right(self):
        for conflict in self.conflicts:
            conflict.select_right()

    def select_all_both(self):
        for conflict in self.conflicts:
            conflict.select_both()

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