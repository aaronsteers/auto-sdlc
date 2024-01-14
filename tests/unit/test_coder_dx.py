from pathlib import Path
from auto_sdlc.python_developer import FilePosition, FileRange

def test_file_range_str(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\n")
    file_range = FileRange(file=file_path, start=1, end=2)
    assert str(file_range) == f"{file_path}:1-2"

def test_file_range_text_getter(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\n")
    file_range = FileRange(file=file_path, start=1, end=2)
    assert file_range.text == "Hello\nWorld\n"

def test_file_range_text_setter(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\n")
    file_range = FileRange(file=file_path, start=1, end=2)
    file_range.text = "New\nText\n"
    assert file_path.read_text() == "New\nText\n"

def test_file_position_index(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\n")
    file_position = FilePosition(file=file_path, line=2, column=3)
    assert file_position.index == 9

def test_file_position_str(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_position = FilePosition(file=file_path, line=3, column=5)
    assert str(file_position) == "test_file.txt:3:5"

def test_file_position_line_start_position(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_position = FilePosition(file=file_path, line=2, column=3)
    line_start_position = file_position.line_start_position
    assert line_start_position.file == file_path
    assert line_start_position.line == 2
    assert line_start_position.column == 0

def test_file_position_line_end_position(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\n")
    file_position = FilePosition(file=file_path, line=2, column=3)
    line_end_position = file_position.line_end_position
    assert line_end_position.file == file_path
    assert line_end_position.line == 2
    assert line_end_position.column == 5

def test_file_position_read_line(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\n")
    file_position = FilePosition(file=file_path, line=2, column=3)
    assert file_position.read_line() == "rld"

def test_file_position_read_lines(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\nThis is a test\n")
    file_position = FilePosition(file=file_path, line=2, column=3)
    assert file_position.read_lines(lines=2) == "rld\nThis is a test"

def test_file_position_insert_string(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\n")
    file_position = FilePosition(file=file_path, line=2, column=3)
    file_position.insert_string("!")
    assert file_path.read_text() == "Hello\nWor!ld\n"

def test_file_position_from_index(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\nThis is a test\n")
    file_position = FilePosition.from_index(file=file_path, index=14)
    assert file_position.file == file_path
    assert file_position.line == 3
    assert file_position.column == 2

def test_file_position_from_search(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\nThis is a test\n")
    file_position = FilePosition.from_search("test", file_path=file_path)
    assert file_position.file == file_path
    assert file_position.line == 3
    assert file_position.column == 11

def test_file_position_find_next(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello\nWorld\nThis is a test\n")
    file_position = FilePosition(file=file_path, line=2, column=3)
    next_position = file_position.find_next("is")
    assert next_position.file == file_path
    assert next_position.line == 3
    assert next_position.column == 3
