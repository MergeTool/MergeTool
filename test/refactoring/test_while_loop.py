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

    def test_conflict_after_raw_for(self):
        code = multiline("""
        int main() {
            while(1)
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

    def test_conflict_after_for_block(self):
        code = multiline("""
        int main() {
            while(1 > 2) {
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

    def test_conflict_before_for_block(self):
        code = multiline("""
        int main() {
        <<<<<<< HEAD
            int n = 0;
            n += 1;
        =======
            int x = 0;
            x -= 3;
        >>>>>>> master
            while(x < 10) {
                printf("Hello!")
            }
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_before_for_block_2(self):
        code = multiline("""
        int main() {
        <<<<<<< HEAD
            int n = 0;
            n += 1;
        =======
            int x = 0;
            x -= 3;
        >>>>>>> master
            while(x = 7,
                x < 10,
                x++) {
                printf("Hello!")
            }
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_inside_for_block(self):
        code = multiline("""
        int main() {
            while(1) {
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

    def test_conflict_inside_for_block_2(self):
        code = multiline("""
        int main()
        {
            while(1)
            {
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

    def test_conflict_inside_for_block_3(self):
        code = multiline("""
        int main() {
            while(1 >
                 1 + 1) {
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

    def test_conflict_outside_for_block(self):
        code = multiline("""
        int main()
        {
        <<<<<<< HEAD
            while(1)
            {
                int n = 0;
                n += 1;
            }
        =======
            while(1)
            {
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

    def test_conflict_outside_for_block_2(self):
        code = multiline("""
        int main() {
        <<<<<<< HEAD
            while(1)
            {
                int n = 0;
                n += 1; }
        =======
            while(1)
            {
                int x = 0;
                x -= 3; }
        >>>>>>> master
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()

        self.assertEqual(code, refactored)

    def test_conflict_outside_for_block_3(self):
        code = multiline("""
        int main()
        {
        <<<<<<< HEAD
            while(1 <
                1 + 1)
            {
                int n = 0;
                n += 1;
            }
        =======
            while(1 >
                10 - 8)
            {
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

    def test_conflict_outside_raw_for(self):
        code = multiline("""
        int main()
        {
            int n = 0;
        <<<<<<< HEAD
            while(1 < 1 + 1) n++;
        =======
            while(1 > 10 - 8) n--;
        >>>>>>> master
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()

        self.assertEqual(code, refactored)


class TestRefactorSingleBlock(TestCase):
    @classmethod
    def setUpClass(cls):
        from merge.external_parser_setup import ExternalParserSetup
        ExternalParserSetup.setup()

    def test_conflict_at_for_block_end(self):
        code = multiline("""
                int main() {
                    while(1) {
                        printf("Hello!")
                <<<<<<< HEAD
                        int n = 0;
                        n += 1;
                    }
                =======
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
                        int n = 0;
                        n += 1;
                    }
                =======
                    while(1) {
                        printf("Hello!")
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

    def test_conflict_at_for_block_end_2(self):
        code = multiline("""
                int main()
                {
                    while(1)
                    {
                        printf("Hello!")
                <<<<<<< HEAD
                        int n = 0;
                        n += 1;
                    }
                    printf("World!")
                =======
                        int x = 0;
                        x -= 3;
                    }
                    printf("World?")
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main()
                {
                <<<<<<< HEAD
                    while(1)
                    {
                        printf("Hello!")
                        int n = 0;
                        n += 1;
                    }
                    printf("World!")
                =======
                    while(1)
                    {
                        printf("Hello!")
                        int x = 0;
                        x -= 3;
                    }
                    printf("World?")
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_for_block_end_3(self):
        code = multiline("""
                int main() {
                    while(1)
                <<<<<<< HEAD
                        { int n = 0; }
                =======
                        { int x = 0; }
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(1)
                        { int n = 0; }
                =======
                    while(1)
                        { int x = 0; }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_for_block_end_4(self):
        code = multiline("""
                int main() {
                    int i = 0;
                    while(i >
                          100)
                <<<<<<< HEAD
                        { int n = 0; }
                =======
                        { int x = 0; }
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                    int i = 0;
                <<<<<<< HEAD
                    while(i >
                          100)
                        { int n = 0; }
                =======
                    while(i >
                          100)
                        { int x = 0; }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_raw_for_end(self):
        code = multiline("""
                int main() {
                    int n, x;
                    while(1)
                <<<<<<< HEAD
                        n = 0;
                =======
                        x = 0;
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                    int n, x;
                <<<<<<< HEAD
                    while(1)
                        n = 0;
                =======
                    while(1)
                        x = 0;
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_raw_for_end_2(self):
        code = multiline("""
                int main() {
                    int n, x;
                    while(
                        1)
                <<<<<<< HEAD
                        n = 0;
                =======
                        x = 0;
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                    int n, x;
                <<<<<<< HEAD
                    while(
                        1)
                        n = 0;
                =======
                    while(
                        1)
                        x = 0;
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_for_block_start(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(1) {
                        int n = 0;
                        n += 1;
                =======
                    while(1) {
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(1) {
                        int n = 0;
                        n += 1;
                    }
                =======
                    while(1) {
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

    def test_conflict_at_for_block_start_2(self):
        code = multiline("""
                int main()
                {
                <<<<<<< HEAD
                    while(1)
                    {
                        int n = 0;
                        n += 1;
                =======
                    while(1)
                    {
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                        printf("Hello!")
                    }
                }
                """)

        expected = multiline("""
                int main()
                {
                <<<<<<< HEAD
                    while(1)
                    {
                        int n = 0;
                        n += 1;
                        printf("Hello!")
                    }
                =======
                    while(1)
                    {
                        int x = 0;
                        x -= 3;
                        printf("Hello!")
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_for_block_start_3(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(1) {
                =======
                    while(1) {
                >>>>>>> master
                        printf("Hello!")
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(1) {
                        printf("Hello!")
                    }
                =======
                    while(1) {
                        printf("Hello!")
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_for_block_start_4(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(1
                            ) {
                =======
                    while(1
                        ) {
                >>>>>>> master
                        printf("Hello!")
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(1
                            ) {
                        printf("Hello!")
                    }
                =======
                    while(1
                        ) {
                        printf("Hello!")
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_raw_for_start(self):
        code = multiline("""
                   int main() {
                       int x;
                   <<<<<<< HEAD
                       while(1)
                   =======
                       while(0)
                   >>>>>>> master
                           x = 0;
                   }
                   """)

        expected = multiline("""
                   int main() {
                       int x;
                   <<<<<<< HEAD
                       while(1)
                           x = 0;
                   =======
                       while(0)
                           x = 0;
                   >>>>>>> master
                   }
                   """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)


class TestRefactorMultipleBlocks(TestCase):
    @classmethod
    def setUpClass(cls):
        from merge.external_parser_setup import ExternalParserSetup
        ExternalParserSetup.setup()

    def test_conflict_at_2_sequential_for_blocks(self):
        code = multiline("""
                int main() {
                    while(0)
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

                    while(2) {
                        int z = 20;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(0)
                    {
                        printf("Hello!")
                        int n = 0;
                        n += 1;
                    }

                    while(1) {
                        int z = 10;
                    }
                =======
                    while(0)
                    {
                        printf("Hello!")
                        int x = 0;
                        x -= 3;
                    }

                    while(2) {
                        int z = 20;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_2_nested_for_blocks_ends(self):
        code = multiline("""
                int main() {
                    while(0) {
                        printf("Hello!")
                        while(10) {
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
                    while(0) {
                        printf("Hello!")
                <<<<<<< HEAD
                        while(10) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                =======
                        while(10) {
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

    def test_conflict_at_2_nested_for_blocks_ends_2(self):
        code = multiline("""
                int main() {
                    while(1) {
                        printf("Hello!")
                        while(2) {
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
                        while(2) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    while(1) {
                        printf("Hello!")
                        while(2) {
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

    def test_conflict_at_2_nested_for_blocks_starts(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    while(1) {
                        printf("Hello!")
                        while(-1) {
                =======
                    while(2) {
                        printf("Hello!")
                        while(-2) {
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
                    while(1) {
                        printf("Hello!")
                        while(-1) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    while(2) {
                        printf("Hello!")
                        while(-2) {
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
