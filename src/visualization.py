# src/visualization.py

import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd


def sort_and_label_lessons(course_df: pd.DataFrame, mode: str = "chronological") -> pd.DataFrame:
    """
    Groups the course_df by lesson_title (if necessary) and sorts/labels the lessons based on the mode.

    For "chronological" mode, sorts by chapter_num and section_num and labels as "chapter.section Lesson Title".
    For "worst-to-best" mode, sorts by descending no_pct and appends the no percentage to the label.

    Returns the modified DataFrame with a new column "lesson_label".
    """
    # Group by lesson_title to collapse duplicates.
    grouped = (
        course_df.groupby("lesson_title")
        .agg({"chapter_num": "min", "section_num": "min", "yes_count": "sum", "no_count": "sum"})
        .reset_index()
    )

    total_counts = grouped["yes_count"] + grouped["no_count"]
    grouped["no_pct"] = (grouped["no_count"] / total_counts) * 100

    if mode == "worst-to-best":
        grouped = grouped.sort_values("no_pct", ascending=False)
        grouped["lesson_label"] = (
            grouped["chapter_num"].astype(str)
            + "."
            + grouped["section_num"].astype(str)
            + " "
            + grouped["lesson_title"]
            + " ("
            + grouped["no_pct"].round(1).astype(str)
            + "% no)"
        )
    elif mode == "chronological":
        grouped = grouped.sort_values(["chapter_num", "section_num"])
        grouped["lesson_label"] = (
            grouped["chapter_num"].astype(str)
            + "."
            + grouped["section_num"].astype(str)
            + " "
            + grouped["lesson_title"]
        )
    else:
        grouped = grouped.sort_values("lesson_title")
        grouped["lesson_label"] = grouped["lesson_title"]

    return grouped


def plot_stacked_bar(agg_df, course, output_filename=None, mode="chronological"):
    """
    Filters agg_df by course, applies sort_and_label_lessons() to generate lesson labels,
    then plots the bar chart.
    """
    course_df = agg_df[agg_df["course"] == course].copy()
    if course_df.empty:
        print(f"No data available for course '{course}'")
        return

    # Filter out lessons with "feedback" in the title.
    course_df = course_df[~course_df["lesson_title"].str.contains("feedback", case=False)]
    if course_df.empty:
        print(f"No lessons to plot after filtering out 'Feedback' lessons for '{course}'.")
        return

    # Assume numeric columns exist.
    labeled = sort_and_label_lessons(course_df, mode=mode)

    lessons = labeled["lesson_label"]
    yes_counts = labeled["yes_count"]
    no_counts = labeled["no_count"]

    plt.figure(figsize=(15, 6))
    plt.bar(lessons, yes_counts, label="Yes", color="blue")
    plt.bar(lessons, no_counts, bottom=yes_counts, label="No", color="red")

    plt.xlabel("Lesson Title", fontsize=10)
    plt.ylabel("Number of Responses", fontsize=10)
    plt.title(f"Feedback for {course}", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.legend(fontsize=9)
    plt.tight_layout()

    if output_filename:
        output_dir = os.path.dirname(output_filename)
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(output_filename)
        print(f"Plot saved to {output_filename}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Plot feedback for a specific course.")
    parser.add_argument("--course", type=str, required=True, help="The course name to visualize")
    parser.add_argument("--output", type=str, help="Optional output filename for the plot")
    parser.add_argument(
        "--data",
        type=str,
        default=os.path.join("data", "aggregated_feedback.csv"),
        help="Path to the aggregated CSV file (default: data/aggregated_feedback.csv)",
    )
    parser.add_argument(
        "--mode", type=str, default="chronological", help="Sorting mode: chronological or worst-to-best"
    )

    args = parser.parse_args()

    agg_df = pd.read_csv(args.data)
    plot_stacked_bar(agg_df, args.course, output_filename=args.output, mode=args.mode)


if __name__ == "__main__":
    main()
