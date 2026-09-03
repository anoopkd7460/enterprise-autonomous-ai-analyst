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
    """
    Extract a section from the analyst response.

    Supports headings such as:

    Key Insight
    Key Insight:
    **Key Insight**
    **Key Insight:**
    """

    next_pattern = "|".join(
        re.escape(section)
        for section in next_sections
    )

    pattern = (
        rf"(?:^|\n)\s*\**{re.escape(section_name)}:?\**\s*\n"
        rf"(.*?)(?=\n\s*\**(?:{next_pattern}):?\**\s*\n|\Z)"
    )

    match = re.search(
        pattern,
        answer,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return ""

    return match.group(1).strip()


def _extract_evidence(answer: str) -> str:
    """Extract the Evidence section."""

    pattern = (
        r"(?:^|\n)\s*\**Evidence:?\**\s*\n"
        r"(.*?)(?=\n\s*\**Recommendation:?\**\s*\n|\Z)"
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
    """Render the analyst response as structured business insights."""

    if not answer:
        st.info("No answer available.")
        return

    st.subheader("🤖 AI Analyst")

    key_insight = _extract_section(
        answer,
        "Key Insight",
        ["Evidence", "Recommendation"],
    )

    evidence = _extract_evidence(answer)

    recommendation = _extract_section(
        answer,
        "Recommendation",
        [],
    )

    # Key Insight

    if key_insight:
        st.markdown("### 💡 Key Insight")

        with st.container(border=True):
            st.markdown(key_insight)

    # Evidence

    if evidence:
        st.markdown("### 📋 Evidence")

        with st.container(border=True):
            st.markdown(evidence)

    # Recommendation

    if recommendation:
        st.markdown("### 🎯 Recommendation")

        with st.container(border=True):
            st.markdown(recommendation)

    # Fallback
    
    if not key_insight and not evidence and not recommendation:
        with st.container(border=True):
            st.markdown(answer)