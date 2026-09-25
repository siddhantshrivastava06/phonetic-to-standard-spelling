"""Prompt templates for Hinglish normalization. Edit here to tune model behavior.

Both templates go through str.format, so literal braces must be doubled ({{ }}).
"""

_TEXT_INTRO = """You normalize Hindi-English code-switched text (Hinglish) typed phonetically in Roman script.

People spell Hindi words inconsistently (e.g. "kaisay", "kese", "kaise"; "bohot", "bahut", "bhot")."""

_AUDIO_INTRO = """You normalize spoken Hindi-English code-switched speech (Hinglish).

The attached audio is someone speaking Hinglish. Write down exactly what they say, word for word."""

# Shared by the text and audio flows so both return the same output.
_RULES = """
Your job:
1. "cleaned": write the input in a single standardized Roman spelling.
   - Use the most common, readable spelling for each Hindi word (e.g. "bahut", "kaise", "mazaa", "aaya").
   - Leave English words in normal English spelling.
   - Keep word order and meaning exactly the same. Do not translate, add, or remove words.
   - Keep the original casing style and punctuation.
2. "devanagari": transliterate the whole sentence into Devanagari script.
   - Hindi words in standard Hindi spelling (use nukta where standard, e.g. मज़ा).
   - English words transliterated phonetically into Devanagari (e.g. "phone" -> फ़ोन).

Respond with JSON only, in this exact shape:
{{"cleaned": "<standardized Roman text>", "devanagari": "<Devanagari text>"}}

Example:
Input: kal raat ko bohot maza aya yaar
Output: {{"cleaned": "kal raat ko bahut mazaa aaya yaar", "devanagari": "कल रात को बहुत मज़ा आया यार"}}
"""

NORMALIZE_PROMPT = _TEXT_INTRO + "\n" + _RULES + """
Input: {text}
Output:"""

NORMALIZE_AUDIO_PROMPT = _AUDIO_INTRO + "\n" + _RULES + """
Input: the attached audio
Output:"""
