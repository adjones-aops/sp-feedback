import ast

import pandas as pd


def filter_courses(agg_df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes rows where the course name contains "Teacher Training" or "B2B".
    """
    df = agg_df.copy()
    df = df[~df["course"].str.contains("Teacher Training", case=False)]
    df = df[~df["course"].str.contains("B2B", case=False)]
    return df


def clean_course_name(full_name: str) -> str:
    """
    Removes 'Self-Paced' from the course name and strips extra whitespace.
    """
    return full_name.replace("Self-Paced", "").strip()


def build_course_display_map(agg_df: pd.DataFrame) -> dict:
    """
    Builds a dictionary mapping the full course name to a 'cleaned' display name
    (where 'Self-Paced' is removed) from the filtered DataFrame.
    """
    # First, filter out unwanted courses.
    filtered_df = filter_courses(agg_df)
    unique_courses = filtered_df["course"].unique()
    return {course: clean_course_name(course) for course in unique_courses}


def sort_course_display_names(display_names: list) -> list:
    """
    Returns a list of course display names sorted in the preferred order:
    Prealgebra 1, Prealgebra 2, Algebra A, Intro C&P, Algebra B,
    followed by any others alphabetically.
    """
    preferred_order = [
        "Prealgebra 1",
        "Prealgebra 2",
        "Introduction to Algebra A",
        "Introduction to Counting & Probability",
        "Introduction to Algebra B",
    ]
    prioritized = [name for name in preferred_order if name in display_names]
    others = sorted([name for name in display_names if name not in prioritized])
    return prioritized + others


def get_course_full_name(display_name: str, course_display_map: dict) -> str:
    """
    Given a cleaned display name, returns the original full course name
    from the provided dictionary. Returns None if no match is found.
    """
    for full_name, cleaned_name in course_display_map.items():
        if cleaned_name == display_name:
            return full_name
    return None


def combine_comment_lists(series):
    """Given a series of stringified comment lists, parse each and combine them into one list."""
    combined = []
    for item in series:
        try:
            c_list = ast.literal_eval(item)
            if isinstance(c_list, list) and c_list:
                combined.extend(c_list)
        except Exception:
            pass
    return combined
