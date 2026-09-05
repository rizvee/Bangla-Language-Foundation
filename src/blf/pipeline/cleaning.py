"""
BLF Conservative Text Cleaning Engine.

Strips control codes and non-printable noise while rigorously preserving
all Bengali diacritics, signs, and phonetic modifiers.
"""

from dataclasses import dataclass, field
import re
from typing import Dict, List, Set, Tuple


@dataclass
class CleaningMetrics:
    original_length: int
    cleaned_length: int
    bengali_char_count: int
    bengali_ratio: float
    removed_control_chars_count: int
    removed_characters: List[str] = field(default_factory=list)


class ConservativeTextCleaner:
    """
    Conservative cleaner that guarantees zero data loss on valid Bengali diacritics
    while eliminating terminal/corrupted control codes and illegal unicode sequences.
    """

    # Bengali Unicode Block: U+0980 - U+09FF
    BENGALI_RANGE = (0x0980, 0x09FF)

    # Allowed control codes: \t (9), \n (10)
    ALLOWED_CONTROLS = {9, 10}

    def __init__(self, preserve_ascii_punctuation: bool = True) -> None:
        self.preserve_ascii_punct = preserve_ascii_punctuation

    def is_bengali(self, ch: str) -> bool:
        return self.BENGALI_RANGE[0] <= ord(ch) <= self.BENGALI_RANGE[1]

    def clean(self, text: str) -> Tuple[str, CleaningMetrics]:
        if not text:
            return "", CleaningMetrics(0, 0, 0, 0.0, 0, [])

        original_len = len(text)
        cleaned_chars: List[str] = []
        removed_chars: List[str] = []
        bengali_count = 0

        for ch in text:
            cp = ord(ch)

            # Check for non-printable control characters
            if (cp < 32 and cp not in self.ALLOWED_CONTROLS) or cp == 127:
                removed_chars.append(ch)
                continue

            # Check for Unicode Bidirectional embedding controls (e.g. U+202A to U+202E)
            if 0x202A <= cp <= 0x202E or 0x2066 <= cp <= 0x2069:
                removed_chars.append(ch)
                continue

            if self.is_bengali(ch):
                bengali_count += 1

            cleaned_chars.append(ch)

        cleaned_text = "".join(cleaned_chars)
        cleaned_len = len(cleaned_text)
        bengali_ratio = (bengali_count / cleaned_len) if cleaned_len > 0 else 0.0

        metrics = CleaningMetrics(
            original_length=original_len,
            cleaned_length=cleaned_len,
            bengali_char_count=bengali_count,
            bengali_ratio=bengali_ratio,
            removed_control_chars_count=len(removed_chars),
            removed_characters=removed_chars,
        )

        return cleaned_text, metrics
