# src/data_processor.py

import os

import pandas as pd


def aggregate_by_lesson(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate feedback by course, chapter_num, section_num, item_num, and lesson_title.
    This computes yes/no counts based on the percentages.
    """
    df = df.copy()

    # Convert string columns to numeric
    df["chapter_num"] = df["chapter"].astype(int)
    df["section_num"] = df["section"].astype(int)
    df["item_num"] = df["item"].astype(int)

    # Calculate counts based on percentages and total responses
    df["yes_count"] = (df["num_responses"] * df["yes_percentage"] / 100).round().astype(int)
    df["no_count"] = (df["num_responses"] * df["no_percentage"] / 100).round().astype(int)

    agg_df = (
        df.groupby(["course", "chapter_num", "section_num", "item_num", "lesson_title"])
        .agg(total_responses=("num_responses", "sum"), yes_count=("yes_count", "sum"), no_count=("no_count", "sum"))
        .reset_index()
    )

    return agg_df


if __name__ == "__main__":
    # Example usage
    input_csv = os.path.join(os.path.dirname(__file__), "..", "data", "parsed_feedback.csv")
    output_csv = os.path.join(os.path.dirname(__file__), "..", "data", "aggregated_feedback.csv")

    df = pd.read_csv(input_csv)
    agg_df = aggregate_by_lesson(df)
    agg_df.to_csv(output_csv, index=False)
    print(f"Aggregated data written to {output_csv}")
