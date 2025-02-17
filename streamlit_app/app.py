# streamlit_app/app.py

import os
import subprocess
import sys
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.visualization import plot_stacked_bar


def run_pipeline():
    """
    Runs the entire backend pipeline:
    1. Scrape the webpage and save the HTML to data/feedback_page.html.
    2. Parse the saved HTML into data/parsed_feedback.csv.
    3. Aggregate the parsed data into data/aggregated_feedback.csv.
    """
    st.info("Running pipeline: scraping, parsing, and aggregating data.")

    # Run scraper
    result_scraper = subprocess.run([sys.executable, "src/scraper.py"], capture_output=True, text=True)
    if result_scraper.returncode != 0:
        st.error("Scraper failed:\n" + result_scraper.stderr)
        return False
    st.info("Scraping complete.")

    # Run parser
    result_parser = subprocess.run([sys.executable, "src/parser.py"], capture_output=True, text=True)
    if result_parser.returncode != 0:
        st.error("Parser failed:\n" + result_parser.stderr)
        return False
    st.info("Parsing complete.")

    # Run aggregator
    result_aggregator = subprocess.run([sys.executable, "src/data_processor.py"], capture_output=True, text=True)
    if result_aggregator.returncode != 0:
        st.error("Aggregation failed:\n" + result_aggregator.stderr)
        return False
    st.info("Aggregation complete.")

    return True


def get_plot_image(agg_df, course, mode):
    # Generate the plot without output_filename
    plot_stacked_bar(agg_df, course, output_filename=None, mode=mode)
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf


def main():
    st.title("Self-Paced Feedback Visualization")

    # Provide a button to run the entire pipeline.
    if st.button("Scrape & Update Data"):
        success = run_pipeline()
        if success:
            st.success("Data successfully updated!")
        else:
            st.error("Data update failed. Check logs above.")

    # Load aggregated data
    data_path = os.path.join("data", "aggregated_feedback.csv")
    if not os.path.exists(data_path):
        st.error(f"Aggregated data not found at {data_path}. Please run the pipeline first.")
        return
    agg_df = pd.read_csv(data_path)

    # Sidebar options for visualization
    st.sidebar.header("Visualization Options")
    courses = sorted(agg_df["course"].unique())
    selected_course = st.sidebar.selectbox("Select a Course", courses)

    mode = st.sidebar.radio(
        "Select Sorting Mode",
        ("numeric", "worst"),
        index=0,
        help="Numeric mode sorts by chapter, section, item; Worst mode sorts by descending no percentage.",
    )

    st.header(f"Feedback for {selected_course} ({mode.capitalize()} Mode)")
    filtered_df = agg_df[agg_df["course"] == selected_course]
    st.dataframe(filtered_df)

    st.subheader("Feedback Chart")
    plot_image = get_plot_image(agg_df, selected_course, mode)
    st.image(plot_image, use_container_width=True)

    st.download_button(
        label="Download Plot as PNG",
        data=plot_image,
        file_name=f"{selected_course.replace(' ', '_')}_{mode}_plot.png",
        mime="image/png",
    )


if __name__ == "__main__":
    main()
