from io import StringIO
from pathlib import Path
from unittest import TestCase

from merge.file_merge import FileMerge


def multiline(text: str) -> str:
    from textwrap import dedent
    return dedent(text).strip()


class TestRefactorIfAndFor(TestCase):
    @classmethod
    def setUpClass(cls):
        from merge.external_parser_setup import ExternalParserSetup
        ExternalParserSetup.setup()

    def test_conflict_at_sequential_if_and_for(self):
        code = multiline("""
                int main() {
                    if(1 > 2)
                    {
                        printf("Hello!")
                <<<<<<< HEAD
                        int n = 0;
                        n += 1;
                    }

                    for(;1;) {
                        int z = 10;
                =======
                        int x = 0;
                        x -= 3;
                    }

                    for(;2;)
                    {
                        int z = 20;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2)
                    {
                        printf("Hello!")
                        int n = 0;
                        n += 1;
                    }

                    for(;1;) {
                        int z = 10;
                    }
                =======
                    if(1 > 2)
                    {
                        printf("Hello!")
                        int x = 0;
                        x -= 3;
                    }

                    for(;2;)
                    {
                        int z = 20;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_sequential_for_and_if(self):
        code = multiline("""
                int main() {
                    for(;0;) {
                        printf("Hello!")
                <<<<<<< HEAD
                        int n = 0;
                        n += 1;
                    }

                    if(1 < 2) {
                        int z = 10;
                =======
                        int x = 0;
                        x -= 3;
                    }

                    if(1 > 2)
                    {
                        int z = 20;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    for(;0;) {
                        printf("Hello!")
                        int n = 0;
                        n += 1;
                    }

                    if(1 < 2) {
                        int z = 10;
                    }
                =======
                    for(;0;) {
                        printf("Hello!")
                        int x = 0;
                        x -= 3;
                    }

                    if(1 > 2)
                    {
                        int z = 20;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_if_in_for_ends(self):
        code = multiline("""
                int main() {
                    for(;;) {
                        printf("Hello!")
                        if(True) {
                            int z;
                <<<<<<< HEAD
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                =======
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                    for(;;) {
                        printf("Hello!")
                <<<<<<< HEAD
                        if(True) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                =======
                        if(True) {
                            int z;
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    }
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_if_in_for_ends_2(self):
        code = multiline("""
                int main() {
                    for(;;) {
                        printf("Hello!")
                        if(True) {
                            int z;
                <<<<<<< HEAD
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                    }
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    for(;;) {
                        printf("Hello!")
                        if(True) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    for(;;) {
                        printf("Hello!")
                        if(True) {
                            int z;
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_for_in_if_ends(self):
        code = multiline("""
                int main() {
                    if(1 > 2) {
                        printf("Hello!")
                        for(;0;) {
                            int z;
                <<<<<<< HEAD
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                =======
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                    if(1 > 2) {
                        printf("Hello!")
                <<<<<<< HEAD
                        for(;0;) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                =======
                        for(;0;) {
                            int z;
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    }
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_for_in_if_ends_2(self):
        code = multiline("""
                int main() {
                    if(1 > 2) {
                        printf("Hello!")
                        for(;;) {
                            int z;
                <<<<<<< HEAD
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                    }
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        printf("Hello!")
                        for(;;) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    if(1 > 2) {
                        printf("Hello!")
                        for(;;) {
                            int z;
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_if_in_for_starts(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    for(;+1;) {
                        printf("Hello!")
                        if(True) {
                =======
                    for(;-1;) {
                        printf("Hello!")
                        if(False) {
                >>>>>>> master
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    for(;+1;) {
                        printf("Hello!")
                        if(True) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    for(;-1;) {
                        printf("Hello!")
                        if(False) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_for_in_if_starts(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        printf("Hello!")
                        for(;0;) {
                =======
                    if(1 < 2) {
                        printf("Hello!")
                        for(;1;) {
                >>>>>>> master
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        printf("Hello!")
                        for(;0;) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    if(1 < 2) {
                        printf("Hello!")
                        for(;1;) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)


class TestRefactorIfAndWhile(TestCase):
    @classmethod
    def setUpClass(cls):
        from merge.external_parser_setup import ExternalParserSetup
        ExternalParserSetup.setup()

    def test_conflict_at_sequential_if_and_while(self):
        code = multiline("""
                int main() {
                    if(1 > 2)
                    {
                        printf("Hello!")
                <<<<<<< HEAD
                        int n = 0;
                        n += 1;
                    }

                    while(1) {
                        int z = 10;
                =======
                        int x = 0;
                        x -= 3;
                    }

                    while(2)
                    {
                        int z = 20;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2)
                    {
                        printf("Hello!")
                        int n = 0;
                        n += 1;
                    }

                    while(1) {
                        int z = 10;
                    }
                =======
                    if(1 > 2)
                    {
                        printf("Hello!")
                        int x = 0;
                        x -= 3;
                    }

                    while(2)
                    {
                        int z = 20;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_sequential_while_and_if(self):
        code = multiline("""
                int main() {
                    while(0) {
                        printf("Hello!")
                <<<<<<< HEAD
                        int n = 0;
                        n += 1;
                    }

                    if(1 < 2) {
                        int z = 10;
                =======
                        int x = 0;
                        x -= 3;
                    }

                    if(1 > 2)
                    {
                        int z = 20;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(0) {
                        printf("Hello!")
                        int n = 0;
                        n += 1;
                    }

                    if(1 < 2) {
                        int z = 10;
                    }
                =======
                    while(0) {
                        printf("Hello!")
                        int x = 0;
                        x -= 3;
                    }

                    if(1 > 2)
                    {
                        int z = 20;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_if_in_while_ends(self):
        code = multiline("""
                int main() {
                    while(1) {
                        printf("Hello!")
                        if(True) {
                            int z;
                <<<<<<< HEAD
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                =======
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                    while(1) {
                        printf("Hello!")
                <<<<<<< HEAD
                        if(True) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                =======
                        if(True) {
                            int z;
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    }
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_if_in_while_ends_2(self):
        code = multiline("""
                int main() {
                    while(1) {
                        printf("Hello!")
                        if(True) {
                            int z;
                <<<<<<< HEAD
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                    }
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(1) {
                        printf("Hello!")
                        if(True) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    while(1) {
                        printf("Hello!")
                        if(True) {
                            int z;
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_while_in_if_ends(self):
        code = multiline("""
                int main() {
                    if(1 > 2) {
                        printf("Hello!")
                        while(0) {
                            int z;
                <<<<<<< HEAD
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                =======
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                    if(1 > 2) {
                        printf("Hello!")
                <<<<<<< HEAD
                        while(0) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                =======
                        while(0) {
                            int z;
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    }
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_while_in_if_ends_2(self):
        code = multiline("""
                int main() {
                    if(1 > 2) {
                        printf("Hello!")
                        while(1) {
                            int z;
                <<<<<<< HEAD
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                    }
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        printf("Hello!")
                        while(1) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    if(1 > 2) {
                        printf("Hello!")
                        while(1) {
                            int z;
                            z = 20;
                        }
                        int x = 0;
                        x -= 3;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_if_in_while_starts(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(+1) {
                        printf("Hello!")
                        if(True) {
                =======
                    while(-1) {
                        printf("Hello!")
                        if(False) {
                >>>>>>> master
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(+1) {
                        printf("Hello!")
                        if(True) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    while(-1) {
                        printf("Hello!")
                        if(False) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_nested_while_in_if_starts(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        printf("Hello!")
                        while(0) {
                =======
                    if(1 < 2) {
                        printf("Hello!")
                        while(1) {
                >>>>>>> master
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        printf("Hello!")
                        while(0) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    if(1 < 2) {
                        printf("Hello!")
                        while(1) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)
