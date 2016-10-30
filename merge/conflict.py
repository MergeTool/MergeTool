from .choice import Choice


class Conflict:
    def __init__(self, line_number: int, left: str, right: str, base: str = "",
                 sep1: str = '<<<<<<<\n', sep2: str = '|||||||\n', sep3: str = '=======\n',
                 sep4: str = '>>>>>>>\n'):

        self.line_number = line_number
        self.left = left
        self.right = right
        self.base = base

        self.sep1 = sep1
        self.sep2 = sep2
        self.sep3 = sep3
        self.sep4 = sep4

        self._select = None
        self.choice = Choice.undesided

    def is_resolved(self) -> bool:
        return self.choice.is_resolved()
    
    def hasBase(self)-> bool:
        while self.base != (self.base.lstrip().lstrip("\n")):
            self.base = self.base.lstrip().lstrip("\n")
        return "" != self.base

    def select(self, choice: Choice):
        self.choice = choice

    def result(self) -> str:
        if self.choice is Choice.undesided:
            return self.sep1 + self.left + self.sep2 + self.base \
                   + self.sep3 + self.right + self.sep4 if self.hasBase() else self.sep1 \
                   + self.left + self.sep3 + self.right + self.sep4
        elif self.choice is Choice.left:
            return self.left
        elif self.choice is Choice.right:
            return self.right
        elif self.choice is Choice.both:
            return self.left + self.right
        else:
            raise ValueError
