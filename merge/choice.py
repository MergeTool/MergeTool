from enum import Enum


class Choice(Enum):
    undecided = 0
    left = 1
    right = 2
    both = 3

    def is_resolved(self) -> bool:
        return self is not self.undecided
