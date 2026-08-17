"""
Phase 1 entry point: a Streamlit app where a business user asks a question
in plain English and the SQL Agent answers it.

Run with:
    streamlit run app/main.py
"""
import streamlit as st

from app.agents.sql_agent import answer_question
from app.database.db import seed_sample_data

st.set_page_config(page_title="Enterprise AI Analyst", page_icon="📊", layout="wide")

seed_sample_data()

st.title("📊 Enterprise Autonomous AI Analyst")
st.caption("Ask a business question about sales — the agent writes the SQL, "
           "runs it, and explains the answer.")

example_questions = [
    "Why did revenue fall in North India in Q4 2024?",
    "Which product sold the most units overall?",
    "Compare total revenue by region",
]
st.write("Try:", " · ".join(f"`{q}`" for q in example_questions))

question = st.text_input("Your question", placeholder="e.g. Why did revenue fall in North India last quarter?")

if st.button("Ask", type="primary") and question:
    with st.spinner("Thinking..."):
        try:
            result = answer_question(question)

            st.subheader("Answer")
            st.markdown(result.explanation.replace("$","₹"), unsafe_allow_html=False)

            with st.expander("Show data"):
                st.dataframe(result.data)

            with st.expander("Show generated SQL"):
                st.code(result.sql_query, language="sql")

        except Exception as e:
            st.error(f"Something went wrong: {e}")