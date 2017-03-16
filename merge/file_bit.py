class FileBit:
    def __init__(self, line_number: int, text: str):
        self.line_number = line_number
        self.text = text

    def shrink_top_down(self, num: int) -> str:
        self.line_number += num
        lines = self.text.splitlines(keepends=True)

        assert len(lines) >= num

        self.text = "".join(lines[num:])
        return "".join(lines[:num])

    def shrink_bottom_up(self, num: int) -> str:
        lines = self.text.splitlines(keepends=True)

        assert len(lines) >= num

        self.text = "".join(lines[:-num])
        return "".join(lines[-num:])
