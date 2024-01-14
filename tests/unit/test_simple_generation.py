from pathlib import Path
from textwrap import dedent

from auto_sdlc.coder_dx import set_docstring, get_docstring 
from auto_sdlc.ask import get_answer, yes_or_no


SAMPLE_PROJECT_PATH = Path("./../resources/sample_project")


def test_llm_yes_or_no():
    """Test LLM."""
    answer = yes_or_no('Please reply "yes"')
    assert answer.answer is True, f"The LLM should reply yes. Debug info: {answer}"


def test_author_docstring():
    """Test author docstring."""
    file_name = "authors.py"
    file_contents = dedent(
        """
        def get_favorite_scifi_writers():
            return ["Isaac Asimov", "Octavia Butler", "Terry Pratchett"]

        def get_favorite_fantasy_writers():
            return ["Octavia Butler", "Toni Morrison", "Terry Pratchett"]
    """
    )
    prompt = dedent(
        f"""
        I want you to write a docstring for this file."
        Please read the contents of the file below and generate just the docstring, with no other commentary.
        Your response should be a string starting with three double quotes and ending with three double quotes.
        The first line of the docstring should be a one-line summary of the file, no longer than 60 characters.
        The second line should always be blank, meaning the first line should be followed by a blank line.
        Starting on the third line, you can write a more detailed summary describing the file."
        For example:
        \"\"\"This file contains mathematical operations.

        This file contains functions for adding, subtracting, multiplying, and dividing numbers.        
        \"\"\"
        ------------
        {file_name}
        ------------
        {file_contents}
        ------------
        """
    )
    docstring_proposal = get_answer(prompt)
    eval_result = yes_or_no(dedent(
        f"""Is the below a valid docstring? (y/n)
        To be valid, the docstring must start and end with three double quotes. Evaluate everything 
        after the dashed line that follows, excluding the dashed line itself.
        ------------
        {docstring_proposal}
        """
    ))
    assert eval_result, "y"


def test_add_docstring():
    """Test add docstring to a file."""
    # TODO: Add test for adding docstring to a file.


def test_modify_docstring():
    """Test modify docstring to a file."""
    # TODO: Add test for modifying docstring to a file.
