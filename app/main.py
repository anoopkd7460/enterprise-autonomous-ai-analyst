"""
Phase 1 entry point: a Streamlit app where a business user asks a question
in plain English and the Planner Agent routes it to the SQL Agent, the Document
Agent, or both - then returns one combined Answer.

Run with:
    python -m streamlit run app/main.py
"""
import streamlit as st

from app.workflows.graph import answer_question
from app.agents.document_agent import index_document
from app.database.db import seed_sample_data

st.set_page_config(page_title="Enterprise AI Analyst", page_icon="📊", layout="wide")

seed_sample_data()
index_document("data/sample/Q4_2024_Regional_Report.pdf", source_name="Q4_2024_Regional_Report")

st.title("📊 Enterprise Autonomous AI Analyst")
st.caption("Ask a business question — the agent pulls data, reads reports, "
           "and explains the answer.")

example_questions = [
    "Why did revenue fall in North India in Q4 2024?",
    "Which product sold the most units overall?",
    "What caused the stock shortage in North India?",
]
st.write("Try:", " · ".join(f"`{q}`" for q in example_questions))

question = st.text_input("Your question", placeholder="e.g. Why did revenue fall in North India last quarter?")

if st.button("Ask", type="primary") and question:
    with st.spinner("Thinking..."):
        try:
            answer = answer_question(question)
            st.subheader("Answer")
            st.markdown(answer.replace("$", "₹"))
        except Exception as e:
            st.error(f"Something went wrong: {e}")