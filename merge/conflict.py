from .choice import Choice


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
        self.choice = Choice.undesided

    def is_resolved(self) -> bool:
        return self.choice.is_resolved()

    def select(self, choice: Choice):
        self.choice = choice

    def result(self, choice: Choice = None) -> str:
        _choice = self.choice if not choice else choice

        if _choice is Choice.undesided:
            return self.sep1 + self.left + self.sep2 + self.right + self.sep3
        elif _choice is Choice.left:
            return self.left
        elif _choice is Choice.right:
            return self.right
        elif _choice is Choice.both:
            return self.left + self.right
        else:
            raise ValueError