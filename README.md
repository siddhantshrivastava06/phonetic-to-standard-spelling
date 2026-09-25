# phonetic-to-standard-spelling

People type Hindi-English code-switched text (Hinglish) phonetically, with no consistent spelling: `kaisay ho`, `kese ho`, `bohot`, `bahut`. This Streamlit app takes messy Hinglish and returns:

- **Standardized Roman spelling**
- **Devanagari transliteration**

| Input | Cleaned | Devanagari |
|---|---|---|
| kal raat ko bohot maza aya yaar | kal raat ko bahut mazaa aaya yaar | कल रात को बहुत मज़ा आया यार |

It uses the Gemini API.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your Gemini API key in .env
```

Get an API key at https://aistudio.google.com/apikey.

## Run

```bash
streamlit run src/app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## Configuration

| Variable | Required | Default |
|---|---|---|
| `GEMINI_API_KEY` | yes | — |
| `GEMINI_MODEL` | no | `gemini-2.5-flash` |

## Project structure

```
src/app.py        Streamlit UI
src/normalize.py  normalize(text) -> {"cleaned", "devanagari"}; calls Gemini
src/prompts.py    prompt template (tune output here)
```
