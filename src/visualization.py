# src/visualization.py

import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd


def plot_stacked_bar(agg_df, course, output_filename=None, mode="chronological"):
    """
    mode can be:
      - "chronological": sorts by the numeric prefix (min chapter and section) of the grouped lesson.
      - "worst-to-best": sorts by descending aggregated no percentage.

    Before plotting, this function groups records by lesson_title (collapsing duplicates).
    It sums the yes_count, no_count, and total_responses, and uses the minimum chapter_num and section_num
    for ordering and label creation.
    """
    # Filter for the given course
    course_df = agg_df[agg_df["course"] == course].copy()
    if course_df.empty:
        print(f"No data available for course '{course}'")
        return

    # Filter out lessons with "feedback" in the lesson title.
    course_df = course_df[~course_df["lesson_title"].str.contains("feedback", case=False)]
    if course_df.empty:
        print(f"No lessons to plot after filtering out 'Feedback' lessons for '{course}'.")
        return

    # Group by lesson_title to collapse duplicate lessons.
    # Sum yes_count, no_count, total_responses; take the minimum chapter_num and section_num.
    grouped = (
        course_df.groupby("lesson_title")
        .agg(
            {
                "yes_count": "sum",
                "no_count": "sum",
                "total_responses": "sum",
                "chapter_num": "min",
                "section_num": "min",
            }
        )
        .reset_index()
    )

    # Calculate aggregated no_pct.
    total_counts = grouped["yes_count"] + grouped["no_count"]
    grouped["no_pct"] = (grouped["no_count"] / total_counts) * 100

    # Build a lesson label that uses the numeric prefix (chapter.section) and the lesson title.
    grouped["lesson_label"] = (
        grouped["chapter_num"].astype(str) + "." + grouped["section_num"].astype(str) + " " + grouped["lesson_title"]
    )

    # Sorting
    if mode == "worst-to-best":
        grouped = grouped.sort_values("no_pct", ascending=False)
        # Optionally, add the no_pct to the label:
        grouped["lesson_label"] = grouped["lesson_label"] + " (" + grouped["no_pct"].round(1).astype(str) + "% no)"
    elif mode == "chronological":
        # Sort by the numeric prefix.
        grouped = grouped.sort_values(["chapter_num", "section_num"])
    else:
        # Fallback: sort alphabetically by lesson_label.
        grouped = grouped.sort_values("lesson_label")

    # Now plot using the grouped data.
    lessons = grouped["lesson_label"]
    yes_counts = grouped["yes_count"]
    no_counts = grouped["no_count"]

    plt.figure(figsize=(20, 8))
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
