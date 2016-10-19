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