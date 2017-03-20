from io import StringIO
from pathlib import Path
from unittest import TestCase

from merge.file_merge import FileMerge


def multiline(text: str) -> str:
    from textwrap import dedent
    return dedent(text).strip()


class TestNoRefactor(TestCase):
    @classmethod
    def setUpClass(cls):
        from merge.external_parser_setup import ExternalParserSetup
        ExternalParserSetup.setup()

    def test_conflict_after_raw_if(self):
        code = multiline("""
        int main() {
            if(1 > 2)
                printf("Hello!")
        <<<<<<< HEAD
            int n = 0;
            n += 1;
        =======
            int x = 0;
            x -= 3;
        >>>>>>> master
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_after_if_block(self):
        code = multiline("""
        int main() {
            if(1 > 2) {
                printf("Hello!")
            }
        <<<<<<< HEAD
            int n = 0;
            n += 1;
        =======
            int x = 0;
            x -= 3;
        >>>>>>> master
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_before_if_block(self):
        code = multiline("""
        int main() {
        <<<<<<< HEAD
            int n = 0;
            n += 1;
        =======
            int x = 0;
            x -= 3;
        >>>>>>> master
            if(1 > 2) {
                printf("Hello!")
            }
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_inside_if_block(self):
        code = multiline("""
        int main() {
            if(1 > 2) {
        <<<<<<< HEAD
                int n = 0;
                n += 1;
        =======
                int x = 0;
                x -= 3;
        >>>>>>> master
            }
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_inside_if_block_at_end(self):
        code = multiline("""
        int main() {
            if(1 > 2) {
                printf("Hello!")
        <<<<<<< HEAD
                int n = 0;
                n += 1;
        =======
                int x = 0;
                x -= 3;
        >>>>>>> master
            }
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_inside_if_block_at_start(self):
        code = multiline("""
        int main() {
            if(1 > 2) {
        <<<<<<< HEAD
                int n = 0;
                n += 1;
        =======
                int x = 0;
                x -= 3;
        >>>>>>> master
                printf("Hello!")
            }
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_outside_if_block(self):
        code = multiline("""
        int main() {
        <<<<<<< HEAD
            if(1 < 2) {
                int n = 0;
                n += 1;
            }
        =======
            if(1 > 2) {
                int x = 0;
                x -= 3;
            }
        >>>>>>> master
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()

        self.assertEqual(code, refactored)

    def test_conflict_outside_if_block_at_start(self):
        code = multiline("""
        int main() {
        <<<<<<< HEAD
            if(1 < 2) {
                int n = 0;
                n += 1;
            }
            printf("Hello!")
        =======
            if(1 > 2) {
                int x = 0;
                x -= 3;
            }
            printf("Hello?")
        >>>>>>> master
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()

        self.assertEqual(code, refactored)

    def test_conflict_outside_if_block_at_end(self):
        code = multiline("""
        int main() {
        <<<<<<< HEAD
            printf("Hello!")
            if(1 < 2) {
                int n = 0;
                n += 1;
            }
        =======
            printf("Hello?")
            if(1 > 2) {
                int x = 0;
                x -= 3;
            }
        >>>>>>> master
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()

        self.assertEqual(code, refactored)
