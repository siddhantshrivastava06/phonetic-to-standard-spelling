"""Prompt template for Hinglish normalization. Edit here to tune model behavior."""

NORMALIZE_PROMPT = """You normalize Hindi-English code-switched text (Hinglish) typed phonetically in Roman script.

People spell Hindi words inconsistently (e.g. "kaisay", "kese", "kaise"; "bohot", "bahut", "bhot").
Your job:
1. "cleaned": rewrite the input in a single standardized Roman spelling.
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

Input: {text}
Output:"""
