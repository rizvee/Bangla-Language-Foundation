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
class NormalizationOp:
    rule: NormalizationRule
    original_segment: str
    transformed_segment: str
    position_before: int
    position_after: int
    lossy: bool
    notes: Optional[str] = None


# Backward-compatible alias
TransformationStep = NormalizationOp


@dataclass
class NormalizationResult:
    raw_text: str
    normalized_text: str
    operations_applied: List[NormalizationOp]
    lossy: bool
    reversible_without_snapshot: bool
    span_map: Optional[List[Tuple[int, int, int, int]]] = None  # (raw_start, raw_end, norm_start, norm_end)


class ReversibleNormalizer:
    """
    Normalizes Bengali text while maintaining an auditable log of operations.
    
    EPISTEMIC NOTE ON REVERSIBILITY:
    Transformations such as whitespace collapsing and quotation standardization are
    inherently lossy (collapsing multiple spaces or variations into canonical forms).
    Therefore, the `revert()` method restores the stored initial raw text snapshot
    rather than performing algorithmic inverse transformation.
    """

    # Bengali Dari: U+0964 (standard danda). Devanagari danda is also U+0964.
    # Western period used as Dari: '.' -> '।' (only when ending a Bengali sentence)
    BENGALI_HASANTA = "\u09CD"
    ZWJ = "\u200D"
    ZWNJ = "\u200C"

    def __init__(self, normalize_terminal_period_to_dari: bool = False) -> None:
        self.normalize_terminal_period = normalize_terminal_period_to_dari

    def normalize_detailed(self, text: str) -> NormalizationResult:
        """
        Runs pipeline steps on text, returning a comprehensive NormalizationResult.
        """
        if not text:
            return NormalizationResult(
                raw_text="",
                normalized_text="",
                operations_applied=[],
                lossy=False,
                reversible_without_snapshot=True,
                span_map=[],
            )

        raw_text = text
        operations: List[NormalizationOp] = []
        current = text
        is_lossy = False

        # 1. Unicode NFC Normalization (canonical decomposition -> canonical composition)
        nfc_text = unicodedata.normalize("NFC", current)
        if nfc_text != current:
            operations.append(
                NormalizationOp(
                    rule=NormalizationRule.UNICODE_NFC,
                    original_segment=current,
                    transformed_segment=nfc_text,
                    position_before=0,
                    position_after=0,
                    lossy=False,  # Canonical equivalence is non-lossy
                    notes="Unicode NFC normalization applied",
                )
            )
            current = nfc_text

        # 2. ZWJ / ZWNJ Policy
        # Valid Bangla ZWJ usage: preceded by Hasanta (e.g. \u09cd\u200d for subjoined consonants or ya-phala)
        # Stray ZWJ/ZWNJ: at word boundaries, after spaces, or consecutive ZWJ/ZWNJ -> quarantined/stripped
        cleaned_chars = []
        n = len(current)
        i = 0
        stray_zwj_found = False
        while i < n:
            ch = current[i]
            if ch in (self.ZWJ, self.ZWNJ):
                has_valid_preceding = i > 0 and current[i - 1] == self.BENGALI_HASANTA
                if has_valid_preceding:
                    cleaned_chars.append(ch)
                else:
                    stray_zwj_found = True
                    is_lossy = True
            else:
                cleaned_chars.append(ch)
            i += 1

        zwj_processed = "".join(cleaned_chars)
        if zwj_processed != current:
            operations.append(
                NormalizationOp(
                    rule=NormalizationRule.ZWJ_ZWNJ_POLICY,
                    original_segment=current,
                    transformed_segment=zwj_processed,
                    position_before=0,
                    position_after=0,
                    lossy=True,
                    notes="Quarantined and stripped stray/spurious ZWJ/ZWNJ characters outside hasanta contexts",
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
                is_lossy = True

        if quote_processed != current:
            operations.append(
                NormalizationOp(
                    rule=NormalizationRule.PUNCTUATION_QUOTES,
                    original_segment=current,
                    transformed_segment=quote_processed,
                    position_before=0,
                    position_after=0,
                    lossy=True,
                    notes="Standardized curly quotes to ASCII quotes",
                )
            )
            current = quote_processed

        # 4. Optional Terminal Period to Dari
        if self.normalize_terminal_period:
            if current.endswith(".") and not current.endswith(".."):
                period_transformed = current[:-1] + "\u0964"
                operations.append(
                    NormalizationOp(
                        rule=NormalizationRule.PUNCTUATION_DARI,
                        original_segment=".",
                        transformed_segment="\u0964",
                        position_before=len(current) - 1,
                        position_after=len(period_transformed) - 1,
                        lossy=True,
                        notes="Normalized sentence-final period to Bengali Dari",
                    )
                )
                current = period_transformed
                is_lossy = True

        # 5. Whitespace collapsing (preserve newlines if multiline)
        lines = current.split("\n")
        collapsed_lines = []
        for line in lines:
            line = line.replace("\u00A0", " ")
            line = re.sub(r"[ \t\r\f\v]+", " ", line).strip()
            collapsed_lines.append(line)
        ws_processed = "\n".join(collapsed_lines).strip()

        if ws_processed != current:
            operations.append(
                NormalizationOp(
                    rule=NormalizationRule.WHITESPACE_COLLAPSE,
                    original_segment=current,
                    transformed_segment=ws_processed,
                    position_before=0,
                    position_after=0,
                    lossy=True,
                    notes="Collapsed redundant whitespace and trimmed line margins",
                )
            )
            current = ws_processed
            is_lossy = True

        span_map = [(0, len(raw_text), 0, len(current))]

        return NormalizationResult(
            raw_text=raw_text,
            normalized_text=current,
            operations_applied=operations,
            lossy=is_lossy,
            reversible_without_snapshot=(not is_lossy),
            span_map=span_map,
        )

    def normalize(self, text: str) -> Tuple[str, List[NormalizationOp]]:
        """Backward-compatible tuple interface."""
        res = self.normalize_detailed(text)
        return res.normalized_text, res.operations_applied

    def revert(self, transformed_text: str, steps: List[NormalizationOp]) -> str:
        """
        Restores the initial raw text snapshot recorded in the operations list.
        NOTE: This performs snapshot restoration, not algorithmic inverse string transformation,
        because operations like whitespace collapse and quote standardizations are inherently lossy.
        """
        if not steps:
            return transformed_text
        return steps[0].original_segment
