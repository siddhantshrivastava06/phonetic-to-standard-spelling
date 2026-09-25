# AGENTS.md

Guide for AI agents and contributors working on this repo.

## What this is

A hackathon MVP: a Streamlit app that normalizes code-switched text in Hindi, Tamil or Malayalam mixed with English (typed phonetically, or spoken into the mic) into standardized Roman spelling and the native script (Devanagari, Tamil, Malayalam), using the Gemini API.

## Structure

- `src/app.py`: Streamlit UI only. No model or prompt logic here. Pill toggles (`st.segmented_control`) pick **Text / Voice** and the language (built from `prompts.LANGUAGES`). Text mode is a form: `st.text_area`, a **Normalize** button and a "Try a sample" bar (`SAMPLES`); voice mode is `st.audio_input`, which runs as soon as a recording exists. Results render below the card.
  - Styling: `.streamlit/config.toml` sets the theme colors and fonts; `app.py` injects the rest as CSS (`st.markdown(..., unsafe_allow_html=True)`), targeting `st.container(key=...)` classes (`.st-key-<key>`). The design follows `homepage_hinglish_workbench.html`.
  - Ctrl+Enter submits a form via its *first* submit button, so Normalize is rendered before the sample bar and CSS `order` shows it after. Keep that order if you touch the form.
- `src/normalize.py`: the only place that calls Gemini.
  - `normalize(text, language)` and `normalize_audio(audio_bytes, mime_type, language)` both return `{"cleaned": str, "native": str}`. `language` is a `LANGUAGES` key (default `"Hindi"`); unknown values raise `ValueError`. Language only changes the prompt: every language shares `_generate()` and the retry logic.
  - Audio is sent to Gemini directly as an inline audio part; there is no separate speech-to-text step.
  - Both go through `_generate()`, which retries rate-limit / overload errors (4 retries, waiting 5s, 10s, 15s, 15s; waits are capped at 15s) If the primary key is still busy and `GEMINI_API_KEY_2` is set, it runs the whole retry sequence once more with that key (`on_fallback` fires so the UI can say so). `ServerBusyError` is raised only when every key is exhausted. The UI then shows a **Try again** button.
- `src/prompts.py`: `LANGUAGES` (per-language settings: script name, spelling rules, example), `NORMALIZE_PROMPT` (text) and `NORMALIZE_AUDIO_PROMPT` (voice). Both templates share one set of rules (`_RULES`), parameterized by a `LANGUAGES` entry, so every language and input type produces the same output shape. To add a language, add a `LANGUAGES` entry with all the same keys. Tune output quality here, not in code.
- `homepage_hinglish_workbench.html`: the landing page. `app.py` serves it at `/` by reading the file and rendering its style block and body with `st.html`; the workbench lives at `/?page=app`. Because `st.html` runs no JavaScript and strips inline SVG, keep this file plain HTML + CSS (no scripts, no Tailwind CDN, no SVG). Its CTA points at `http://localhost:8501/?page=app` so the file also works opened directly; `app.py` rewrites that to `?page=app`.
- `requirements.txt`: runtime dependencies (`streamlit>=1.39` for `st.audio_input`, `google-genai`, `python-dotenv`).
- `.env.example`: config template. The real `.env` is gitignored and must never be committed.

## Conventions

- Light mode only: no dark theme, dark-mode toggle or `prefers-color-scheme: dark` rules. The Streamlit header/toolbar (which holds the theme switcher) is hidden.
- Keep scope minimal: no auth, database, extra frameworks or extra services.
- Config comes from environment variables (`GEMINI_API_KEY`, optional `GEMINI_API_KEY_2` backup key, optional `GEMINI_MODEL` defaulting to `gemini-3.5-flash-lite`), loaded from `.env` with `python-dotenv`.
- The model must return JSON of shape `{"cleaned": ..., "native": ...}` for every language. Text and voice must keep returning the same shape. If you change it, update `_RULES`, `normalize.py` and `app.py` together.
- Both prompt templates go through `str.format` with a `LANGUAGES` entry's fields, so literal braces in the templates must be doubled (`{{` / `}}`). Values inside `LANGUAGES` are substituted verbatim and use single braces.
- Modules in `src/` import each other by bare name (`from prompts import ...`), because Streamlit runs `src/app.py` with `src/` on the path.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY
streamlit run src/app.py
```
