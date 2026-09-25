"""Streamlit UI for Hinglish spelling normalization."""

import streamlit as st

from normalize import ServerBusyError, normalize, normalize_audio

st.set_page_config(page_title="Phonetic to Standard Spelling", page_icon="🔤")

st.title("Phonetic to Standard Spelling")
st.caption("Type or speak messy Hinglish and get standardized Roman spelling plus Devanagari.")


def run_and_show(fn, *args) -> None:
    """Call a normalize function, showing retry notices and errors, then render the result."""
    retry_notice = st.empty()

    def show_retry(attempt: int, delay: int) -> None:
        retry_notice.info(f"Server busy, retrying in {delay}s... (retry {attempt})")

    with st.spinner("Normalizing..."):
        try:
            result = fn(*args, on_retry=show_retry)
        except ServerBusyError as e:
            retry_notice.empty()
            st.error(str(e))
        except Exception as e:
            retry_notice.empty()
            st.error(f"Something went wrong: {e}")
        else:
            retry_notice.empty()
            st.subheader("Cleaned (Roman)")
            st.code(result["cleaned"], language=None)
            st.subheader("Devanagari")
            st.code(result["devanagari"], language=None)


mode = st.radio("Input method", ["Text", "Voice"], horizontal=True)

if mode == "Text":
    text = st.text_area("Hinglish input", placeholder="kal raat ko bohot maza aya yaar", height=120)
    if st.button("Normalize", type="primary"):
        if not text.strip():
            st.warning("Enter some text first.")
        else:
            run_and_show(normalize, text)
else:
    audio = st.audio_input("Record Hinglish speech")
    if audio is not None:
        run_and_show(normalize_audio, audio.getvalue(), audio.type or "audio/wav")
