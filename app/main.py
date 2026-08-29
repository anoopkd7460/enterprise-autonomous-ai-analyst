"""
Streamlit entry point for the Enterprice Autonomous AI Analyst.

Supports:
- Natural-language business questions
- SQL database analysis
- Document/RAG analysis
- CSV/Excel dataset analysis

Run with:

    python -m streamlit run app/main.py
"""

import streamlit as st
import pandas as pd

from app.workflows.graph import answer_question
from app.agents.document_agent import index_document
from app.database.db import seed_sample_data
from app.analytics.profiler import profile_dataset


# ------------------------ Page Configuration ----------------------
st.set_page_config(
    page_title = "Enterprise AI Analyst",
    page_icon = "📊",
    layout="wide",
)


# ----------------------------- Initialize application data ---------------

seed_sample_data()

index_document(
    "data/sample/Q4_2024_Regional_Report.pdf",
    source_name="Q4_2024_Regional_Report",
)


# ------------------------------ Application Header -----------------

st.title("📊 Enterprise Autonomous AI Analyst")

st.caption(
    "Ask business question using SQL data, business documents, "
    "or an uploaded CSV/Excel dataset."
)


# ------------------------------- Dataset Upload ---------------------


st.sidebar.header("📁 Upload Dataset")

# Initialize session state
if "dataframe" not in st.session_state:
    st.session_state.dataframe = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None


with st.sidebar.form("dataset_upload_form"):

    uploaded_file = st.file_uploader(
        "Select a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
    )

    upload_clicked = st.form_submit_button(
        "Upload Dataset",
        type="primary",
        width="stretch",
    )


# Process dataset only after Upload button is clicked

if upload_clicked:

    if uploaded_file is None:

        st.sidebar.warning(
            "Please select a CSV or Excel file first."
        )

    else:

        try:

            file_name = uploaded_file.name.lower()

            if file_name.endswith(".csv"):

                dataframe = pd.read_csv(
                    uploaded_file
                )

            elif file_name.endswith((".xlsx", ".xls")):

                dataframe = pd.read_excel(
                    uploaded_file
                )

            else:

                raise ValueError(
                    "Unsupported file format."
                )

            # Store dataset in session state
            st.session_state.dataframe = dataframe
            st.session_state.uploaded_filename = (
                uploaded_file.name
            )

            st.sidebar.success(
                f"Uploaded {uploaded_file.name}"
            )

        except Exception as e:

            st.session_state.dataframe = None
            st.session_state.uploaded_filename = None

            st.sidebar.error(
                f"Could not load dataset: {e}"
            )


# Retrieve currently uploaded dataset

dataframe = st.session_state.dataframe


# Display dataset information in sidebar

if dataframe is not None:

    profile = profile_dataset(dataframe)

    st.sidebar.success(
        f"Loaded {len(dataframe):,} rows."
    )

    st.sidebar.metric(
        "Rows",
        f"{profile['rows']:,}",
    )

    st.sidebar.metric(
        "Columns",
        f"{profile['columns']:,}",
    )

    st.sidebar.metric(
        "Duplicate Rows",
        f"{profile['duplicate_rows']:,}",
    )


# ------------------------ Dataset Preview ----------------------

if dataframe is not None:

    st.subheader("📋 Uploaded Dataset")

    st.dataframe(dataframe.head(10), width="stretch",)

    with st.expander("Dataset Profile"):
        profile = profile_dataset(dataframe)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Rows", f"{profile['rows']:,}",)
        col2.metric("Columns", f"{profile['columns']:,}",)
        col3.metric("Duplicates", f"{profile['duplicate_rows']:,}",)
        col4.metric("Columns With Missing Columns", len(profile['missing_values']),)

        st.write("### Columns")

        st.write(profile["column_names"])


# --------------------------- Example Questions -------------------

st.write("#### Try a question")

example_questions = [
    "Why did revenue fall in North India in Q4 2024?",
    "Which product sold the most units overall?",
    "What caused the stock shortage in North India?",
]

st.write(
    " . ".join(f"`{question}`" for question in example_questions)
)

# ------------------------------ User question ---------------------

question = st.text_input("Your question", placeholder=("e.g. What are the top 5 products by revenue?"),)


# --------------------------- Execute analysis

if st.button("Ask", type="primary",) and question:
    with st.spinner("Analyzing your question..."):
        try:
            answer = answer_question(question=question, dataframe=dataframe,)
            st.subheader("💡 Answer")
            st.markdown(answer.replace("$", "₹"))

        except Exception as e:
            st.error(f"Something went wrong: {e}")