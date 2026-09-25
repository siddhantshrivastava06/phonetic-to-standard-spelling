# AGENTS.md

Guide for AI agents and contributors working on this repo.

## What this is

A hackathon MVP: a Streamlit app that normalizes Hinglish (typed phonetically, or spoken into the mic) into standardized Roman spelling and Devanagari, using the Gemini API.

## Structure

- `src/app.py`: Streamlit UI only. No model or prompt logic here. A **Text / Voice** toggle picks the input: `st.text_area` + button, or `st.audio_input` (runs as soon as a recording exists).
- `src/normalize.py`: the only place that calls Gemini.
  - `normalize(text)` and `normalize_audio(audio_bytes, mime_type)` both return `{"cleaned": str, "devanagari": str}`.
  - Audio is sent to Gemini directly as an inline audio part; there is no separate speech-to-text step.
  - Both go through `_generate()`, which retries rate-limit / overload errors (4 retries, waiting 5s, 10s, 15s, 15s; waits are capped at 15s) and raises `ServerBusyError` when they run out. The UI then shows a **Try again** button.
- `src/prompts.py`: `NORMALIZE_PROMPT` (text) and `NORMALIZE_AUDIO_PROMPT` (voice). They share one set of rules (`_RULES`) so both inputs produce the same output. Tune output quality here, not in code.
- `requirements.txt`: runtime dependencies (`streamlit>=1.39` for `st.audio_input`, `google-genai`, `python-dotenv`).
- `.env.example`: config template. The real `.env` is gitignored and must never be committed.

## Conventions

- Keep scope minimal: no auth, database, extra frameworks or extra services.
- Config comes from environment variables (`GEMINI_API_KEY`, optional `GEMINI_MODEL`), loaded from `.env` with `python-dotenv`.
- The model must return JSON of shape `{"cleaned": ..., "devanagari": ...}`. Text and voice must keep returning the same shape. If you change it, update `_RULES`, `normalize.py` and `app.py` together.
- Both prompt templates go through `str.format`, so literal braces must be doubled (`{{` / `}}`).
- Modules in `src/` import each other by bare name (`from prompts import ...`), because Streamlit runs `src/app.py` with `src/` on the path.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY
streamlit run src/app.py
```
