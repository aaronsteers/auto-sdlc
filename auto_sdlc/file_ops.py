
from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel


def find_line_and_column_from_index(file, index) -> tuple[int, int] | tuple[None, None]:
    """Find the line and column from the index of a file."""
    file_text = file.read_text()
    lines = file_text.splitlines()
    chars_left = index
    for line_number, line in enumerate(lines):
        if len(line) + 1 > chars_left:
            return line_number + 1, chars_left
        else:
            chars_left -= len(line) + 1
    return None, None  # return None if index is out of range


def insert_lines(file_path: Path, text: str, at_line: int) -> None:
    """Insert lines into a file."""
    file_text = file_path.read_text()
    lines = file_text.splitlines()
    lines.insert(at_line, text)
    file_path.write_text("\n".join(lines))


class FilePlace(ABC, BaseModel):
    """Abstract file place."""

    @abstractmethod
    def previous_lines(self, lines: int) -> "FileRange":
        """Previous lines."""
        ...

    @abstractmethod
    def next_lines(self, lines: int) -> "FileRange":
        """Next lines."""
        ...

    @property
    def file_line_count(self) -> int:
        """Number of lines in the file."""
        return len(self.file.read_text().splitlines())

    @property
    def parent_file_range(self) -> "FileRange":
        """Parent file range."""
        return FileRange(
            file=self.file,
            start=1,
            end=self.file_line_count,
        )


class FilePosition(FilePlace):
    """File Position."""
    file: Path
    line: int
    column: int

    @property
    def index(self) -> int:
        """Index of the file position.

        To calculate, we need to add the number of characters in each line before the current line.
        """
        return sum(len(line) + 1 for line in self.file.read_text().splitlines()[:self.line - 1]) + self.column

    @index.setter
    def index(self, value) -> None:
        """Set index of the file position.

        To set, we need to find the line and column of the index.
        """
        line, column = find_line_and_column_from_index(self.file, value)
        if line is None or column is None:
            raise ValueError("Index is out of range.")

        self.line = line
        self.column = column

    def __str__(self) -> str:
        """String representation of the file position."""
        return f"{self.file.name}:{self.line}:{self.column}"

    @property
    def line_start_position(self) -> "FilePosition":
        """Line start position."""
        return FilePosition(
            file=self.file,
            line=self.line,
            column=0,
        )

    @property
    def line_end_position(self) -> "FilePosition":
        """Line start position."""
        return FilePosition(
            file=self.file,
            line=self.line,
            column=len(self.file.read_text().splitlines()[self.line -1]),
        )

    def read_line(self, *, from_start: bool = False) -> str:
        """Text of the file position."""
        if from_start:
            return self.file.read_text().splitlines()[self.line - 1]

        return self.file.read_text().splitlines()[self.line - 1][self.column - 1:]

    def read_lines(self, lines: int, *, from_start: bool = False) -> str:
        first_line = self.read_line(from_start=from_start)
        if lines == 1:
            return first_line

        addl_lines = self.file.read_text().splitlines()[self.line:self.line + lines]
        return "\n".join([first_line] + addl_lines)

    def insert_string(self, string: str) -> None:
        """Insert string into the file position."""
        file_text = self.file.read_text()
        lines = file_text.splitlines()
        lines[self.line - 1] = lines[self.line -1][:self.column] + string + lines[self.line - 1][self.column:]
        self.file.write_text("\n".join(lines) + "\n")

    @classmethod
    def from_search(
        cls,
        search: str,
        /,
        *,
        file_path: Path,
    ) -> "FilePosition | None":
        """Get file position from search."""
        file_text = file_path.read_text()
        if search not in file_text:
            return None

        return FilePosition.from_index(
            file=file_path,
            index=file_text.index(search) + 1,
        )

    @classmethod
    def from_index(cls, file: Path, index: int) -> "FilePosition":
        """Get file position from index."""
        line, column = find_line_and_column_from_index(file, index)
        if line is None or column is None:
            raise ValueError("Index is out of range.")

        return FilePosition(
            file=file,
            line=line,
            column=column,
        )

    def find_next(self, search: str) -> "FilePosition | None":
        """Find after."""
        file_text = self.file.read_text()
        if search not in file_text:
            return None

        return FilePosition.from_index(
            file=self.file,
            index=file_text.index(search, self.index + 1) + 1,
        )

    def previous_lines(self, lines: int) -> "FileRange":
        """Previous lines."""
        return FileRange(
            file=self.file,
            start=max(1, self.line - lines),
            end=self.start,
        )
    
    def current_line(self) -> "FileRange":
        """Current line."""
        return FileRange(
            file=self.file,
            start=self.line,
            end=self.line,
        )

    def next_lines(self, lines: int) -> "FileRange":
        """Next lines."""
        return FileRange(
            file=self.file,
            start=self.line + 1,
            end=min(self.end + lines, self.file_line_count),
        )


class FileRange(FilePlace):
    """File Range."""
    file: Path
    start: int
    end: int

    def __str__(self) -> str:
        """String representation of the file range."""
        return f"{self.file}:{self.start}-{self.end}"

    @property
    def start_position(self) -> FilePosition:
        """Start position."""
        return FilePosition(
            file=self.file,
            line=self.start,
            column=0,
        )

    @property
    def end_position(self) -> FilePosition:
        """End position."""
        return FilePosition(
            file=self.file,
            line=self.end,
            column=len(self.file.read_text().splitlines(keepends=1)[self.end - 1]),
        )

    @property
    def text(self) -> str:
        """Text of the file range."""
        return "\n".join(self.file.read_text().splitlines()[self.start - 1:self.end]) + "\n"

    @text.setter
    def text(self, value) -> None:
        """Set text of the file range."""
        file_text = self.file.read_text()
        lines = file_text.splitlines()
        lines_before = lines[:self.start - 1]
        lines_after = lines[self.end:]
        new_text = "\n".join(lines_before + value.splitlines() + lines_after) + "\n"
        self.file.write_text(new_text)

    def previous_lines(self, lines: int) -> "FileRange":
        """Previous lines."""
        return FileRange(
            file=self.file,
            start=max(1, self.start - lines),
            end=self.start,
        )

    def next_lines(self, lines: int) -> "FileRange":
        """Next lines."""
        return FileRange(
            file=self.file,
            start=self.end + 1,
            end=min(self.end + lines, self.file_line_count),
        )
