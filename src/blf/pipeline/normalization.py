"""
BLF Reversible Unicode & Punctuation Normalization Engine.

Applies standardized Bengali text normalization while tracking detailed
transformation provenance to allow inspection and deterministic reversal.
"""

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Tuple
import unicodedata


class NormalizationRule(str, Enum):
    UNICODE_NFC = "UNICODE_NFC"
    PUNCTUATION_DARI = "PUNCTUATION_DARI"
    PUNCTUATION_QUOTES = "PUNCTUATION_QUOTES"
    WHITESPACE_COLLAPSE = "WHITESPACE_COLLAPSE"
    ZWJ_ZWNJ_POLICY = "ZWJ_ZWNJ_POLICY"


@dataclass
class TransformationStep:
    rule: NormalizationRule
    original_segment: str
    transformed_segment: str
    position: int
    notes: Optional[str] = None


class ReversibleNormalizer:
    """
    Normalizes Bengali text while maintaining an audit trail of changes.
    """

    # Bengali Dari: U+0964 (standard danda). Devanagari danda is also U+0964.
    # Western period used as Dari: '.' -> '।' (only when ending a Bengali sentence)
    BENGALI_HASANTA = "\u09CD"
    ZWJ = "\u200D"
    ZWNJ = "\u200C"

    def __init__(self, normalize_terminal_period_to_dari: bool = False) -> None:
        self.normalize_terminal_period = normalize_terminal_period_to_dari

    def normalize(self, text: str) -> Tuple[str, List[TransformationStep]]:
        """
        Runs pipeline steps on text, returning (normalized_text, transformation_steps).
        """
        if not text:
            return "", []

        steps: List[TransformationStep] = []
        current = text

        # 1. Unicode NFC Normalization
        nfc_text = unicodedata.normalize("NFC", current)
        if nfc_text != current:
            steps.append(
                TransformationStep(
                    rule=NormalizationRule.UNICODE_NFC,
                    original_segment=current,
                    transformed_segment=nfc_text,
                    position=0,
                    notes=f"Unicode normalized from form {unicodedata.name(current[0]) if current else ''} to NFC",
                )
            )
            current = nfc_text

        # 2. ZWJ / ZWNJ Policy
        # Valid Bangla ZWJ usage: preceded by Hasanta (e.g. \u09cd\u200d for subjoined consonants or ya-phala)
        # Invalid ZWJ/ZWNJ: isolated between non-Bengali characters or consecutive ZWJ/ZWNJ
        cleaned_chars = []
        n = len(current)
        i = 0
        zwj_steps_taken = False
        while i < n:
            ch = current[i]
            if ch in (self.ZWJ, self.ZWNJ):
                # Check preceding character
                has_valid_preceding = i > 0 and current[i - 1] == self.BENGALI_HASANTA
                if has_valid_preceding:
                    # Legitimate ligature controller in Indic typography
                    cleaned_chars.append(ch)
                else:
                    # Spurious ZWJ/ZWNJ, strip it
                    zwj_steps_taken = True
            else:
                cleaned_chars.append(ch)
            i += 1

        zwj_processed = "".join(cleaned_chars)
        if zwj_processed != current:
            steps.append(
                TransformationStep(
                    rule=NormalizationRule.ZWJ_ZWNJ_POLICY,
                    original_segment=current,
                    transformed_segment=zwj_processed,
                    position=0,
                    notes="Stripped spurious/isolated ZWJ/ZWNJ characters outside hasanta contexts",
                )
            )
            current = zwj_processed

        # 3. Punctuation & Quotes Normalization
        quote_replacements = {
            "\u2018": "'",
            "\u2019": "'",
            "\u201C": '"',
            "\u201D": '"',
            "\u00AB": '"',
            "\u00BB": '"',
        }
        quote_processed = current
        for bad_q, good_q in quote_replacements.items():
            if bad_q in quote_processed:
                quote_processed = quote_processed.replace(bad_q, good_q)

        if quote_processed != current:
            steps.append(
                TransformationStep(
                    rule=NormalizationRule.PUNCTUATION_QUOTES,
                    original_segment=current,
                    transformed_segment=quote_processed,
                    position=0,
                    notes="Standardized curly quotes to ASCII quotes",
                )
            )
            current = quote_processed

        # 4. Optional Terminal Period to Dari
        if self.normalize_terminal_period:
            if current.endswith(".") and not current.endswith(".."):
                period_transformed = current[:-1] + "\u0964"
                steps.append(
                    TransformationStep(
                        rule=NormalizationRule.PUNCTUATION_DARI,
                        original_segment=".",
                        transformed_segment="\u0964",
                        position=len(current) - 1,
                        notes="Normalized sentence-final period to Bengali Dari",
                    )
                )
                current = period_transformed

        # 5. Whitespace collapsing (preserve newlines if multiline)
        lines = current.split("\n")
        collapsed_lines = []
        for line in lines:
            # Replace non-breaking space and irregular horizontal whitespace
            line = line.replace("\u00A0", " ")
            line = re.sub(r"[ \t\r\f\v]+", " ", line).strip()
            collapsed_lines.append(line)
        ws_processed = "\n".join(collapsed_lines).strip()

        if ws_processed != current:
            steps.append(
                TransformationStep(
                    rule=NormalizationRule.WHITESPACE_COLLAPSE,
                    original_segment=current,
                    transformed_segment=ws_processed,
                    position=0,
                    notes="Collapsed redundant whitespace and trimmed line margins",
                )
            )
            current = ws_processed

        return current, steps

    def revert(self, transformed_text: str, steps: List[TransformationStep]) -> str:
        """
        Reconstructs original text from transformed text using reverse transformation steps.
        """
        if not steps:
            return transformed_text
        # The last step's original_segment represents the input to that step,
        # and the first step's original_segment is the initial raw text.
        return steps[0].original_segment
