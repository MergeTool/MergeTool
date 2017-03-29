from .choice import Choice


class Conflict3Way:
    """
    Represents a generic conflict of a 3-way merge.
    Contains its position and all the text components needed to completely reproduce the conflict.

    Components order in the initial file:
        sep1
          left
        sep2
          base
        sep3
          right
        sep4

    Example:
        int main() {               1
            if(1 > 2) {            2
                printf("Hello!")   3
            }                      4
        <<<<<<< HEAD               5      sep1      (line_number = 5)
            int n = 0;             6        left    (line_num_left = 5)
            n += 1;                7        left
        |||||||                    8      sep2
            printf("World!")       9        base
        =======                    10     sep3
            int x = 0;             11       right   (line_num_right = 5)
            x -= 3;                12       right
        >>>>>>> master             13     sep4
        }                          14
    """
    def __init__(self, line_number: int, line_num_left: int, line_num_right: int,
                 left: str, base: str, right: str, sep1: str, sep2: str, sep3: str, sep4: str):
        """
        :ivar line_number:    first line of the conflict in the initial conflicted file
        :ivar line_num_left:  first line of `left` in the left branch
        :ivar line_num_right: first line of `right` in the right branch

        :ivar left:  left part of the conflict
        :ivar base:  base part of the conflict
        :ivar right: right part of the conflict

        :ivar sep1: complete line with the `<<<<<<<` separator
        :ivar sep2: complete line with the `|||||||` separator
        :ivar sep3: complete line with the `=======` separator
        :ivar sep4: complete line with the `>>>>>>>` separator
        """
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

    def __eq__(self, other):
        return isinstance(self, Conflict3Way) and\
               (self.line_number, self.line_num_left, self.line_num_right,
                self.left, self.base, self.right,
                self.sep1, self.sep2, self.sep3, self.sep4
                ) == (
                   other.line_number, other.line_num_left, other.line_num_right,
                   other.left, other.base, other.right,
                   other.sep1, other.sep2, other.sep3, other.sep4)

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
    """
    Represents a generic conflict of a 2-way merge.
    Contains its position and all the text components needed to completely reproduce the conflict.

    Implemented as a special case of `Conflict3Way`.
    """
    def __init__(self, line_number: int, line_num_left: int, line_num_right: int,
                 left: str, right: str, sep1: str, sep3: str, sep4: str):
        """
        :ivar base: should not be used
        :ivar sep2: must be an empty string
        """
        super().__init__(line_number, line_num_left, line_num_right, left, "NOSTR", right, sep1, "", sep3, sep4)

    def result(self, choice: Choice = None) -> str:
        _choice = self.choice if not choice else choice

        if _choice is Choice.undecided:
            return self.sep1 + self.left + self.sep3 + self.right + self.sep4
        else:
            return super().result(_choice)

    def description(self) -> str:
        return "\n left = \n" + self.left + "\n right = \n" + self.right


"""
A type alias for exporting `Conflict3Way` and `Conflict2Way` into other modules.
Use it when you do not care which implementation of conflict to use.
"""
Conflict = Conflict3Way
Conflict.__doc__ = "Supertype of `Conflict3Way` and `Conflict2Way`"


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

    def build(self) -> Conflict:
        if self.has_base:
            return Conflict3Way(self.line_number, self.line_num_left, self.line_num_right,
                                self.left, self.base, self.right, self.sep1, self.sep2, self.sep3, self.sep4)
        else:
            return Conflict2Way(self.line_number, self.line_num_left, self.line_num_right,
                                self.left, self.right, self.sep1, self.sep3, self.sep4)
