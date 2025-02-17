import pandas as pd

from streamlit_app.utils import (
    build_course_display_map,
    clean_course_name,
    combine_comment_lists,
    filter_courses,
    sort_course_display_names,
)


def test_filter_courses():
    # Create a sample DataFrame with various course names.
    data = {
        "course": ["Prealgebra 1 Self-Paced", "Teacher Training Module", "B2B Math Workshop", "Algebra A Self-Paced"]
    }
    df = pd.DataFrame(data)
    filtered = filter_courses(df)
    # Expect only the courses that don't contain "Teacher Training" or "B2B".
    expected_courses = {"Prealgebra 1 Self-Paced", "Algebra A Self-Paced"}
    assert set(filtered["course"]) == expected_courses


def test_clean_course_name():
    # Verify that "Self-Paced" is removed and whitespace is stripped.
    assert clean_course_name("Prealgebra 1 Self-Paced") == "Prealgebra 1"
    assert clean_course_name("Algebra A Self-Paced") == "Algebra A"
    assert (
        clean_course_name("   Introduction to Counting & Probability Self-Paced   ")
        == "Introduction to Counting & Probability"
    )


def test_build_course_display_map():
    # Build a display map from a DataFrame of courses.
    data = {"course": ["Prealgebra 1 Self-Paced", "Algebra A Self-Paced", "Algebra B Self-Paced"]}
    df = pd.DataFrame(data)
    display_map = build_course_display_map(df)
    expected_map = {
        "Prealgebra 1 Self-Paced": "Prealgebra 1",
        "Algebra A Self-Paced": "Algebra A",
        "Algebra B Self-Paced": "Algebra B",
    }
    assert display_map == expected_map


def test_sort_course_display_names():
    # Test that the sorting function orders courses in the preferred order.
    unsorted = [
        "Introduction to Algebra A",
        "Introduction to Counting & Probability",
        "Prealgebra 2",
        "Introduction to Algebra B",
        "Prealgebra 1",
    ]
    sorted_names = sort_course_display_names(unsorted)
    # Preferred order: Prealgebra 1, Prealgebra 2, Algebra A, Introduction to Counting & Probability, Algebra B
    expected = [
        "Prealgebra 1",
        "Prealgebra 2",
        "Introduction to Algebra A",
        "Introduction to Counting & Probability",
        "Introduction to Algebra B",
    ]
    assert sorted_names == expected


def test_combine_comment_lists():
    # Test that the combine_comment_lists function correctly parses and combines stringified lists.
    series = pd.Series(["['I love math']", "['Math is fun', 'I enjoy challenges']", "[]"])
    combined = combine_comment_lists(series)
    expected = ["I love math", "Math is fun", "I enjoy challenges"]
    assert combined == expected
