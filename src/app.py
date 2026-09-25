"""Streamlit UI for code-switched spelling normalization (Hindi, Tamil, Malayalam).

Two views: the landing page (homepage_hinglish_workbench.html, rendered as-is) at "/", and the
workbench at "/?page=app". Styled to match the landing page: base colors and fonts come from
.streamlit/config.toml, the rest from the CSS injected below. Always light mode.
"""

import re
from html import escape
from pathlib import Path

import streamlit as st

from normalize import ServerBusyError, normalize, normalize_audio
from prompts import LANGUAGES

st.set_page_config(page_title="Phonetic to Standard Spelling", page_icon="🔤", layout="wide")

HOMEPAGE = Path(__file__).resolve().parent.parent / "homepage_hinglish_workbench.html"
# The homepage's "Show me the app" link, written for opening the file directly in a browser.
HOMEPAGE_APP_LINK = "http://localhost:8501/?page=app"

# Shared by both views: forced light mode and no Streamlit chrome over the design.
BASE_CSS = """
<style>
:root { color-scheme: light; }
[data-testid="stHeader"], [data-testid="stToolbar"] { display: none; }
</style>
"""

# (title, text) pairs for the "Try a sample" bar, typed the messy way people actually text.
SAMPLES = {
    "Hindi": [
        ("A quick plan", "bhai kal milte h, plz tym bta dena"),
        ("Weekend recap", "kal raat ko bohot maza aya yaar"),
        ("Checking in", "kya haal hai, sab thik thak?"),
        ("Running late", "sorry yaar traffic me fas gya, 10 min me pohchta hu"),
    ],
    "Tamil": [
        ("Long day", "inniku office la romba work irunthuchu"),
        ("Sick day", "naan nalaiku office ku varala, fever ah iruku"),
        ("Checking in", "enna panra, saptiya?"),
        ("Running late", "traffic la maatikiten, oru 10 min la varen"),
    ],
    "Malayalam": [
        ("Rough commute", "inn bhayankra traffic aayrunnu machane"),
        ("Lost phone", "ninte phone evide vechu, njan kandilla"),
        ("Checking in", "enthokke und vishesham? sugam alle?"),
        ("Movie plan", "nale movie kaanan pokam, ticket njan book cheyyam"),
    ],
}

CSS = """
<style>
.stApp {
  background-color: #FBF8F3;
  background-image: radial-gradient(#E3D9CC 1px, transparent 1px);
  background-size: 20px 20px;
}
[data-testid="stMainBlockContainer"] { max-width: 1240px; padding-top: 2.5rem; position: relative; z-index: 10; }

/* Decorative Indic glyphs: a fixed layer behind all content, never clickable. */
.glyphs { position: fixed; inset: 0; z-index: 0; pointer-events: none; user-select: none; overflow: hidden; }
.glyph { position: absolute; font-family: 'Lora', serif; line-height: 1; color: #E2D9CD; }
.home-link { display: inline-block; margin-bottom: 1.8rem; font-family: 'IBM Plex Mono', monospace; font-size: .75rem;
  letter-spacing: .15em; text-transform: uppercase; color: #5C564E !important; text-decoration: none !important; }
.home-link:hover { color: #B34418 !important; }

/* Header */
.hdr { display: flex; gap: 1.1rem; align-items: flex-start; position: relative; }
.hdr-mark { font-family: 'Lora', serif; color: #B34418; line-height: 1; text-align: center; padding-top: .3rem; }
.hdr-mark .dev { font-size: 2rem; display: block; }
.hdr-mark .lat { font-size: 1.4rem; opacity: .8; }
.hdr-body { flex: 1; }
.eyebrow { font-family: 'IBM Plex Mono', monospace; font-size: .75rem; font-weight: 600;
  letter-spacing: .2em; text-transform: uppercase; color: #B34418; }
.hdr-title { font-family: 'Lora', serif; font-weight: 700; font-size: clamp(2.6rem, 6vw, 4.6rem);
  line-height: 1.02; letter-spacing: -.02em; color: #1F1C19; margin: .5rem 0 1rem; }
.hdr-title span { color: #B34418; }
.hdr-sub { font-family: 'Lora', serif; font-size: 1.25rem; color: #5C564E; margin: 0; }
.badges { position: absolute; top: 0; right: 0; display: flex; gap: .5rem; }
@media (max-width: 900px) { .badges { display: none; } }
.badge { font-family: 'IBM Plex Mono', monospace; font-size: .7rem; letter-spacing: .15em;
  text-transform: uppercase; color: #5C564E; border: 1px solid #E5DDCF; background: #F4EFE6;
  border-radius: 999px; padding: .4rem .9rem; white-space: nowrap; }
.rule { height: 1px; background: #D9CFC1; margin: 2.2rem 0 2.4rem; position: relative; }
.rule::before { content: ""; position: absolute; left: 0; top: -1px; height: 3px; width: 17%;
  background: #D38D6B; border-radius: 2px; }

/* Main card */
.st-key-card { position: relative; z-index: 10; background: #FCF8F1; border: 1px solid #E5DDCF; border-radius: 14px;
  padding: 3rem 3.2rem 2.6rem; box-shadow: 0 10px 30px -5px rgba(31,28,25,.05), 0 2px 6px -1px rgba(31,28,25,.03); }
.card-title { font-family: 'Lora', serif; font-weight: 700; font-size: 2rem; color: #1F1C19; margin: .5rem 0 .4rem; }

/* Pill toggles (Text / Voice, language) */
[data-testid="stButtonGroup"] { background: #F1E8DA; border-radius: 999px; padding: 5px; width: fit-content; }
[data-testid="stButtonGroup"] button { border: none !important; border-radius: 999px !important;
  background: transparent; font-family: 'Lora', serif; font-size: 1.1rem; color: #5C564E;
  padding: .45rem 1.4rem; min-height: 0; }
[data-testid="stButtonGroup"] button[aria-checked="true"] { background: #B34418 !important; color: #FBF8F3 !important;
  box-shadow: 0 3px 8px rgba(179,68,24,.3); }
[data-testid="stButtonGroup"] button p { font-family: 'Lora', serif; font-size: 1.1rem; }

/* Text input */
.stTextArea textarea { font-family: 'IBM Plex Mono', monospace !important; font-size: 1rem;
  letter-spacing: .04em; background: #FFFDF9; color: #1F1C19; }
[data-testid="stForm"] { border: none; padding: 0; }

/* Keep Normalize first in the form (so Ctrl+Enter triggers it) but show it after the sample bar. */
[data-testid="stLayoutWrapper"]:has(> .st-key-normalize_row) { order: 2; }
[data-testid="stLayoutWrapper"]:has(> .st-key-sample_bar) { order: 1; }
.st-key-sample_bar { background: #F4EDE2; border: 1px solid #E5DDCF; border-radius: 8px; padding: .7rem 1.2rem; }
.st-key-sample_bar .eyebrow { font-size: .68rem; }
.st-key-sample_bar .eyebrow em { font-style: normal; text-transform: none; letter-spacing: .08em; }
.st-key-sample_bar button { background: transparent !important; border: none !important; box-shadow: none !important;
  color: #1F4E5A; padding: .2rem .4rem; min-height: 0; justify-content: flex-start; }
.st-key-sample_bar button p { font-family: 'IBM Plex Mono', monospace; font-size: .95rem; letter-spacing: .04em; }
.st-key-sample_text button p { color: #1F1C19; }
.st-key-sample_text button:hover p { color: #B34418; }
.dots { display: flex; gap: 5px; align-items: center; height: 100%; justify-content: flex-end; padding-top: .9rem; }
.dots i { width: 5px; height: 5px; border-radius: 50%; background: #D8C7B4; }
.dots i.on { width: 8px; height: 8px; background: #B34418; }
.hint { font-family: 'Lora', serif; font-size: 1.1rem; color: #5C564E; margin-top: .7rem; }

/* Primary buttons */
[data-testid^="stBaseButton-primary"] { background: linear-gradient(#C0521F, #A83F14) !important;
  border: none !important; border-bottom: 3px solid #7F2E0C !important; border-radius: 8px;
  box-shadow: 0 6px 14px rgba(179,68,24,.28); padding: .6rem 1.3rem; }
[data-testid^="stBaseButton-primary"] p { font-family: 'Lora', serif; font-size: 1.1rem; color: #FBF8F3; }

/* Output */
.out-empty { font-family: 'Lora', serif; font-size: 1.15rem; color: #6F685F; margin: 2.2rem 0 0; }
.out-card { position: relative; z-index: 10; background: #F4EFE6; border: 1px solid #E5DDCF; border-radius: 12px; padding: 1.3rem 1.6rem; margin-top: 1.6rem; }
.out-card p { font-family: 'IBM Plex Mono', monospace; font-size: 1.2rem; color: #1F1C19; margin: .6rem 0 0; }
.out-card p.native { font-family: 'Lora', serif; font-size: 1.6rem; line-height: 1.6; }
</style>
"""

GLYPHS = """
<div class="glyphs" aria-hidden="true">
<div class="glyph" style="top:20%;right:9%;font-size:5rem;color:#E6C9B6">अ</div>
<div class="glyph" style="top:36%;left:2%;font-size:2.6rem">क</div>
<div class="glyph" style="top:62%;left:1%;font-size:1.8rem;opacity:.8">தமிழ்</div>
<div class="glyph" style="bottom:8%;right:4%;font-size:3rem;color:#EBD3C2">ab</div>
<div class="glyph" style="bottom:4%;left:5%;font-size:1.5rem">മലയാളം</div>
</div>
"""

HEADER = """
<a class="home-link" href="./" target="_self">← Home</a>
<div class="hdr">
  <div class="hdr-mark"><span class="dev">अ</span><span class="lat">ab</span></div>
  <div class="hdr-body">
    <div class="eyebrow">AI / Machine Learning · Language Tools</div>
    <div class="hdr-title">Phonetic<br><span>to Standard Spelling</span></div>
    <p class="hdr-sub">A Hinglish, Tamil and Malayalam workbench for code-switching and spelling by ear.</p>
  </div>
  <div class="badges"><span class="badge">Hindi · Tamil · Malayalam</span><span class="badge">Text + Voice</span></div>
</div>
<div class="rule"></div>
"""


def render_homepage() -> None:
    """Render homepage_hinglish_workbench.html (its <style> and <body>) as the landing view."""
    page = re.sub(r"<!--.*?-->", "", HOMEPAGE.read_text(encoding="utf-8"), flags=re.S)
    style = re.search(r"<style>.*?</style>", page, re.S).group(0)
    body = re.search(r"<body>(.*)</body>", page, re.S).group(1)
    st.markdown(
        BASE_CSS + """<style>
[data-testid="stMainBlockContainer"] { max-width: none; padding: 0; }
</style>""",
        unsafe_allow_html=True,
    )
    st.html(style + body.replace(HOMEPAGE_APP_LINK, "?page=app"))


if st.query_params.get("page") != "app":
    render_homepage()
    st.stop()

st.markdown(BASE_CSS + CSS + GLYPHS + HEADER, unsafe_allow_html=True)

# Set by the "Try again" button (via on_click, so it survives the rerun that button triggers).
retry_requested = st.session_state.pop("retry_requested", False)


def request_retry() -> None:
    st.session_state.retry_requested = True


def step_sample(language: str, step: int) -> None:
    key = f"sample_{language}"
    st.session_state[key] = (st.session_state.get(key, 0) + step) % len(SAMPLES[language])


def use_sample(text: str) -> None:
    st.session_state.text = text


def show_result(result: dict, language: str) -> None:
    script = LANGUAGES[language]["script"]
    st.markdown(
        f"""
<div class="out-card"><div class="eyebrow">Cleaned · English alphabet</div>
<p>{escape(result["cleaned"])}</p></div>
<div class="out-card"><div class="eyebrow">{escape(script)} · {escape(language)}</div>
<p class="native">{escape(result["native"])}</p></div>
""",
        unsafe_allow_html=True,
    )


def run_and_show(fn, *args, language: str) -> None:
    """Call a normalize function, showing retry notices and errors, then render the result."""
    retry_notice = st.empty()

    def show_retry(attempt: int, delay: int, backup: bool) -> None:
        key = "backup key" if backup else "server"
        retry_notice.info(f"{key.capitalize()} busy, retrying in {delay}s... (retry {attempt})")

    def show_fallback() -> None:
        retry_notice.warning("Primary key still busy. Trying backup key...")

    with st.spinner("Normalizing..."):
        try:
            result = fn(*args, language=language, on_retry=show_retry, on_fallback=show_fallback)
        except ServerBusyError as e:
            retry_notice.empty()
            st.error(str(e))
            st.button("Try again", on_click=request_retry)
        except Exception as e:
            retry_notice.empty()
            st.error(f"Something went wrong: {e}")
        else:
            retry_notice.empty()
            show_result(result, language)


card = st.container(key="card")
output = st.container()

with card:
    st.markdown(
        '<div class="eyebrow">Your message</div><div class="card-title">Write it the way you text it.</div>',
        unsafe_allow_html=True,
    )
    toggles = st.columns([1, 2.4], gap="small", vertical_alignment="center")
    with toggles[0]:
        mode = st.segmented_control("Input method", ["Text", "Voice"], default="Text",
                                    key="mode", label_visibility="collapsed") or "Text"
    with toggles[1]:
        language = st.segmented_control("Language", list(LANGUAGES), default="Hindi",
                                        key="language", label_visibility="collapsed") or "Hindi"
    lang = LANGUAGES[language]
    shown = False

    if mode == "Text":
        idx = st.session_state.get(f"sample_{language}", 0)
        title, sample = SAMPLES[language][idx]
        # A form makes Ctrl+Enter (Cmd+Enter on Mac) in the text area submit. Ctrl+Enter fires the
        # form's first submit button, so Normalize is rendered before the sample bar (CSS reorders them).
        with st.form("text_form", border=False):
            text = st.text_area(f"{lang['mix']} input", placeholder=sample, height=90,
                                key="text", label_visibility="collapsed")
            with st.container(key="normalize_row"):
                hint, btn = st.columns([5, 1], vertical_alignment="center")
                hint.markdown('<div class="hint">Spelling by ear is fine. Click a sample to place it in '
                              'the workbench.</div>', unsafe_allow_html=True)
                submitted = btn.form_submit_button("Normalize", type="primary", width="stretch")
            with st.container(key="sample_bar"):
                prev, body, nxt, dots = st.columns([0.35, 8, 0.35, 0.7], vertical_alignment="center")
                prev.form_submit_button("‹", key="sample_prev", on_click=step_sample, args=(language, -1))
                with body:
                    st.markdown(f'<div class="eyebrow">Try a sample · <em>{escape(title)}</em></div>',
                                unsafe_allow_html=True)
                    with st.container(key="sample_text"):
                        st.form_submit_button(sample, key="sample_use", on_click=use_sample, args=(sample,))
                nxt.form_submit_button("›", key="sample_next", on_click=step_sample, args=(language, 1))
                dots.markdown('<div class="dots">' + "".join(
                    f'<i class="{"on" if i == idx else ""}"></i>' for i in range(len(SAMPLES[language]))
                ) + "</div>", unsafe_allow_html=True)
        if submitted or retry_requested:
            with output:
                if not text.strip():
                    st.warning("Enter some text first.")
                else:
                    run_and_show(normalize, text, language=language)
            shown = True
    else:
        audio = st.audio_input(f"Record {language} / English speech")
        st.markdown('<div class="hint">Speak naturally, mixing English in as you like.</div>',
                    unsafe_allow_html=True)
        # Runs on every rerun while a recording exists, so "Try again" re-sends the same audio.
        if audio is not None:
            with output:
                run_and_show(normalize_audio, audio.getvalue(), audio.type or "audio/wav", language=language)
            shown = True

if not shown:
    output.markdown(
        '<p class="out-empty">Your cleaned text and native script rendering will appear here.</p>',
        unsafe_allow_html=True,
    )
