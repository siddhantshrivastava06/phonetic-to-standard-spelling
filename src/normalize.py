"""Core normalization: sends code-switched text or audio to Gemini and returns cleaned Roman + native script."""

import json
import os
import time
from typing import Callable, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from prompts import DEFAULT_LANGUAGE, LANGUAGES, NORMALIZE_AUDIO_PROMPT, NORMALIZE_PROMPT

load_dotenv()

DEFAULT_MODEL = "gemini-3.5-flash-lite"

# Retry schedule for rate-limit / overload errors: 4 retries after the first call,
# waiting 5s and doubling, capped at 15s -> 5s, 10s, 15s, 15s.
MAX_RETRIES = 4
MAX_DELAY = 15
RETRY_DELAYS = [min(5 * 2**i, MAX_DELAY) for i in range(MAX_RETRIES)]
_RETRYABLE_CODES = {429, 503}
_RETRYABLE_STATUSES = {"RESOURCE_EXHAUSTED", "UNAVAILABLE"}

# on_retry(attempt, delay_seconds, using_backup_key) is called before each wait.
RetryCallback = Callable[[int, int, bool], None]

_clients: dict[str, genai.Client] = {}


def _api_keys() -> list[str]:
    """Primary key (required), then the optional backup key GEMINI_API_KEY_2."""
    primary = os.getenv("GEMINI_API_KEY")
    if not primary:
        raise RuntimeError("GEMINI_API_KEY is not set. Copy .env.example to .env and add your key.")
    backup = os.getenv("GEMINI_API_KEY_2")
    return [primary, backup] if backup else [primary]


def _get_client(api_key: str) -> genai.Client:
    if api_key not in _clients:
        _clients[api_key] = genai.Client(api_key=api_key)
    return _clients[api_key]


class ServerBusyError(Exception):
    """Gemini kept returning rate-limit / overload errors after all retries."""


def _is_retryable(e: errors.APIError) -> bool:
    return (
        e.code in _RETRYABLE_CODES
        or (e.status or "").upper() in _RETRYABLE_STATUSES
        or "traffic" in (e.message or "").lower()
    )


def _generate(
    contents,
    on_retry: Optional[RetryCallback],
    on_fallback: Optional[Callable[[], None]],
):
    """Call Gemini with the primary key; if it stays busy, run the same retries once on the backup key."""
    keys = _api_keys()
    for i, api_key in enumerate(keys):
        backup = i > 0
        if backup and on_fallback:
            on_fallback()
        try:
            return _generate_with_key(api_key, contents, on_retry, backup)
        except ServerBusyError:
            if i == len(keys) - 1:
                raise


def _generate_with_key(api_key: str, contents, on_retry: Optional[RetryCallback], backup: bool):
    """Call Gemini with one key, retrying on rate-limit / overload errors per RETRY_DELAYS."""
    for attempt, delay in enumerate([*RETRY_DELAYS, None], start=1):
        try:
            return _get_client(api_key).models.generate_content(
                model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )
        except errors.APIError as e:
            if not _is_retryable(e):
                raise
            if delay is None:
                which = "on both API keys" if backup else f"after {attempt} attempts"
                raise ServerBusyError(
                    f"Gemini is still busy {which}. Please try again in a minute."
                ) from e
            if on_retry:
                on_retry(attempt, delay, backup)
            time.sleep(delay)


def _language_fields(language: str) -> dict:
    if language not in LANGUAGES:
        raise ValueError(f"Unsupported language {language!r}. Choose one of: {', '.join(LANGUAGES)}.")
    return LANGUAGES[language]


def normalize(
    text: str,
    language: str = DEFAULT_LANGUAGE,
    on_retry: Optional[RetryCallback] = None,
    on_fallback: Optional[Callable[[], None]] = None,
) -> dict:
    """Return {"cleaned": str, "native": str} for the given code-switched text.

    language is a key of prompts.LANGUAGES (e.g. "Hindi", "Tamil"); it picks the native script.

    on_retry(attempt, delay_seconds, using_backup_key) is called before each wait after a busy error.
    on_fallback() is called when the primary key is exhausted and the backup key takes over.
    Raises ServerBusyError if every retry fails (on both keys, when a backup is set).
    """
    fields = _language_fields(language)
    text = text.strip()
    if not text:
        return {"cleaned": "", "native": ""}

    return _parse(_generate(NORMALIZE_PROMPT.format(text=text, **fields), on_retry, on_fallback))


def normalize_audio(
    audio: bytes,
    mime_type: str = "audio/wav",
    language: str = DEFAULT_LANGUAGE,
    on_retry: Optional[RetryCallback] = None,
    on_fallback: Optional[Callable[[], None]] = None,
) -> dict:
    """Same as normalize(), but for recorded speech sent directly to Gemini as audio."""
    fields = _language_fields(language)
    contents = [
        types.Part.from_bytes(data=audio, mime_type=mime_type),
        NORMALIZE_AUDIO_PROMPT.format(**fields),
    ]
    return _parse(_generate(contents, on_retry, on_fallback))


def _parse(response) -> dict:
    data = json.loads(response.text)
    return {
        "cleaned": data.get("cleaned", "").strip(),
        "native": data.get("native", "").strip(),
    }
