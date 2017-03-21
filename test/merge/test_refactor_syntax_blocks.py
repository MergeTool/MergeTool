from io import StringIO
from pathlib import Path
from unittest import TestCase
from unittest import skip

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


class TestRefactorSingleBlock(TestCase):
    @classmethod
    def setUpClass(cls):
        from merge.external_parser_setup import ExternalParserSetup
        ExternalParserSetup.setup()

    def test_conflict_at_if_block_end(self):
        code = multiline("""
                int main() {
                    if(1 > 2) {
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
                    if(1 > 2) {
                        printf("Hello!")
                        int n = 0;
                        n += 1;
                    }
                =======
                    if(1 > 2) {
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

    def test_conflict_at_if_block_end_2(self):
        code = multiline("""
                int main() {
                    if(1 > 2) {
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
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        printf("Hello!")
                        int n = 0;
                        n += 1;
                    }
                    printf("World!")
                =======
                    if(1 > 2) {
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

    def test_conflict_at_if_block_end_3(self):
        code = multiline("""
                int main() {
                    if(1 > 2)
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
                    if(1 > 2)
                        { int n = 0; }
                =======
                    if(1 > 2)
                        { int x = 0; }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    @skip("Unplanned functionality")
    def test_conflict_at_raw_if_end(self):
        code = multiline("""
                int main() {
                    if(1 > 2)
                <<<<<<< HEAD
                        int n = 0;
                =======
                        int x = 0;
                >>>>>>> master
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2)
                        int n = 0;
                =======
                    if(1 > 2)
                        int x = 0;
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_if_block_start(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        int n = 0;
                        n += 1;
                =======
                    if(1 > 2) {
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
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
        self.assertEqual(expected, refactored)

    def test_conflict_at_if_block_start_2(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        int n = 0;
                        n += 1;
                =======
                    if(1 > 2) {
                        int x = 0;
                        x -= 3;
                >>>>>>> master
                        printf("Hello!")
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        int n = 0;
                        n += 1;
                        printf("Hello!")
                    }
                =======
                    if(1 > 2) {
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

    def test_conflict_at_if_block_start_3(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                =======
                    if(1 < 2) {
                >>>>>>> master
                        printf("Hello!")
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        printf("Hello!")
                    }
                =======
                    if(1 < 2) {
                        printf("Hello!")
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    @skip("Unplanned functionality")
    def test_conflict_at_raw_if_start(self):
        code = multiline("""
                   int main() {
                   <<<<<<< HEAD
                       if(1 > 2)
                   =======
                       if(1 < 2)
                   >>>>>>> master
                           int x = 0;
                   }
                   """)

        expected = multiline("""
                   int main() {
                   <<<<<<< HEAD
                       if(1 > 2)
                           int x = 0;
                   =======
                       if(1 < 2)
                           int x = 0;
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

    def test_conflict_at_2_sequential_if_blocks(self):
        code = multiline("""
                int main() {
                    if(1 > 2) {
                        printf("Hello!")
                <<<<<<< HEAD
                        int n = 0;
                        n += 1;
                    }

                    if(True) {
                        int z = 10;
                =======
                        int x = 0;
                        x -= 3;
                    }

                    if(False) {
                        int z = 20;
                >>>>>>> master
                    }
                }
                """)

        expected = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        printf("Hello!")
                        int n = 0;
                        n += 1;
                    }

                    if(True) {
                        int z = 10;
                    }
                =======
                    if(1 > 2) {
                        printf("Hello!")
                        int x = 0;
                        x -= 3;
                    }

                    if(False) {
                        int z = 20;
                    }
                >>>>>>> master
                }
                """)

        file_merge = FileMerge.parse(Path("prog.c"), StringIO(code))
        file_merge.refactor_syntax_blocks()
        refactored = file_merge.result()
        self.assertEqual(expected, refactored)

    def test_conflict_at_2_nested_if_blocks_ends(self):
        code = multiline("""
                int main() {
                    if(1 > 2) {
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
                    if(1 > 2) {
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

    def test_conflict_at_2_nested_if_blocks_ends_2(self):
        code = multiline("""
                int main() {
                    if(1 > 2) {
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
                    if(1 > 2) {
                        printf("Hello!")
                        if(True) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    if(1 > 2) {
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

    def test_conflict_at_2_nested_if_blocks_starts(self):
        code = multiline("""
                int main() {
                <<<<<<< HEAD
                    if(1 > 2) {
                        printf("Hello!")
                        if(True) {
                =======
                    if(1 < 2) {
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
                    if(1 > 2) {
                        printf("Hello!")
                        if(True) {
                            int z;
                            z = 10;
                        }
                        int n = 0;
                        n += 1;
                    }
                =======
                    if(1 < 2) {
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
