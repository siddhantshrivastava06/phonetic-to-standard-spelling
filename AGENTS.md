# AGENTS.md

Guide for AI agents and contributors working on this repo.

## What this is

A hackathon MVP: a Streamlit app that normalizes phonetically typed Hinglish into standardized Roman spelling and Devanagari, using the Gemini API.

## Structure

- `src/app.py`: Streamlit UI only. No model or prompt logic here.
- `src/normalize.py`: `normalize(text) -> {"cleaned": str, "devanagari": str}`. The only place that calls Gemini.
- `src/prompts.py`: `NORMALIZE_PROMPT` template. Tune output quality here, not in code.
- `requirements.txt`: runtime dependencies (`streamlit`, `google-genai`, `python-dotenv`).
- `.env.example`: config template. The real `.env` is gitignored and must never be committed.

## Conventions

- Keep scope minimal: no auth, database, extra frameworks or extra services.
- Config comes from environment variables (`GEMINI_API_KEY`, optional `GEMINI_MODEL`), loaded from `.env` with `python-dotenv`.
- The model must return JSON of shape `{"cleaned": ..., "devanagari": ...}`. If you change that shape, update the prompt, `normalize.py` and `app.py` together.
- `prompts.py` uses `str.format`, so literal braces in the template must be doubled (`{{` / `}}`).
- Modules in `src/` import each other by bare name (`from prompts import ...`), because Streamlit runs `src/app.py` with `src/` on the path.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY
streamlit run src/app.py
```
