from .choice import Choice


class Conflict3Way:
    def __init__(self, line_number: int, line_num_left: int, line_num_right: int,
                 left: str, base: str, right: str, sep1: str, sep2: str, sep3: str, sep4: str):

        self.line_number = line_number
        self.line_num_left = line_num_left
        self.line_num_right = line_num_right

        self.left = left
        self.base = base
        self.right = right

        self.sep1 = sep1
        self.sep2 = sep2
        self.sep3 = sep3
        self.sep4 = sep4

        self.choice = Choice.undecided

    def is_resolved(self) -> bool:
        return self.choice.is_resolved()

    def select(self, choice: Choice):
        self.choice = choice

    def result(self, choice: Choice = None) -> str:
        _choice = self.choice if not choice else choice

        if _choice is Choice.undecided:
            return self.sep1 + self.left + self.sep2 + self.base + self.sep3 + self.right + self.sep4
        elif _choice is Choice.left:
            return self.left
        elif _choice is Choice.right:
            return self.right
        elif _choice is Choice.both:
            return self.left + self.right
        else:
            raise ValueError

    def description(self):
        return "\n left = \n" + self.left + "\n right = \n" + self.right + "\n base = \n" + self.base

    def extend_top_up(self, chunk: str):
        line_num = chunk.count('\n')
        self.line_number -= line_num
        self.line_num_left -= line_num
        self.line_num_right -= line_num
        self.left = chunk + self.left
        self.base = chunk + self.base
        self.right = chunk + self.right

    def extend_bottom_down(self, chunk: str):
        self.left += chunk
        self.base += chunk
        self.right += chunk

    def start(self, choice: Choice):
        if choice is Choice.left:
            return self.line_num_left
        elif choice is Choice.right:
            return self.line_num_right
        else:
            raise ValueError

    def end(self, choice: Choice):
        return self.start(choice) + len(self.result(choice).splitlines())


class Conflict2Way(Conflict3Way):
    def __init__(self, line_number: int, line_num_left: int, line_num_right: int,
                 left: str, right: str, sep1: str, sep3: str, sep4: str):

        super().__init__(line_number, line_num_left, line_num_right, left, "", right, sep1, "", sep3, sep4)

    def result(self, choice: Choice = None) -> str:
        _choice = self.choice if not choice else choice

        if _choice is Choice.undecided:
            return self.sep1 + self.left + self.sep3 + self.right + self.sep4
        else:
            return super().result(_choice)

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
        self.line_num_left = -1
        self.line_num_right = -1

        self.left = ""
        self.base = ""
        self.right = ""

        self.sep1 = ConflictBuilder.sep1_marker + '\n'
        self.sep2 = ConflictBuilder.sep2_marker + '\n'
        self.sep3 = ConflictBuilder.sep3_marker + '\n'
        self.sep4 = ConflictBuilder.sep4_marker + '\n'

    def build(self):
        if self.has_base:
            return Conflict3Way(self.line_number, self.line_num_left, self.line_num_right,
                                self.left, self.base, self.right, self.sep1, self.sep2, self.sep3, self.sep4)
        else:
            return Conflict2Way(self.line_number, self.line_num_left, self.line_num_right,
                                self.left, self.right, self.sep1, self.sep3, self.sep4)
