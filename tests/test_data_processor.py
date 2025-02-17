import pandas as pd

from src.data_processor import aggregate_by_lesson


def test_aggregate_by_lesson_multiple_groups():
    # Create a DataFrame with two distinct lessons.
    data = {
        "course": ["Course A", "Course A", "Course A", "Course A"],
        "chapter": ["1", "1", "1", "1"],
        "section": ["2", "2", "3", "3"],
        "item": ["3", "3", "1", "1"],
        "lesson_title": ["Lesson X", "Lesson X", "Lesson Y", "Lesson Y"],
        "num_responses": [10, 20, 15, 25],
        "yes_percentage": [50, 60, 80, 70],
        "no_percentage": [50, 40, 20, 30],
        "comments": ["['good']", "['better']", "['okay']", "['great']"],
    }
    df = pd.DataFrame(data)
    agg_df = aggregate_by_lesson(df)

    # We expect two aggregated rows, one for "Lesson X" and one for "Lesson Y".
    assert len(agg_df) == 2

    # For Lesson X:
    lesson_x = agg_df[agg_df["lesson_title"] == "Lesson X"].iloc[0]
    expected_total_responses_x = 10 + 20  # 30
    expected_yes_x = round(10 * 50 / 100) + round(20 * 60 / 100)  # 5 + 12 = 17
    expected_no_x = round(10 * 50 / 100) + round(20 * 40 / 100)  # 5 + 8 = 13

    actual_total_responses_x = lesson_x["total_responses"]
    actual_yes_x = lesson_x["yes_count"]
    actual_no_x = lesson_x["no_count"]

    assert (
        actual_total_responses_x == expected_total_responses_x
    ), f"Expected total_responses {expected_total_responses_x}, got {actual_total_responses_x}"
    assert actual_yes_x == expected_yes_x, f"Expected yes_count {expected_yes_x}, got {actual_yes_x}"
    assert actual_no_x == expected_no_x, f"Expected no_count {expected_no_x}, got {actual_no_x}"

    # For Lesson Y:
    lesson_y = agg_df[agg_df["lesson_title"] == "Lesson Y"].iloc[0]
    expected_total_responses_y = 15 + 25  # 40
    expected_yes_y = round(15 * 80 / 100) + round(25 * 70 / 100)  # 12 + 18 = 30
    expected_no_y = round(15 * 20 / 100) + round(25 * 30 / 100)  # 3 + 8 = 11

    actual_total_responses_y = lesson_y["total_responses"]
    actual_yes_y = lesson_y["yes_count"]
    actual_no_y = lesson_y["no_count"]

    assert (
        actual_total_responses_y == expected_total_responses_y
    ), f"Expected total_responses {expected_total_responses_y}, got {actual_total_responses_y}"
    assert actual_yes_y == expected_yes_y, f"Expected yes_count {expected_yes_y}, got {actual_yes_y}"
    assert actual_no_y == expected_no_y, f"Expected no_count {expected_no_y}, got {actual_no_y}"
