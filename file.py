import subprocess
from enum import Enum


class Conflict:
    def __init__(self, line_number: int, left: str, right: str):
        self.line_number = line_number
        self.left = left
        self.right = right
        self.select = None

    def select_left(self):
        self.select = self.left

    def select_right(self):
        self.select = self.right

    def select_both(self):
        self.select = self.left + self.right


class FileBit:
    def __init__(self, line_number: int, text: str):
        self.line_number = line_number
        self.text = text


def combined_file(file_bits: [FileBit], conflicts: [Conflict]) -> str:
    _file_bits = file_bits[:]
    _conflicts = conflicts[:]
    bits = []
    for i in range(len(file_bits) + len(conflicts)):
        if i % 2 == 0:
            bits += file_bits.pop(0).text
        else:
            bits += conflicts.pop(0).select

    return "".join(bits)


def compilate(file_bits: [FileBit], conflicts: [Conflict]):
    fout = open('code.cpp', 'w')
    fout.write(combined_file(file_bits, conflicts))
    fout.close()
    subprocess.check_output(["g++", "code.cpp"])


def parse_stream_into_conflicts(stream) -> ([FileBit], [Conflict]):
    class State(Enum):
        text = 1
        left = 2
        right = 3

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
            else:
                file_bit.text += line

        elif State.left == state:
            if switch == "===":
                state = State.right
            else:
                conflict.left += line

        elif State.right == state:
            if switch == ">>>":
                state = State.text
                conflicts.append(conflict)
                conflict = Conflict(-1, "", "")
                file_bit.line_number = index + 1
            else:
                conflict.right += line

        else:
            raise ValueError

    file_bits.append(file_bit)

    return file_bits, conflicts


# changes `conflicts`
def resolve_conflicts_event_loop(file_bits: [FileBit], conflicts: [Conflict]):
    unresolved_conflicts = list(range(len(conflicts)))
    unresolved_conflict_index = 0
    while True:
        if not unresolved_conflicts:
            print("All conflicts have been resolved")
            break

        unresolved_conflict_index %= len(unresolved_conflicts)
        conflict = conflicts[unresolved_conflicts[unresolved_conflict_index]]

        print("\n left = ")
        print(conflict.left)
        print("\n right = ")
        print(conflict.right)

        response = input(
            "Choose what to leave ('R' = right, 'L' = left, 'B' = both, "
            "'N' = next conflict, 'P' = previous conflict 'C' = compile, 'Q' = quit): \n")

        switch = response.lower()[0]

        if switch == 'l':
            conflict.select_left()
            unresolved_conflicts.pop(unresolved_conflict_index)
            unresolved_conflict_index += 1
        elif switch == 'r':
            conflict.select_right()
            unresolved_conflicts.pop(unresolved_conflict_index)
            unresolved_conflict_index += 1
        elif switch == 'b':
            conflict.select_both()
            unresolved_conflicts.pop(unresolved_conflict_index)
            unresolved_conflict_index += 1
        elif switch == 'p':
            unresolved_conflict_index -= 1
        elif switch == 'n':
            unresolved_conflict_index += 1
        elif switch == 'c':
            compilate(file_bits, conflict)
        elif switch == 'q':
            print("Left unresolved %d conflicts" % len(unresolved_conflicts))
            break
        else:
            continue


file_stream = open('prog.cpp', 'r', encoding="latin-1")

File_bits, Conflicts = parse_stream_into_conflicts(file_stream)

# conflictServe(conflicts_list, 0)

resolve_conflicts_event_loop(File_bits, Conflicts)

result = combined_file(File_bits, Conflicts)
print(result)


