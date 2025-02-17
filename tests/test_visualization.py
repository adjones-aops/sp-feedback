import pandas as pd
import pytest

from src.visualization import sort_and_label_lessons


@pytest.fixture
def sample_course_df():
    # Create a sample DataFrame with duplicate lessons that should be collapsed.
    data = {
        "course": ["Test Course"] * 5,
        "chapter": ["1", "1", "2", "2", "2"],
        "section": ["1", "1", "2", "2", "2"],
        "item": ["3", "4", "1", "2", "3"],
        "lesson_title": ["Lesson X", "Lesson X", "Lesson Y", "Lesson Y", "Lesson Y"],
        "num_responses": [10, 20, 15, 25, 5],
        "yes_percentage": [50, 60, 70, 80, 90],
        "no_percentage": [50, 40, 30, 20, 10],
    }
    df = pd.DataFrame(data)
    # Simulate numeric conversion as in the data_processor.
    df["chapter_num"] = df["chapter"].astype(int)
    df["section_num"] = df["section"].astype(int)
    df["item_num"] = df["item"].astype(int)
    # Compute yes_count and no_count similarly.
    df["yes_count"] = (df["num_responses"] * df["yes_percentage"] / 100).round().astype(int)
    df["no_count"] = (df["num_responses"] * df["no_percentage"] / 100).round().astype(int)
    return df


def test_sort_and_label_chronological(sample_course_df):
    # Test the sorting in chronological mode.
    grouped = sort_and_label_lessons(sample_course_df, mode="chronological")
    # Expecting two distinct lessons: one for Lesson X and one for Lesson Y.
    first_lesson = grouped.iloc[0]["lesson_title"]
    second_lesson = grouped.iloc[1]["lesson_title"]
    expected_first = "Lesson X"
    expected_second = "Lesson Y"
    assert first_lesson == expected_first, f"Expected first lesson '{expected_first}', got '{first_lesson}'"
    assert second_lesson == expected_second, f"Expected second lesson '{expected_second}', got '{second_lesson}'"

    # Check that each lesson_label includes only chapter and section.
    for label in grouped["lesson_label"]:
        # Assume label format: "chapter.section Lesson Title"
        label_prefix = label.split()[0]  # Should be something like "1.1"
        parts = label_prefix.split(".")
        assert len(parts) == 2, f"Expected lesson label prefix to have 2 parts separated by '.', got: {label_prefix}"


def test_sort_and_label_worst_to_best(sample_course_df):
    # Test the sorting in worst-to-best mode.
    grouped = sort_and_label_lessons(sample_course_df, mode="worst-to-best")
    # Verify that no_pct is in descending order.
    no_pct_list = grouped["no_pct"].tolist()
    sorted_no_pct = sorted(no_pct_list, reverse=True)
    assert no_pct_list == sorted_no_pct, f"Expected no_pct descending order, got {no_pct_list}"

    # Check that lesson_label includes a '%' symbol indicating the no_pct value.
    for label in grouped["lesson_label"]:
        assert "%" in label, f"Expected '%' in lesson label, got '{label}'"
