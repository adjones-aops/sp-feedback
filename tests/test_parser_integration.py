# tests/test_parser_integration.py

import os

import pytest

from src.parser import parse_feedback


@pytest.fixture
def real_html():
    filepath = os.path.join(os.path.dirname(__file__), "fixtures", "feedback_page.html")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def test_multiple_courses_in_real_html(real_html):
    df = parse_feedback(real_html)
    # Check that we have at least some cards parsed.
    assert len(df) > 0, "No cards were parsed from the HTML"
    # Check that there are cards from more than one course.
    unique_courses = df["course"].unique()
    assert len(unique_courses) > 1, f"Expected multiple courses, got: {unique_courses}"
