from copy import copy
from io import StringIO
from pathlib import Path
from unittest import TestCase

from clang.cindex import CursorKind

from merge.choice import Choice
from merge.conflict import Conflict2Way, Conflict3Way
from merge.file_bit import FileBit
from merge.file_merge import FileMerge
import merge.cursor_utils


class TestFileMerge(TestCase):
    @classmethod
    def setUpClass(cls):
        from merge.external_parser_setup import ExternalParserSetup
        ExternalParserSetup.setup()

    def setUp(self):
        self.fb1 = FileBit(1, ("int main() {\n"
                               "   if(true)\n"
                               "   {\n"
                               "	   cin >> n;\n"
                               "	   n += 1;\n"
                               "	   printf(\"left\");\n"
                               "   }\n"))

        self.ct1 = Conflict2Way(8, 8, 8,
                                "   int x = 0;\n"
                                "   x = 0;\n",
                                "   int y = 3;\n",
                                "<<<<<<<\n", "=======\n", ">>>>>>>\n")

        self.fb2 = FileBit(14, ("   while(true) {\n"
                                "	   cin >> n;\n"
                                "	   n += 1;\n"
                                "	   printf(\"left\");\n"
                                "   }\n"))

        self.ct2 = Conflict3Way(19, 15, 14, "   x = 0;\n", """   printf("Hello!")\n""", "   y = 2;\n",
                                "<<<<<<<\n", "|||||||\n", "=======\n", ">>>>>>>\n")

        self.fb3 = FileBit(26, "   return 0;\n"
                               "}\n")

        self.file_merge = FileMerge(Path("./testproject/prog.cpp"),
                                    [self.fb1, self.fb2, self.fb3], [self.ct1, self.ct2])

    def test_is_resolved(self):
        self.assertFalse(self.file_merge.is_resolved())
        self.ct1.select(Choice.both)
        self.assertFalse(self.file_merge.is_resolved())
        self.ct2.select(Choice.left)
        self.assertTrue(self.file_merge.is_resolved())

    def test_select_all(self):
        self.assertFalse(self.ct1.is_resolved())
        self.assertFalse(self.ct2.is_resolved())

        self.file_merge.select_all(Choice.right)

        self.assertTrue(self.ct1.is_resolved())
        self.assertTrue(self.ct2.is_resolved())

    def test_result_default(self):
        self.ct1.select(Choice.both)
        self.ct2.select(Choice.undecided)

        text = self.file_merge.result()
        self.assertEqual(text, ("int main() {\n"
                                "   if(true)\n"
                                "   {\n"
                                "	   cin >> n;\n"
                                "	   n += 1;\n"
                                "	   printf(\"left\");\n"
                                "   }\n"
                                "   int x = 0;\n"
                                "   x = 0;\n"
                                "   int y = 3;\n"
                                "   while(true) {\n"
                                "	   cin >> n;\n"
                                "	   n += 1;\n"
                                "	   printf(\"left\");\n"
                                "   }\n"
                                "<<<<<<<\n"
                                "   x = 0;\n"
                                "|||||||\n"
                                "   printf(\"Hello!\")\n"
                                "=======\n"
                                "   y = 2;\n"
                                ">>>>>>>\n"
                                "   return 0;\n"
                                "}\n"))

    def test_result_left(self):
        self.ct1.select(Choice.both)
        self.ct2.select(Choice.undecided)

        text = self.file_merge.result(Choice.left)
        self.assertEqual(text, ("int main() {\n"
                                "   if(true)\n"
                                "   {\n"
                                "	   cin >> n;\n"
                                "	   n += 1;\n"
                                "	   printf(\"left\");\n"
                                "   }\n"
                                "   int x = 0;\n"
                                "   x = 0;\n"
                                "   while(true) {\n"
                                "	   cin >> n;\n"
                                "	   n += 1;\n"
                                "	   printf(\"left\");\n"
                                "   }\n"
                                "   x = 0;\n"
                                "   return 0;\n"
                                "}\n"))

    def test_result_right(self):
        self.ct1.select(Choice.left)
        self.ct2.select(Choice.right)

        text = self.file_merge.result(Choice.right)
        self.assertEqual(text, ("int main() {\n"
                                "   if(true)\n"
                                "   {\n"
                                "	   cin >> n;\n"
                                "	   n += 1;\n"
                                "	   printf(\"left\");\n"
                                "   }\n"
                                "   int y = 3;\n"
                                "   while(true) {\n"
                                "	   cin >> n;\n"
                                "	   n += 1;\n"
                                "	   printf(\"left\");\n"
                                "   }\n"
                                "   y = 2;\n"
                                "   return 0;\n"
                                "}\n"))

    def test_abstract_syntax_tree_left(self):
        root = self.file_merge.abstract_syntax_tree(Choice.left).cursor
        main_body = root.child(0).child(0)

        if1 = main_body.child(0)
        var1 = main_body.child(1)
        ass1 = main_body.child(2)
        while1 = main_body.child(3)
        ass2 = main_body.child(4)
        return1 = main_body.child(5)

        self.assertEqual(if1.kind, CursorKind.IF_STMT)
        self.assertEqual(var1.kind, CursorKind.DECL_STMT)
        self.assertEqual(ass1.kind, CursorKind.BINARY_OPERATOR)
        self.assertEqual(while1.kind, CursorKind.WHILE_STMT)
        self.assertEqual(ass2.kind, CursorKind.BINARY_OPERATOR)
        self.assertEqual(return1.kind, CursorKind.RETURN_STMT)

    def test_abstract_syntax_tree_right(self):
        root = self.file_merge.abstract_syntax_tree(Choice.right).cursor
        main_body = root.child(0).child(0)

        if1 = main_body.child(0)
        var1 = main_body.child(1)
        while1 = main_body.child(2)
        ass2 = main_body.child(3)
        return1 = main_body.child(4)

        self.assertEqual(if1.kind, CursorKind.IF_STMT)
        self.assertEqual(var1.kind, CursorKind.DECL_STMT)
        self.assertEqual(while1.kind, CursorKind.WHILE_STMT)
        self.assertEqual(ass2.kind, CursorKind.BINARY_OPERATOR)
        self.assertEqual(return1.kind, CursorKind.RETURN_STMT)

    def test_abstract_syntax_tree_default(self):
        default = self.file_merge.abstract_syntax_tree()
        left = self.file_merge.abstract_syntax_tree(Choice.left)

        kinds = [CursorKind.FUNCTION_DECL, CursorKind.IF_STMT, CursorKind.WHILE_STMT, CursorKind.BINARY_OPERATOR]

        self.assertListEqual([ch.kind for ch in FileMerge.extract_children(default.cursor, kinds)],
                             [ch.kind for ch in FileMerge.extract_children(left.cursor, kinds)])

    def test_abstract_syntax_tree_cache(self):
        left1 = self.file_merge.abstract_syntax_tree(Choice.left)
        left2 = self.file_merge.abstract_syntax_tree(Choice.left)
        right = self.file_merge.abstract_syntax_tree(Choice.right)
        left3 = self.file_merge.abstract_syntax_tree(Choice.left)

        self.assertEqual(left1, left2)
        self.assertNotEqual(left2, right)
        self.assertNotEqual(right, left3)

    def test_refactor_syntax_blocks(self):
        before = copy(self.file_merge)
        self.file_merge.refactor_syntax_blocks()

        # `self.file_merge` contains no problematic conflicts
        self.assertEqual(self.file_merge.path, before.path)
        self.assertListEqual(self.file_merge.file_bits, before.file_bits)
        self.assertListEqual(self.file_merge.conflicts, before.conflicts)

    def test_extract_children(self):
        root = self.file_merge.abstract_syntax_tree(Choice.left).cursor
        children = FileMerge.extract_children(root,
                                              [CursorKind.FUNCTION_DECL, CursorKind.IF_STMT, CursorKind.WHILE_STMT])

        extracted_features = [(ch.kind, ch.extent.start.line) for ch in children]
        correct_features = [(CursorKind.FUNCTION_DECL, 1), (CursorKind.IF_STMT, 2), (CursorKind.WHILE_STMT, 10)]

        self.assertListEqual(extracted_features, correct_features)

    def test_parse(self):
        text = ("int main() {\n"
                "   if(true)\n"
                "   {\n"
                "	   cin >> n;\n"
                "	   n += 1;\n"
                "	   printf(\"left\");\n"
                "   }\n"
                "<<<<<<<\n"
                "   int x = 0;\n"
                "   x = 0;\n"
                "=======\n"
                "   int y = 3;\n"
                ">>>>>>>\n"
                "   while(true) {\n"
                "	   cin >> n;\n"
                "	   n += 1;\n"
                "	   printf(\"left\");\n"
                "   }\n"
                "<<<<<<<\n"
                "   x = 0;\n"
                "|||||||\n"
                "   printf(\"Hello!\")\n"
                "=======\n"
                "   y = 2;\n"
                ">>>>>>>\n"
                "   return 0;\n"
                "}\n")

        parsed_file = FileMerge.parse(Path("./testproject/prog.cpp"), StringIO(text))

        self.assertEqual(parsed_file.path, self.file_merge.path)
        self.assertListEqual(parsed_file.file_bits, self.file_merge.file_bits)
        self.assertListEqual(parsed_file.conflicts, self.file_merge.conflicts)

    def test_can_parse(self):
        self.assertTrue(FileMerge.can_parse(Path("./testproject/prog.cpp")))
        self.assertTrue(FileMerge.can_parse(Path("/Users/admin/testproject/prog.hpp")))
        self.assertTrue(FileMerge.can_parse(Path("testproject/prog.c")))
        self.assertTrue(FileMerge.can_parse(Path("testproject/prog.h")))
        self.assertFalse(FileMerge.can_parse(Path("testproject/h")))
        self.assertFalse(FileMerge.can_parse(Path("testproject/prog.log")))
