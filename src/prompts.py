"""Prompt templates for code-switched text normalization. Edit here to tune model behavior.

Both templates go through str.format with one LANGUAGES entry (plus `text` for the text
prompt), so literal braces must be doubled ({{ }}). Values substituted in are not re-parsed,
so LANGUAGES entries use single braces.
"""

# Per-language settings substituted into the shared templates. Keys are the names shown in the UI.
LANGUAGES = {
    "Hindi": {
        "language": "Hindi",
        "mix": "Hinglish",
        "script": "Devanagari",
        "variants": '"kaisay", "kese", "kaise"; "bohot", "bahut", "bhot"',
        "roman_rule": 'Use the most common, readable spelling for each Hindi word (e.g. "bahut", "kaise", "mazaa", "aaya").',
        "native_rule": "Hindi words in standard Hindi spelling (use nukta where standard, e.g. मज़ा).",
        "phone": "फ़ोन",
        "example_input": "kal raat ko bohot maza aya yaar",
        "example_cleaned": "kal raat ko bahut mazaa aaya yaar",
        "example_native": "कल रात को बहुत मज़ा आया यार",
    },
    "Tamil": {
        "language": "Tamil",
        "mix": "Tanglish",
        "script": "Tamil script",
        "variants": '"romba", "rombha", "roamba"; "enna", "ena", "yenna"',
        "roman_rule": 'Use the most common, readable spelling for each Tamil word (e.g. "romba", "enna", "innikku", "irundhuchu").',
        "native_rule": "Tamil words in standard Tamil spelling, keeping the colloquial form that was used (e.g. இருந்துச்சு, not இருந்தது).",
        "phone": "ஃபோன்",
        "example_input": "inniku office la romba work irunthuchu",
        "example_cleaned": "innikku office la romba work irundhuchu",
        "example_native": "இன்னிக்கு ஆஃபீஸ்ல ரொம்ப வொர்க் இருந்துச்சு",
    },
    "Malayalam": {
        "language": "Malayalam",
        "mix": "Manglish",
        "script": "Malayalam script",
        "variants": '"enthanu", "entha", "enthaanu"; "aayirunnu", "ayrunnu", "aayrnu"',
        "roman_rule": 'Use the most common, readable spelling for each Malayalam word (e.g. "enthaanu", "aayirunnu", "bhayankara", "machane").',
        "native_rule": "Malayalam words in standard Malayalam spelling (use chillu letters where standard, e.g. അവൻ).",
        "phone": "ഫോൺ",
        "example_input": "inn bhayankra traffic aayrunnu machane",
        "example_cleaned": "innu bhayankara traffic aayirunnu machane",
        "example_native": "ഇന്ന് ഭയങ്കര ട്രാഫിക് ആയിരുന്നു മച്ചാനേ",
    },
}

DEFAULT_LANGUAGE = "Hindi"

_TEXT_INTRO = """You normalize {language}-English code-switched text ({mix}) typed phonetically in Roman script.

People spell {language} words inconsistently (e.g. {variants})."""

_AUDIO_INTRO = """You normalize spoken {language}-English code-switched speech.

The attached audio is someone speaking {language}, possibly mixed with English. Write down exactly what they say, word for word."""

# Shared by the text and audio flows and by every language, so all return the same output.
_RULES = """
Your job:
1. "cleaned": write the input in a single standardized Roman spelling.
   - {roman_rule}
   - Leave English words in normal English spelling.
   - Keep word order and meaning exactly the same. Do not translate, add, or remove words.
   - Keep the original casing style and punctuation.
2. "native": transliterate the whole sentence into {script}.
   - {native_rule}
   - English words transliterated phonetically into {script} (e.g. "phone" -> {phone}).

Respond with JSON only, in this exact shape:
{{"cleaned": "<standardized Roman text>", "native": "<{script} text>"}}

Example:
Input: {example_input}
Output: {{"cleaned": "{example_cleaned}", "native": "{example_native}"}}
"""

NORMALIZE_PROMPT = _TEXT_INTRO + "\n" + _RULES + """
Input: {text}
Output:"""

NORMALIZE_AUDIO_PROMPT = _AUDIO_INTRO + "\n" + _RULES + """
Input: the attached audio
Output:"""
