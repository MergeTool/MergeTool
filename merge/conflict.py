from .choice import Choice


class Conflict:
    def __init__(self, line_number: int, left: str, right: str,
                 sep1: str = '<<<<<<<\n', sep2: str = '=======\n', sep3: str = '>>>>>>>\n'):

        self.line_number = line_number
        self.left = left
        self.right = right

        self.sep1 = sep1
        self.sep2 = sep2
        self.sep3 = sep3

        self._select = None
        self.choice = Choice.undesided

    def is_resolved(self) -> bool:
        return self.choice.is_resolved()

    def select(self, choice: Choice):
        self.choice = choice

    def result(self) -> str:
        if self.choice is Choice.undesided:
            return self.sep1 + self.left + self.sep2 + self.right + self.sep3
        elif self.choice is Choice.left:
            return self.left
        elif self.choice is Choice.right:
            return self.right
        elif self.choice is Choice.both:
            return self.left + self.right
        else:
            raise ValueError

    def description(self) -> str:
        return "\n left = \n" + self.left + "\n right = \n" + self.right


class Conflict3Way(Conflict):
    def __init__(self, line_number: int, left: str, right: str, base: str,
                 sep: str = '|||||||\n', sep1: str = '<<<<<<<\n', sep2: str = '=======\n', sep3: str = '>>>>>>>\n'):
        
        super().__init__(line_number, left, right, sep1, sep2, sep3)

        self.sep_base = sep
        self.base = base

    def result(self) -> str:
        if self.choice is Choice.undecided:
            return self.sep1 + self.left + self.sep_base + self.base + self.sep2 + self.right + self.sep3
        else:
            return super().result()

    def description(self):
        return super().description() + "\n base = \n" + self.base
