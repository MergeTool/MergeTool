from .choice import Choice


class Conflict3Way:
    def __init__(self, line_number: int, left: str, base: str, right: str, sep1: str, sep2: str, sep3: str, sep4: str):

        self.line_number = line_number
        self.left = left
        self.base = base
        self.right = right

        self.sep1 = sep1
        self.sep2 = sep2
        self.sep3 = sep3
        self.sep4 = sep4

        self._select = None
        self.choice = Choice.undesided

    def is_resolved(self) -> bool:
        return self.choice.is_resolved()

    def select(self, choice: Choice):
        self.choice = choice

    def result(self) -> str:
        if self.choice is Choice.undesided:
            return self.sep1 + self.left + self.sep2 + self.base + self.sep3 + self.right + self.sep4
        elif self.choice is Choice.left:
            return self.left
        elif self.choice is Choice.right:
            return self.right
        elif self.choice is Choice.both:
            return self.left + self.right
        else:
            raise ValueError

    def description(self):
        return "\n left = \n" + self.left + "\n right = \n" + self.right + "\n base = \n" + self.base


class Conflict2Way(Conflict3Way):
    def __init__(self, line_number: int, left: str, right: str, sep1: str, sep3: str, sep4: str):
        super().__init__(line_number, left, "", right, sep1, "", sep3, sep4)

    def description(self) -> str:
        return "\n left = \n" + self.left + "\n right = \n" + self.right


class ConflictBuilder:
    sep1_marker = "<<<<<<<"
    sep2_marker = "|||||||"
    sep3_marker = "======="
    sep4_marker = ">>>>>>>"

    def __init__(self):
        self.has_base = False

        self.line_number = -1
        self.left = ""
        self.base = ""
        self.right = ""

        self.sep1 = ConflictBuilder.sep1_marker + '\n'
        self.sep2 = ConflictBuilder.sep2_marker + '\n'
        self.sep3 = ConflictBuilder.sep3_marker + '\n'
        self.sep4 = ConflictBuilder.sep4_marker + '\n'

    def build(self):
        if self.has_base:
            return Conflict3Way(self.line_number, self.left, self.base, self.right, self.sep1, self.sep2, self.sep3, self.sep4)
        else:
            return Conflict2Way(self.line_number, self.left, self.right, self.sep1, self.sep3, self.sep4)
