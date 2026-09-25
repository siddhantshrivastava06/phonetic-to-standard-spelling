"""Streamlit UI for Hinglish spelling normalization."""

import streamlit as st

from normalize import normalize

st.set_page_config(page_title="Phonetic to Standard Spelling", page_icon="🔤")

st.title("Phonetic to Standard Spelling")
st.caption("Paste messy Hinglish and get standardized Roman spelling plus Devanagari.")

text = st.text_area("Hinglish input", placeholder="kal raat ko bohot maza aya yaar", height=120)

if st.button("Normalize", type="primary"):
    if not text.strip():
        st.warning("Enter some text first.")
    else:
        with st.spinner("Normalizing..."):
            try:
                result = normalize(text)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
            else:
                st.subheader("Cleaned (Roman)")
                st.code(result["cleaned"], language=None)
                st.subheader("Devanagari")
                st.code(result["devanagari"], language=None)
