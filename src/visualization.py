# src/visualization.py

import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd


def plot_stacked_bar(agg_df, course, output_filename=None, mode="numeric"):
    """
    mode can be:
      - "numeric": sort by chapter_num, section_num, item_num
      - "worst": sort by highest no percentage to lowest
    """
    course_df = agg_df[agg_df["course"] == course].copy()
    if course_df.empty:
        print(f"No data available for course '{course}'")
        return

    # Filter out chapter feedback lessons
    course_df = course_df[~course_df["lesson_title"].str.contains("feedback", case=False)]
    if course_df.empty:
        print(f"No lessons to plot after filtering out 'Feedback' lessons for '{course}'.")
        return

    # Calculate no_pct for sorting if needed
    total = course_df["yes_count"] + course_df["no_count"]
    course_df["no_pct"] = (course_df["no_count"] / total) * 100

    if mode == "worst":
        course_df = course_df.sort_values("no_pct", ascending=False)
        # Create an x-axis label for clarity
        course_df["lesson_label"] = (
            course_df["lesson_title"] + " (" + course_df["no_pct"].round(1).astype(str) + "% no)"
        )
    elif mode == "numeric":
        # If numeric columns exist, sort on them
        if all(col in course_df.columns for col in ["chapter_num", "section_num", "item_num"]):
            course_df = course_df.sort_values(["chapter_num", "section_num", "item_num"])
            course_df["lesson_label"] = (
                course_df["chapter_num"].astype(str)
                + "."
                + course_df["section_num"].astype(str)
                + "."
                + course_df["item_num"].astype(str)
                + " "
                + course_df["lesson_title"]
            )
        else:
            # Fallback
            course_df = course_df.sort_values("lesson_title")
            course_df["lesson_label"] = course_df["lesson_title"]
    else:
        # Default fallback: sort by lesson_title
        course_df = course_df.sort_values("lesson_title")
        course_df["lesson_label"] = course_df["lesson_title"]

    # Now plot
    lessons = course_df["lesson_label"]
    yes_counts = course_df["yes_count"]
    no_counts = course_df["no_count"]

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
        try:
            plt.show()
        except Exception as e:
            print(f"Unable to display interactive plot. Error: {e}. Consider saving the plot to a file.")


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
    parser.add_argument("--mode", type=str, default="numeric", help="The mode to use for sorting the lessons")

    args = parser.parse_args()

    agg_df = pd.read_csv(args.data)
    plot_stacked_bar(agg_df, args.course, output_filename=args.output, mode=args.mode)


if __name__ == "__main__":
    main()
