#!/usr/bin/env python3
import argparse
import subprocess
from enum import Enum


class Conflict:
    def __init__(self, line_number: int, left: str, right: str,
                 sep1: str = '<<<\n', sep2: str = '===\n', sep3: str = '>>>\n'):

        self.line_number = line_number
        self.left = left
        self.right = right

        self.sep1 = sep1
        self.sep2 = sep2
        self.sep3 = sep3

        self._select = None

    def select_left(self):
        self._select = self.left

    def select_right(self):
        self._select = self.right

    def select_both(self):
        self._select = self.left + self.right

    def result(self) -> str:
        if self._select:
            return self._select
        else:
            return self.sep1 + self.left + self.sep2 + self.right + self.sep3


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
            bits += _file_bits.pop(0).text
        else:
            bits += _conflicts.pop(0).result()

    return "".join(bits)


def compile_text(program: str):
    buf_path = '~buffer.cpp'

    buf = open(buf_path, 'w')
    buf.write(program)
    buf.close()

    try:
        # out, err = subprocess.check_output(["g++", buf_path])

        compiler = subprocess.Popen(["g++", buf_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = compiler.communicate()
        print(out.decode())
        print(err.decode())

        if not err:
            print("The code has been compiled with no errors")

    except subprocess.CalledProcessError:
        print("Compiler terminated unexpectedly")


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

    return file_bits, conflicts


# changes `conflicts`
def resolve_conflicts_event_loop(file_bits: [FileBit], conflicts: [Conflict]):
    unresolved_conflicts = list(range(len(conflicts)))
    unresolved_conflict_index = 0
    while True:
        if not unresolved_conflicts:
            print("All conflicts have been resolved")
            compile_text(combined_file(file_bits, conflicts))
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

        if not response:
            continue

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
            compile_text(combined_file(file_bits, conflicts))
        elif switch == 'q':
            print("Left unresolved %d conflicts" % len(unresolved_conflicts))
            break
        else:
            continue


def parse_cli_args():
    parser = argparse.ArgumentParser(description='Resolves conflicts in a file')

    parser.add_argument('file', default='prog.cpp', help='file to resolve')
    parser.add_argument('--verbose', dest='verbose', action='store_true')

    defaul_behaviour_group = parser.add_mutually_exclusive_group()
    defaul_behaviour_group.add_argument('-ours', action='store_true')
    defaul_behaviour_group.add_argument('-theirs', action='store_true')
    defaul_behaviour_group.add_argument('-union', action='store_true')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cli_args()

    file_stream = open(args.file, 'r', encoding="latin-1")

    File_bits, Conflicts = parse_stream_into_conflicts(file_stream)

    if args.ours:
        for conflict in Conflicts:
            conflict.select_left()
    elif args.theirs:
        for conflict in Conflicts:
            conflict.select_right()
    elif args.union:
        for conflict in Conflicts:
            conflict.select_both()
    else:
        resolve_conflicts_event_loop(File_bits, Conflicts)

    result = combined_file(File_bits, Conflicts)
    print(result)

    compile_text(result)


