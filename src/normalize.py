"""Core normalization: sends Hinglish text to Gemini and returns cleaned Roman + Devanagari."""

import json
import os
import time
from typing import Callable, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from prompts import NORMALIZE_PROMPT

load_dotenv()

DEFAULT_MODEL = "gemini-3.8-flash"

# Retry schedule for rate-limit / overload errors: wait 5s, 10s, 20s between attempts.
RETRY_DELAYS = [5, 10, 20]
_RETRYABLE_CODES = {429, 503}
_RETRYABLE_STATUSES = {"RESOURCE_EXHAUSTED", "UNAVAILABLE"}

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Copy .env.example to .env and add your key.")
        _client = genai.Client(api_key=api_key)
    return _client


class ServerBusyError(Exception):
    """Gemini kept returning rate-limit / overload errors after all retries."""


def _is_retryable(e: errors.APIError) -> bool:
    return (
        e.code in _RETRYABLE_CODES
        or (e.status or "").upper() in _RETRYABLE_STATUSES
        or "traffic" in (e.message or "").lower()
    )


def _generate(prompt: str, on_retry: Optional[Callable[[int, int], None]]):
    """Call Gemini, retrying on rate-limit / overload errors per RETRY_DELAYS."""
    for attempt, delay in enumerate([*RETRY_DELAYS, None], start=1):
        try:
            return _get_client().models.generate_content(
                model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )
        except errors.APIError as e:
            if not _is_retryable(e):
                raise
            if delay is None:
                raise ServerBusyError(
                    f"Gemini is still busy after {attempt} attempts. Please try again in a minute."
                ) from e
            if on_retry:
                on_retry(attempt, delay)
            time.sleep(delay)


def normalize(text: str, on_retry: Optional[Callable[[int, int], None]] = None) -> dict:
    """Return {"cleaned": str, "devanagari": str} for the given Hinglish text.

    on_retry(attempt, delay_seconds) is called before each wait after a busy error.
    Raises ServerBusyError if every retry fails.
    """
    text = text.strip()
    if not text:
        return {"cleaned": "", "devanagari": ""}

    response = _generate(NORMALIZE_PROMPT.format(text=text), on_retry)

    data = json.loads(response.text)
    return {
        "cleaned": data.get("cleaned", "").strip(),
        "devanagari": data.get("devanagari", "").strip(),
    }
