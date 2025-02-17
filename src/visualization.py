# src/visualization.py

import matplotlib.pyplot as plt
import pandas as pd


def plot_stacked_bar(agg_df: pd.DataFrame, course: str):
    """
    Generate a stacked bar chart for a given course from the aggregated data.
    """
    # Filter the aggregated DataFrame for the given course
    course_df = agg_df[agg_df["course"] == course]
    if course_df.empty:
        print(f"No data available for course {course}")
        return

    lessons = course_df["lesson_title"]
    yes_counts = course_df["yes_count"]
    no_counts = course_df["no_count"]

    plt.figure(figsize=(10, 6))
    plt.bar(lessons, yes_counts, label="Yes", color="blue")
    plt.bar(lessons, no_counts, bottom=yes_counts, label="No", color="red")
    plt.xlabel("Lesson Title")
    plt.ylabel("Number of Responses")
    plt.title(f"Feedback for {course}")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.show()
