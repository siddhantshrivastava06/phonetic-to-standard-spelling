"""Core normalization: sends Hinglish text to Gemini and returns cleaned Roman + Devanagari."""

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import NORMALIZE_PROMPT

load_dotenv()

DEFAULT_MODEL = "gemini-2.5-flash"

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Copy .env.example to .env and add your key.")
        _client = genai.Client(api_key=api_key)
    return _client


def normalize(text: str) -> dict:
    """Return {"cleaned": str, "devanagari": str} for the given Hinglish text."""
    text = text.strip()
    if not text:
        return {"cleaned": "", "devanagari": ""}

    response = _get_client().models.generate_content(
        model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        contents=NORMALIZE_PROMPT.format(text=text),
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )

    data = json.loads(response.text)
    return {
        "cleaned": data.get("cleaned", "").strip(),
        "devanagari": data.get("devanagari", "").strip(),
    }
