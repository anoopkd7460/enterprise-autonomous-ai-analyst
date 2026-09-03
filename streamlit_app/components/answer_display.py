"""
Structured AI Analyst result display component.
"""

import re

import streamlit as st


def _extract_section(
    answer: str,
    section_name: str,
    next_sections: list[str],
) -> str:
    """Extract a named section from the analyst response."""

    if next_sections:
        next_pattern = "|".join(
            re.escape(section)
            for section in next_sections
        )

        end_pattern = (
            rf"(?=\n\s*\**(?:{next_pattern}):?\**\s*\n|\Z)"
        )
    else:
        end_pattern = r"(?=\Z)"

    pattern = (
        rf"(?:^|\n)\s*\**{re.escape(section_name)}:?\**\s*\n"
        rf"(.*?){end_pattern}"
    )

    match = re.search(
        pattern,
        answer,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return ""

    return match.group(1).strip()


def render_answer(answer: str | None) -> None:
    """Render the structured AI analyst response."""

    if not answer:
        st.info("No answer available.")
        return

    st.subheader("🤖 AI Analyst")

    key_insight = _extract_section(
        answer,
        "Key Insight",
        ["Evidence", "Recommendation"],
    )

    evidence = _extract_section(
        answer,
        "Evidence",
        ["Recommendation"],
    )

    answer_section = _extract_section(
        answer,
        "Answer",
        ["Recommendation"],
    )

    recommendation = _extract_section(
        answer,
        "Recommendation",
        [],
    )

    if key_insight:
        st.markdown("### 💡 Key Insight")

        with st.container(border=True):
            st.markdown(key_insight)

    if evidence:
        st.markdown("### 📋 Evidence")

        with st.container(border=True):
            st.markdown(evidence)

    if answer_section:
        st.markdown("### 📊 Analysis Result")

        with st.container(border=True):
            st.markdown(answer_section)

    if recommendation:
        st.markdown("### 🎯 Recommendation")

        with st.container(border=True):
            st.markdown(recommendation)

    if (
        not key_insight
        and not evidence
        and not answer_section
        and not recommendation
    ):
        st.markdown("### 🤖 Analyst Response")

        with st.container(border=True):
            st.markdown(answer)