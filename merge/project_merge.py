import shutil
import subprocess
import sys
from pathlib import Path

from .choice import Choice
from .file_merge import FileMerge


class ProjectMergeChoise:
    pass


class ProjectMerge:
    def __init__(self, path: Path, tmp_path: Path, files: [FileMerge]):
        self.path = path
        self.tmp_path = tmp_path
        self.files = files

    def is_resolved(self):
        return len([f for f in self.files if not f.is_resolved()]) == 0

    def select_all(self, choice: Choice):
        for file in self.files:
            file.select_all(choice)

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
        for file in path.iterdir():
            merges.append(FileMerge.parse(file))

        return ProjectMerge(path, tmp_path, merges)
