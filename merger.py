#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path
import shutil
from enum import Enum

import sys


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

    def is_resolved(self) -> bool:
        return self._select is not None

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


class ProjectMerge:
    def __init__(self, path: Path, tmp_path: Path, files: [FileMerge]):
        self.path = path
        self.tmp_path = tmp_path
        self.files = files

    def is_resolved(self):
        return len([f for f in self.files if not f.is_resolved()]) == 0

    def select_all_left(self):
        for file in self.files:
            file.select_all_left()

    def select_all_right(self):
        for file in self.files:
            file.select_all_right()

    def select_all_both(self):
        for file in self.files:
            file.select_all_both()

    def write_result(self):
        if self.tmp_path.exists():
            if self.tmp_path.is_dir():
                shutil.rmtree(str(self.tmp_path))
            else:
                raise ValueError("`tmp_path` is supposed to be a directory (if exists)", self.tmp_path)

        self.tmp_path.mkdir()

        for file in self.files:
            relative_path = file.path.relative_to(self.path)
            path = self.tmp_path / relative_path

            path.write_text(file.result(), encoding="latin-1")

    def compile_print(self):
        self.write_result()

        try:
            # out, err = subprocess.check_output(["g++", buf_path])

            compiler = subprocess.Popen(["make", "--directory=%s" % self.tmp_path],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = compiler.communicate()
            print(out.decode())
            print(err.decode(), file=sys.stderr)

            if not err:
                print("The project has been build with no errors")

        except subprocess.CalledProcessError:
            print("Make terminated unexpectedly")


    @staticmethod
    def parse(path: Path, tmp_path: Path):  # -> ProjectMerge:
        merges = []
        for file in project_path.iterdir():
            merges.append(FileMerge.parse(file))

        return ProjectMerge(path, tmp_path, merges)


### changes `conflicts`
def resolve_conflicts_event_loop(project_merge: ProjectMerge, file_merge_index: int):
    file_merge = project_merge.files[file_merge_index]

    if file_merge.is_resolved():
        return

    unresolved_conflicts = list(range(len(file_merge.conflicts)))
    unresolved_conflict_index = 0
    while True:
        if not unresolved_conflicts:
            print("All conflicts have been resolved")
            project_merge.compile_print()
            break

        unresolved_conflict_index %= len(unresolved_conflicts)
        conflict = file_merge.conflicts[unresolved_conflicts[unresolved_conflict_index]]

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
            project_merge.compile_print()
        elif switch == 'q':
            print("Left unresolved %d conflicts" % len(unresolved_conflicts))
            break
        else:
            continue


def parse_cli_args():
    parser = argparse.ArgumentParser(description='Resolves conflicts in a file')

    parser.add_argument('project_path', default='.', help='folder with the top-level Makefile')
    parser.add_argument('--verbose', dest='verbose', action='store_true')

    defaul_behaviour_group = parser.add_mutually_exclusive_group()
    defaul_behaviour_group.add_argument('-ours', action='store_true')
    defaul_behaviour_group.add_argument('-theirs', action='store_true')
    defaul_behaviour_group.add_argument('-union', action='store_true')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cli_args()
    project_path = Path(args.project_path)

    if not project_path.is_dir():
        print("%s is not a folder" % project_path)
        quit()

    makefile_path = project_path / "Makefile"
    if not makefile_path.is_file():
        print("Could not find a Makefile at %s" % makefile_path)
        print("Unable to build the project")
        quit()

    tmp_path = project_path.parent / ("~" + str(project_path.parts[-1]))
    merge = ProjectMerge.parse(project_path, tmp_path)

    if merge.is_resolved():
        print("The project %s has no conflicts to resolve" % project_path)
        quit()

    if [f for f in merge.files if f.path == makefile_path and not f.is_resolved()]:
        print("Makefile cannot be in the merging state")
        quit()

    # TODO: incapsulate
    for index in range(len(merge.files)):
        resolve_conflicts_event_loop(merge, index)  # changes `merge`

    merge.compile_print()
