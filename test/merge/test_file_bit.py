from unittest import TestCase

from merge.file_bit import FileBit


class TestFileBit(TestCase):
    def setUp(self):
        self.file_bit = FileBit(239, ("   if(true)\n"
                                      "   {\n"
                                      "	   cin >> n;\n"
                                      "	   n += 1;\n"
                                      "	   printf(\"left\");\n"
                                      "   }"))

    def test_shrink_top_down(self):
        self.file_bit.shrink_top_down(1)
        self.assertEqual(self.file_bit.line_number, 240)
        self.assertEqual(self.file_bit.text, ("   {\n"
                                              "	   cin >> n;\n"
                                              "	   n += 1;\n"
                                              "	   printf(\"left\");\n"
                                              "   }"))

    def test_shrink_bottom_up(self):
        self.file_bit.shrink_bottom_up(1)
        self.assertEqual(self.file_bit.line_number, 239)
        self.assertEqual(self.file_bit.text, ("   if(true)\n"
                                              "   {\n"
                                              "	   cin >> n;\n"
                                              "	   n += 1;\n"
                                              "	   printf(\"left\");\n"))

    def test_shrink_0(self):
        with self.assertRaises(AssertionError):
            self.file_bit.shrink_bottom_up(0)

        with self.assertRaises(AssertionError):
            self.file_bit.shrink_top_down(0)
