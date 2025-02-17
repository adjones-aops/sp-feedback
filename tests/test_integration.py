import os

import pytest

from src.data_processor import aggregate_by_lesson
from src.parser import parse_feedback


@pytest.fixture
def real_html():
    filepath = os.path.join(os.path.dirname(__file__), "fixtures", "feedback_page.html")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def test_integration_pipeline(real_html):
    # Parse the HTML into a DataFrame
    parsed_df = parse_feedback(real_html)

    # Check that the expected columns are present in the parsed DataFrame.
    expected_columns = {
        "course",
        "lesson_title",
        "chapter",
        "section",
        "item",
        "num_responses",
        "yes_percentage",
        "no_percentage",
        "comments",
    }
    missing = expected_columns - set(parsed_df.columns)
    assert not missing, f"Missing expected columns in parsed DataFrame: {missing}"

    # Ensure that we parsed at least one card.
    assert len(parsed_df) > 0, "No cards were parsed from the HTML"

    # Check that there are multiple courses.
    unique_courses = parsed_df["course"].unique()
    assert len(unique_courses) > 1, f"Expected multiple courses, got: {unique_courses}"

    # Now run the aggregation step.
    agg_df = aggregate_by_lesson(parsed_df)

    # Check that the aggregated DataFrame has the expected aggregated columns.
    expected_agg_columns = {
        "course",
        "lesson_title",
        "total_responses",
        "yes_count",
        "no_count",
        "chapter_num",
        "section_num",
        "item_num",
    }
    missing_agg = expected_agg_columns - set(agg_df.columns)
    assert not missing_agg, f"Missing expected aggregated columns: {missing_agg}"

    # For each aggregated row, check that total_responses equals yes_count + no_count.
    for idx, row in agg_df.iterrows():
        total = row["yes_count"] + row["no_count"]
        assert (
            row["total_responses"] == total
        ), f"Total responses mismatch at row {idx}: {row['total_responses']} != {total}"
