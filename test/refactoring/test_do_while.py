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

    def test_conflict_after_raw_do_while(self):
        code = multiline("""
        int main() {
            do
                printf("Hello!");
            while(1);
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

    def test_conflict_after_do_while_block(self):
        code = multiline("""
        int main() {
            do {
                printf("Hello!");
            } while(1 > 2);
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

    def test_conflict_before_do_while_block(self):
        code = multiline("""
        int main() {
        <<<<<<< HEAD
            int n = 0;
            n += 1;
        =======
            int x = 0;
            x -= 3;
        >>>>>>> master
            do {
                printf("Hello!");
            } while(x < 10);
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_before_do_while_block_2(self):
        code = multiline("""
        int main() {
        <<<<<<< HEAD
            int n = 0;
            n += 1;
        =======
            int x = 0;
            x -= 3;
        >>>>>>> master
            do {
                printf("Hello!");
            } while(x = 7,
                    x < 10,
                    x++)
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_inside_do_while_block(self):
        code = multiline("""
        int main() {
            do {
        <<<<<<< HEAD
                int n = 0;
                n += 1;
        =======
                int x = 0;
                x -= 3;
        >>>>>>> master
            } while(1);
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_inside_do_while_block_2(self):
        code = multiline("""
        int main()
        {
            do
            {
        <<<<<<< HEAD
                int n = 0;
                n += 1;
        =======
                int x = 0;
                x -= 3;
        >>>>>>> master
            }
            while(1);
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_inside_do_while_block_3(self):
        code = multiline("""
        int main() {
             do {
        <<<<<<< HEAD
                int n = 0;
                n += 1;
        =======
                int x = 0;
                x -= 3;
        >>>>>>> master
            } while(1 >
                 1 + 1);
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(code, refactored)

    def test_conflict_outside_do_while_block(self):
        code = multiline("""
        int main()
        {
        <<<<<<< HEAD
            do
            {
                int n = 0;
                n += 1;
            }
            while(1);
        =======
            do
            {
                int x = 0;
                x -= 3;
            }
            while(1);
        >>>>>>> master
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()

        self.assertEqual(code, refactored)

    def test_conflict_outside_do_while_block_2(self):
        code = multiline("""
        int main() {
        <<<<<<< HEAD
            do
            {
                int n = 0;
                n += 1; } while(1);
        =======
            do
            {
                int x = 0;
                x -= 3; } while(1);
        >>>>>>> master
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()

        self.assertEqual(code, refactored)

    def test_conflict_outside_do_while_block_3(self):
        code = multiline("""
        int main()
        {
        <<<<<<< HEAD
            do
            {
                int n = 0;
                n += 1;
            }
            while(1 <
                1 + 1);
        =======
            do
            {
                int x = 0;
                x -= 3;
            }
            while(1 >
                10 - 8);
        >>>>>>> master
        }
        """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()

        self.assertEqual(code, refactored)

    def test_conflict_outside_raw_do_while(self):
        code = multiline("""
        int main()
        {
            int n = 0;
        <<<<<<< HEAD
            do n++; while(1 < 1 + 1);
        =======
            do n--; while(1 > 10 - 8);
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

    def test_conflict_at_do_while_block_end(self):
        code = multiline("""
                int main() {
                    do {
                        printf("Hello!");
                <<<<<<< HEAD
                        int n = 0;
                        n += 1;
                    } while(1);
                =======
                        int x = 0;
                        x -= 3;
                    } while(1);
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    do {
                        printf("Hello!");
                        int n = 0;
                        n += 1;
                    } while(1);
                =======
                    do {
                        printf("Hello!")
                        int x = 0;
                        x -= 3;
                    } while(1);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_do_while_block_end_2(self):
        code = multiline("""
                int main()
                {
                    do
                    {
                        printf("Hello!");
                <<<<<<< HEAD
                        int n = 0;
                        n += 1;
                    }
                    while(1);
                    printf("World!");
                =======
                        int x = 0;
                        x -= 3;
                    }
                    while(1);
                    printf("World?");
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main()
                {
                <<<<<<< HEAD
                    do
                    {
                        printf("Hello!");
                        int n = 0;
                        n += 1;
                    }
                    while(1);
                    printf("World!");
                =======
                    do
                    {
                        printf("Hello!");
                        int x = 0;
                        x -= 3;
                    }
                    while(1);
                    printf("World?");
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_do_while_block_end_3(self):
        code = multiline("""
                int main() {
                    do
                <<<<<<< HEAD
                        { int n = 0; }
                =======
                        { int x = 0; }
                >>>>>>> master
                    while(1);
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    do
                        { int n = 0; }
                    while(1);
                =======
                    do
                        { int x = 0; }
                    while(1);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_do_while_block_end_4(self):
        code = multiline("""
                int main() {
                    int i = 0;
                    do
                <<<<<<< HEAD
                        { int n = 0; }
                =======
                        { int x = 0; }
                >>>>>>> master
                    while(i >
                          100);
                }
                """)

        expected = multiline("""
                int main() {
                    int i = 0;
                <<<<<<< HEAD
                    do
                        { int n = 0; }
                    while(i >
                          100);
                =======
                    do
                        { int x = 0; }
                    while(i >
                          100);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_raw_do_while_end(self):
        code = multiline("""
                int main() {
                    int n, x;
                <<<<<<< HEAD
                    do
                        n = 0;
                =======
                        x = 0;
                >>>>>>> master
                    while(1);
                }
                """)

        expected = multiline("""
                int main() {
                    int n, x;
                <<<<<<< HEAD
                    do
                        n = 0;
                    while(1);
                =======
                    do
                        x = 0;
                    while(1);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_raw_do_while_end_2(self):
        code = multiline("""
                int main() {
                    int n, x;
                    do
                <<<<<<< HEAD
                        n = 0;
                =======
                        x = 0;
                >>>>>>> master
                    while(
                        1);
                }
                """)

        expected = multiline("""
                int main() {
                    int n, x;
                <<<<<<< HEAD
                    do
                        n = 0;
                    while(
                        1);
                =======
                    do
                        x = 0;
                    while(
                        1);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_do_while_block_start(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    do {
                        int n = 0;
                        n += 1;
                =======
                    do {
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    } while(1);
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    do {
                        int n = 0;
                        n += 1;
                    } while(1);
                =======
                    do {
                        int x = 0;
                        x -= 3;
                    } while(1);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_do_while_block_start_2(self):
        code = multiline("""
                int main()
                {
                <<<<<<< HEAD
                    do
                    {
                        int n = 0;
                        n += 1;
                =======
                    do
                    {
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                        printf("Hello!")
                    } while(1);
                }
                """)

        expected = multiline("""
                int main()
                {
                <<<<<<< HEAD
                    do
                    {
                        int n = 0;
                        n += 1;
                        printf("Hello!")
                    } while(1);
                =======
                    do
                    {
                        int x = 0;
                        x -= 3;
                        printf("Hello!")
                    } while(1);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_do_while_block_start_3(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    do {
                =======
                    do {
                >>>>>>> master
                        printf("Hello!")
                    } while(1);
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    do {
                        printf("Hello!")
                    } while(1);
                =======
                    do {
                        printf("Hello!")
                    } while(1);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_do_while_block_start_4(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    do {
                =======
                    do
                    {
                >>>>>>> master
                        printf("Hello!");
                    } while(1);
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    do {
                        printf("Hello!");
                    } while(1);
                =======
                    do
                    {
                        printf("Hello!");
                    } while(1);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_raw_do_while_start(self):
        code = multiline("""
                   int main() {
                       int x;
                       do
                           x = 0;
                   <<<<<<< HEAD
                       while(1);
                   =======
                       while(0);
                   >>>>>>> master
                   }
                   """)

        expected = multiline("""
                   int main() {
                       int x;
                   <<<<<<< HEAD
                       do
                           x = 0;
                       while(1);
                   =======
                       do
                           x = 0;
                       while(0);
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

    def test_conflict_at_2_sequential_do_while_blocks(self):
        code = multiline("""
                int main() {
                    do
                    {
                        printf("Hello!")
                <<<<<<< HEAD
                        int n = 0;
                        n += 1;
                    }
                    while(0);

                    do {
                        int z = 10;
                =======
                        int x = 0;
                        x -= 3;
                    } while(1);

                    do {
                        int z = 20;
                >>>>>>> master
                    } while(2);
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    do
                    {
                        printf("Hello!")
                        int n = 0;
                        n += 1;
                    }
                    while(0);

                    do {
                        int z = 10;
                    } while(1);
                =======
                    do
                    {
                        printf("Hello!")
                        int x = 0;
                        x -= 3;
                    }
                    while(0);

                    do {
                        int z = 20;
                    } while(2);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_2_nested_do_while_blocks_ends(self):
        code = multiline("""
                int main() {
                    do {
                        printf("Hello!")
                        do {
                            int z;
                <<<<<<< HEAD
                            z = 10;
                        } while(10);
                        int n = 0;
                        n += 1;
                =======
                            z = 20;
                        } while(10);
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    } while(0);
                }
                """)

        expected = multiline("""
                int main() {
                    do {
                        printf("Hello!")
                <<<<<<< HEAD
                        do {
                            int z;
                            z = 10;
                        } while(10);
                        int n = 0;
                        n += 1;
                =======
                        do {
                            int z;
                            z = 20;
                        } while(10);
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    } while(0);
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_2_nested_do_while_blocks_ends_2(self):
        code = multiline("""
                int main() {
                    do {
                        printf("Hello!")
                        do {
                            int z;
                <<<<<<< HEAD
                            z = 10;
                        } while(2);
                        int n = 0;
                        n += 1;
                    }
                =======
                            z = 20;
                        } while(2);
                        int x = 0;
                        x -= 3;
                    }  while(1);
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    do {
                        printf("Hello!")
                        do {
                            int z;
                            z = 10;
                        } while(2);
                        int n = 0;
                        n += 1;
                    } while(1);
                =======
                    do {
                        printf("Hello!")
                        do {
                            int z;
                            z = 20;
                        } while(2);
                        int x = 0;
                        x -= 3;
                    } while(1);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_2_nested_do_while_blocks_starts(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    do {  // 1
                        printf("Hello!")
                        do {
                =======
                    do {  // 2
                        printf("Hello!")
                        do {
                >>>>>>> master
                            int z;
                            z = 10;
                        } while(-1);
                        int n = 0;
                        n += 1;
                    } while(1);
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    do {  // 1
                        printf("Hello!")
                        do {
                            int z;
                            z = 10;
                        } while(-1);
                        int n = 0;
                        n += 1;
                    } while(1);
                =======
                    do {  // 2
                        printf("Hello!")
                        do {
                            int z;
                            z = 10;
                        } while(-1);
                        int n = 0;
                        n += 1;
                    } while(1);
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)
