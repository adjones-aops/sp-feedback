# src/data_processor.py

import pandas as pd


def aggregate_by_lesson(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate feedback by lesson title.
    Returns a DataFrame grouped by course and lesson_title with counts of yes and no responses.
    """
    # We assume that yes_percentage and no_percentage represent percentages but we need counts.
    # Here, we simply use num_responses as the total and derive counts based on percentages.
    # For a more robust implementation, your parser might capture raw counts directly.
    df = df.copy()
    df["yes_count"] = (df["num_responses"] * df["yes_percentage"] / 100).round().astype(int)
    df["no_count"] = (df["num_responses"] * df["no_percentage"] / 100).round().astype(int)
    agg_df = (
        df.groupby(["course", "lesson_title"])
        .agg(total_responses=("num_responses", "sum"), yes_count=("yes_count", "sum"), no_count=("no_count", "sum"))
        .reset_index()
    )
    return agg_df
