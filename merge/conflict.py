from .choice import Choice
from enum import Enum


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
    
    #def hasBase(self)-> bool:
    #    while self.base != (self.base.lstrip().lstrip("\n")):
    #        self.base = self.base.lstrip().lstrip("\n")
    #    return "" != self.base

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

    def print_description(self):
        print("\n left = ")
        print(self.left)
        print("\n right = ")
        print(self.right)


class Diff3Conflict(Conflict):
    def __init__(self, line_number: int, left: str, right: str, base: str = "", sep: str = '|||||||\n',
                 sep1: str = '<<<<<<<\n', sep2: str = '=======\n', sep3: str = '>>>>>>>\n'):
        
        super().__init__(self, line_number, left, right, sep1, sep2, sep3)

        self.sep = sep
        self.base = base

    def result(self) -> str:
        if self.choice is Choice.undecided:
            return self.sep1 + self.left + self.sep+ + self.base + self.sep2 + self.right + self.sep3
        else:
            return super().result()

    def print_description(self):
        super().printConflict()
        print("\n base = ")
        print(self.base)



