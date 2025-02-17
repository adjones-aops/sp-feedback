# streamlit_app/app.py

import os
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.visualization import plot_stacked_bar  # reuse our visualization function


# Helper function to generate and return plot as image bytes.
def get_plot_image(agg_df, course, mode):
    # Create a BytesIO buffer to save the plot image.
    buf = BytesIO()
    # Generate the plot into the buffer.
    plot_stacked_bar(agg_df, course, output_filename=None, mode=mode)
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()  # close the figure after saving to buffer
    buf.seek(0)
    return buf


def main():
    st.title("Self-Paced Feedback Visualization")

    # Load aggregated data
    data_path = os.path.join("data", "aggregated_feedback.csv")
    if not os.path.exists(data_path):
        st.error(f"Aggregated data not found at {data_path}. Please run the data processor first.")
        return
    agg_df = pd.read_csv(data_path)

    # Sidebar for user inputs
    st.sidebar.header("Visualization Options")

    # Dropdown for course selection
    courses = sorted(agg_df["course"].unique())
    selected_course = st.sidebar.selectbox("Select a Course", courses)

    # Visualization mode options
    mode = st.sidebar.radio(
        "Select Sorting Mode",
        ("numeric", "worst"),
        index=0,
        help="Numeric mode sorts by chapter, section, item; Worst mode sorts by descending no percentage.",
    )

    # Optionally, you could also have a mode for chapter-level aggregation.

    st.header(f"Feedback for {selected_course} ({mode.capitalize()} Mode)")

    # Display aggregated data table (filtered by course)
    filtered_df = agg_df[agg_df["course"] == selected_course]
    st.dataframe(filtered_df)

    # Generate and display the plot
    st.subheader("Feedback Chart")
    # Here we capture the plot image bytes from our helper function
    plot_image = get_plot_image(agg_df, selected_course, mode)
    st.image(plot_image, use_container_width=True)

    # Optionally, provide a download button for the plot image
    st.download_button(
        label="Download Plot as PNG",
        data=plot_image,
        file_name=f"{selected_course.replace(' ', '_')}_{mode}_plot.png",
        mime="image/png",
    )


if __name__ == "__main__":
    main()
