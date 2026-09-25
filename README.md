# phonetic-to-standard-spelling

People type code-switched text (a local language mixed with English) phonetically, with no consistent spelling: `kaisay ho`, `kese ho`, `bohot`, `bahut`. This Streamlit app takes that messy text, typed or spoken, and returns:

- **Standardized Roman spelling**
- **Native-script transliteration**

Supported languages:

| Language | Typed form | Native script | Example input | Cleaned | Native script |
|---|---|---|---|---|---|
| Hindi | Hinglish | Devanagari | kal raat ko bohot maza aya yaar | kal raat ko bahut mazaa aaya yaar | कल रात को बहुत मज़ा आया यार |
| Tamil | Tanglish | Tamil | inniku office la romba work irunthuchu | innikku office la romba work irundhuchu | இன்னிக்கு ஆஃபீஸ்ல ரொம்ப வொர்க் இருந்துச்சு |
| Malayalam | Manglish | Malayalam | inn bhayankra traffic aayrunnu machane | innu bhayankara traffic aayirunnu machane | ഇന്ന് ഭയങ്കര ട്രാഫിക് ആയിരുന്നു മച്ചാനേ |

It uses the Gemini API.

## Input options

Pick the language (Hindi, Tamil or Malayalam) and the input method with the pill toggles at the top of the card:

- **Text**: type or paste text and click **Normalize** (or press Ctrl+Enter). Or click a line in the **Try a sample** bar to fill it in.
- **Voice**: record from your mic. The recording goes straight to Gemini as audio (no separate transcription step) and comes back in the same format as text input. Your browser will ask for microphone permission.


To add a language, add an entry to `LANGUAGES` in `src/prompts.py`; the UI picks it up automatically.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your Gemini API key in .env
```

## Run

```bash
streamlit run src/app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501). It opens on the landing page (`homepage_hinglish_workbench.html`); **Show me the app** takes you to the workbench at `/?page=app`, and **← Home** brings you back.

## Configuration

| Variable | Required | Default |
|---|---|---|
| `GEMINI_API_KEY` | yes | — |
| `GEMINI_API_KEY_2` | no | — (backup key; see below) |
| `GEMINI_MODEL` | no | `gemini-3.5-flash-lite` |

If Gemini is busy (rate limited or overloaded), the app retries 4 times, waiting 5s, 10s, 15s and 15s. If it's still busy and `GEMINI_API_KEY_2` is set, it runs the same retries once more with that key, showing "Trying backup key..." in the UI. If everything fails, a **Try again** button lets you resubmit.

## Project structure

```
src/app.py        Streamlit UI (text or voice input)
src/normalize.py  normalize(text, language) / normalize_audio(bytes, mime, language) -> {"cleaned", "native"}; calls Gemini
src/prompts.py    LANGUAGES settings + shared prompt templates for text and audio (tune output here)
.streamlit/config.toml            theme colors and fonts for the app
homepage_hinglish_workbench.html  landing page, served by the app at /
```
