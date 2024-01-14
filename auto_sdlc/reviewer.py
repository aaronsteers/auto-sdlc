"""An automated code reviewer."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel
from auto_sdlc import ask
from auto_sdlc.coder_dx import get_docstring, set_docstring
from auto_sdlc.file_ops import FilePlace, FileRange, FilePosition

import difflib

def _generate_diff(before: str, after: str) -> str:
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    diff = difflib.unified_diff(before_lines, after_lines)
    return ''.join(diff)


class SuggestionBase(ABC, BaseModel):

    target: FilePlace
    suggested_text: str
    description: str

    @abstractmethod
    def apply(self) -> None:
        """Apply suggestion."""
        raise NotImplementedError

    @abstractmethod
    @property
    def diff(self) -> str:
        """Preview diff."""
        raise NotImplementedError

class EditSuggestion(BaseModel):

    target: FileRange
    suggested_text: str
    description: str

    def apply(self) -> None:
        """Apply suggestion."""
        self.file_range.text = self.suggestion_text

    @property
    def diff(self) -> str:
        """Preview diff."""
        previous_3_lines = self.target.previous_lines(3)
        next_3_lines = self.target.next_lines(3)
        return _generate_diff(
            previous_3_lines.text + self.target.text + next_3_lines.text,
            previous_3_lines.text + self.suggested_text + next_3_lines.text,
        )

class InsertSuggestion(BaseModel):

    target: FilePosition
    suggested_text: str
    description: str

    def apply(self) -> None:
        """Apply suggestion."""
        self.target.insert_string(self.suggested_text)

    @property
    def diff(self) -> str:
        """Preview diff."""
        previous_3_lines = self.target.previous_lines(3)
        next_3_lines = self.target.next_lines(3)
        curr_line_before = self.target.current_line[:self.target.column]
        curr_line_after = self.target.current_line[self.target.column:]
        new_curr_line = curr_line_before + self.suggested_text + curr_line_after
        return _generate_diff(
            previous_3_lines.text + self.current_line.text + next_3_lines.text,
            previous_3_lines.text + new_curr_line  + next_3_lines.text,
        )

class MissingDocstringSuggestion(InsertSuggestion):

    description: str = "Missing docstring in this file."
    file: Path
    
    @property
    def target(self) -> FilePosition:
        """Get target."""
        return FilePosition.from_index(self.file, 0)

    @lru_cache
    @property
    def suggested_text(self) -> None:
        """Initialize."""
        return ask.suggest_docstring(self.file)

    def apply(self) -> None:
        """Apply suggestion."""
        set_docstring(self.file_range.file, self.docstring)

def get_file_suggestions(file_path: Path) -> Iterator[SuggestionBase]:
    """Get file suggestions."""
    if get_docstring(file_path) is None:
        yield MissingDocstringSuggestion(FileRange(file_path, 0, 0))
