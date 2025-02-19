# flake8: noqa: E402
import os
import sys

# Add the repository root (one level up) to sys.path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# (Optional) Debug print to check that the parent directory is included:
print("Updated sys.path:", sys.path)

import subprocess
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import streamlit_app.bootstrap as bootstrap  # noqa: F401
from src.visualization import plot_stacked_bar
from streamlit_app.utils import (
    build_course_display_map,
    combine_comment_lists,
    filter_courses,
    get_course_full_name,
    sort_course_display_names,
)


def run_pipeline():
    st.info("Running pipeline: scraping, parsing, and aggregating data.")

    result_scraper = subprocess.run([sys.executable, "src/scraper.py"], capture_output=True, text=True)
    if result_scraper.returncode != 0:
        st.error("Scraper failed:\n" + result_scraper.stderr)
        return False
    st.info("Scraping complete.")

    result_parser = subprocess.run([sys.executable, "src/parser.py"], capture_output=True, text=True)
    if result_parser.returncode != 0:
        st.error("Parser failed:\n" + result_parser.stderr)
        return False
    st.info("Parsing complete.")

    result_aggregator = subprocess.run([sys.executable, "src/data_processor.py"], capture_output=True, text=True)
    if result_aggregator.returncode != 0:
        st.error("Aggregation failed:\n" + result_aggregator.stderr)
        return False
    st.info("Aggregation complete.")

    return True


def get_plot_image(agg_df, course, mode):
    plot_stacked_bar(agg_df, course, output_filename=None, mode=mode)
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf


def main():
    # Must be the first Streamlit call
    st.set_page_config(layout="wide")
    st.title("Self-Paced Feedback Visualization")

    if st.button("Scrape & Update Data"):
        success = run_pipeline()
        if success:
            st.success("Data successfully updated!")
        else:
            st.error("Data update failed. Check logs above.")

    data_path = os.path.join("data", "aggregated_feedback.csv")
    if not os.path.exists(data_path):
        st.error(f"Aggregated data not found at {data_path}. Please run the pipeline first.")
        return
    agg_df = pd.read_csv(data_path)

    # Filter and build course mapping.
    agg_df = filter_courses(agg_df)
    course_display_map = build_course_display_map(agg_df)
    display_names = sort_course_display_names(list(course_display_map.values()))

    st.sidebar.header("Visualization Options")
    selected_display_name = st.sidebar.selectbox("Select a Course", display_names)
    selected_course = get_course_full_name(selected_display_name, course_display_map)
    if selected_course is None:
        st.warning("No matching course found. Using first available course.")
        selected_course = list(course_display_map.keys())[0]

    mode = st.sidebar.radio(
        "Select Sorting Mode",
        ("chronological", "worst-to-best"),
        index=0,
        help="Chronological sorts by chapter, section, and item; Worst-to-best sorts by descending no percentage.",
    )

    st.header(f"Feedback for {selected_display_name} ({mode.replace('-', ' ').capitalize()} Mode)")

    # Use Streamlit tabs to separate the chart from the comments.
    tab1, tab2 = st.tabs(["Visualization", "Detailed Comments"])

    with tab1:
        plot_image = get_plot_image(agg_df, selected_course, mode)
        st.image(plot_image, use_container_width=True)
        st.download_button(
            label="Download Plot as PNG",
            data=plot_image,
            file_name=f"{selected_display_name.replace(' ', '_')}_{mode}_plot.png",
            mime="image/png",
        )

    with tab2:
        st.subheader("Student Feedback Comments")
        parsed_path = os.path.join("data", "parsed_feedback.csv")
        if os.path.exists(parsed_path):
            parsed_df = pd.read_csv(parsed_path)
            # Filter by selected course and remove lessons with "feedback" in title.
            course_feedback = parsed_df[parsed_df["course"] == selected_course]
            course_feedback = course_feedback[
                ~course_feedback["lesson_title"].str.contains("feedback", case=False, na=False)
            ]

            # Group by lesson_title and combine comments.
            grouped_comments = (
                course_feedback.groupby("lesson_title")["comments"].apply(combine_comment_lists).reset_index()
            )

            # Group the aggregated data by lesson_title to get numeric info (chapter_num, section_num, etc.)
            grouped_agg = (
                agg_df.groupby("lesson_title")
                .agg({"chapter_num": "min", "section_num": "min", "yes_count": "sum", "no_count": "sum"})
                .reset_index()
            )
            total_counts = grouped_agg["yes_count"] + grouped_agg["no_count"]
            grouped_agg["no_pct"] = (grouped_agg["no_count"] / total_counts) * 100

            # Merge the grouped comments with the numeric aggregated data.
            merged = pd.merge(grouped_comments, grouped_agg, on="lesson_title", how="inner")

            # Sort the merged DataFrame according to mode.
            if mode == "worst-to-best":
                merged = merged.sort_values("no_pct", ascending=False)
            elif mode == "chronological":
                merged = merged.sort_values(["chapter_num", "section_num"])
            else:
                merged = merged.sort_values("lesson_title")

            # Display each lesson's combined comments in a single expander.
            for _, row in merged.iterrows():
                # Use the minimum chapter and section numbers for the label.
                lesson_label = f"{row['chapter_num']}.{row['section_num']} {row['lesson_title']}"
                comment_list = row["comments"]
                # Skip if there are no comments.
                if not comment_list:
                    continue
                # Join the individual responses with a double newline for readability.
                comments_text = "\n\n".join(comment_list)
                with st.expander(lesson_label):
                    st.write(comments_text)
        else:
            st.info("Parsed feedback data not found. Please run the pipeline.")

    # Also display aggregated data table if desired.
    st.subheader("Aggregated Data")
    filtered_df = agg_df[agg_df["course"] == selected_course]
    st.dataframe(filtered_df)


if __name__ == "__main__":
    main()
