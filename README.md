# phonetic-to-standard-spelling

People type Hindi-English code-switched text (Hinglish) phonetically, with no consistent spelling: `kaisay ho`, `kese ho`, `bohot`, `bahut`. This Streamlit app takes messy Hinglish, typed or spoken, and returns:

- **Standardized Roman spelling**
- **Devanagari transliteration**

| Input | Cleaned | Devanagari |
|---|---|---|
| kal raat ko bohot maza aya yaar | kal raat ko bahut mazaa aaya yaar | कल रात को बहुत मज़ा आया यार |

It uses the Gemini API.

## Input options

- **Text**: type or paste Hinglish and click **Normalize**.
- **Voice**: record from your mic. The recording goes straight to Gemini as audio (no separate transcription step) and comes back in the same format as text input. Your browser will ask for microphone permission.

Switch between them with the **Input method** toggle at the top of the app.

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

Then open the URL Streamlit prints (usually http://localhost:8501).

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
src/normalize.py  normalize(text) / normalize_audio(bytes) -> {"cleaned", "devanagari"}; calls Gemini
src/prompts.py    prompt templates for text and audio (tune output here)
```
