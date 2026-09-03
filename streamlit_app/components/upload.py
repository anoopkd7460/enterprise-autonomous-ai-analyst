"""
Dataset upload component for the Streamlit application.
"""

import streamlit as st


def render_upload():
    """
    Render the dataset uploader.

    Returns
    -------
    UploadedFile | None
        Uploaded CSV or Excel file.
    """

    st.subheader("📂 Dataset")

    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel dataset",
        type=["csv", "xlsx", "xls"],
        help="Upload a dataset for the AI Analyst to analyze.",
    )

    if uploaded_file is not None:
        st.success(
            f"Loaded: {uploaded_file.name}"
        )

        file_size_mb = uploaded_file.size / (1024 * 1024)

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "File",
                uploaded_file.name,
            )

        with col2:
            st.metric(
                "Size",
                f"{file_size_mb:.2f} MB",
            )
            
    return uploaded_file