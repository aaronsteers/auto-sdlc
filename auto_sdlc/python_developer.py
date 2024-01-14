from pathlib import Path

from auto_sdlc.file_ops import insert_lines, FileRange, FilePosition


def get_docstring_range(file_path: Path) -> FileRange | None:
    """Get docstring from a file."""
    start_position = FilePosition.from_search(
        '"""',
        file_path=file_path,
    )
    if not start_position:
        return None
    end_position = start_position.find_next('"""')
    if not end_position:
        return None

    return FileRange(
        file=file_path,
        start=start_position.line,
        end=end_position.line,
    )


def get_docstring(file_path: Path) -> str | None:
    """Get docstring from a file."""
    docstring_range = get_docstring_range(file_path)
    if docstring_range is None:
        return None

    return docstring_range.text


def set_docstring(file_path: Path, docstring: str) -> None:
    """Set docstring to a file."""
    if not docstring.endswith("\n"):
        raise ValueError("Docstring must end with a newline.")
    if not docstring.startswith('"""') or not docstring.endswith('"""\n'):
        raise ValueError("Docstring must start and end with three double quotes.")

    docstring_range = get_docstring_range(file_path)
    if docstring_range is None:
        # If there is no docstring, add one
        insert_lines(file_path, docstring, at_line=0)
    else:
        # If there is a docstring, replace it
        docstring_range.text = docstring
