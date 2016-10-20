class Index:
    def __init__(self, values: []):
        self.values = values

        self._index = 0
        self._left_indices = list(range(len(values)))

    def next(self):
        if not self.is_empty():
            self._index += 1
            self._index %= self.size_left()

    def prev(self):
        if not self.is_empty():
            self._index -= 1
            self._index %= self.size_left()

    def value(self):
        if self.is_empty():
            raise ValueError("The index is empty")

        return self.values[self._left_indices[self._index]]

    def delete(self):
        if self.is_empty():
            raise ValueError("The index is empty")

        self._left_indices.pop(self._index)

        if not self.is_empty() > 0:
            self._index %= self.size_left()
        else:
            self._index = 0

    def size_left(self) -> int:
        return len(self._left_indices)

    def values_left(self) -> []:
        return self.values[self._left_indices]

    def is_empty(self):
        return self.size_left() == 0
