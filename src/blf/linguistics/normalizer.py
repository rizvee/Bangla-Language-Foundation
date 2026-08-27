"""
Bengali Unicode Normalization and Character Validation Utilities.
"""

import re
import unicodedata

# Unicode Range for Bengali: U+0980 to U+09FF
BENGALI_UNICODE_RANGE = (0x0980, 0x09FF)

# Zero-width joiner & non-joiner
ZWJ = "\u200D"
ZWNJ = "\u200C"

# Common character mappings for normalization (e.g. Dari / Full Stop normalization)
CHAR_REPLACEMENTS = {
    "\u0964": "\u0964",  # Bengali Dari (Devanagari Danda mapped to standard Dari)
    "\u0965": "\u0965",  # Double Danda
    "\u00A0": " ",       # Non-breaking space
    "\u2018": "'",       # Left single quote
    "\u2019": "'",       # Right single quote
    "\u201C": '"',       # Left double quote
    "\u201D": '"',       # Right double quote
}

# Regex to collapse multiple whitespace
WHITESPACE_REGEX = re.compile(r"[ \t\r\f\v]+")
MULTIPLE_NEWLINES_REGEX = re.compile(r"\n{3,}")


def normalize_bangla_text(text: str, preserve_newlines: bool = True) -> str:
    """
    Normalizes Bengali text to standard Unicode NFC form, replaces irregular punctuation,
    and strips spurious whitespace while preserving valid diacritics and hasant ligatures.
    """
    if not text:
        return ""

    # Step 1: Unicode NFC Normalization
    normalized = unicodedata.normalize("NFC", text)

    # Step 2: Apply char replacements
    for bad_char, good_char in CHAR_REPLACEMENTS.items():
        normalized = normalized.replace(bad_char, good_char)

    # Step 3: Whitespace normalization
    if preserve_newlines:
        lines = [WHITESPACE_REGEX.sub(" ", line).strip() for line in normalized.split("\n")]
        normalized = "\n".join(lines)
        normalized = MULTIPLE_NEWLINES_REGEX.sub("\n\n", normalized).strip()
    else:
        normalized = WHITESPACE_REGEX.sub(" ", normalized).strip()

    return normalized


def contains_bengali_characters(text: str) -> bool:
    """
    Checks if the given string contains at least one Bengali Unicode code point (U+0980 - U+09FF).
    """
    return any(BENGALI_UNICODE_RANGE[0] <= ord(char) <= BENGALI_UNICODE_RANGE[1] for char in text)


def get_bengali_character_ratio(text: str) -> float:
    """
    Computes the proportion of characters belonging to the Bengali Unicode block (ignoring whitespace).
    """
    non_ws = [c for c in text if not c.isspace()]
    if not non_ws:
        return 0.0
    bengali_count = sum(1 for c in non_ws if BENGALI_UNICODE_RANGE[0] <= ord(c) <= BENGALI_UNICODE_RANGE[1])
    return bengali_count / len(non_ws)
