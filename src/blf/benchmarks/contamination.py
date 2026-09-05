"""
BLF Evaluation Contamination & Leakage Auditor.

Verifies that benchmark evaluation test sets are strictly free from:
  1. Exact sentence duplication against training sets
  2. Long verbatim n-gram overlap (default: 8-gram or longer)
  3. Cross-split sentence family co-occurrence
"""

from collections import defaultdict
from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Set, Tuple


from enum import Enum


class ContaminationStatus(str, Enum):
    CLEAN = "CLEAN"
    CONTAMINATED = "CONTAMINATED"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass
class ContaminationIncident:
    test_item_id: str
    training_item_id: str
    incident_type: str  # "RAW_EXACT_MATCH", "NORMALIZED_EXACT_MATCH", "FAMILY_LEAKAGE", "TEMPLATE_LEAKAGE", "NGRAM_OVERLAP"
    matched_content: str
    similarity_score: float


@dataclass
class ContaminationReport:
    total_test_items: int
    total_training_items: int
    clean_items_count: int
    contaminated_items_count: int
    contamination_rate: float
    status: ContaminationStatus
    incidents: List[ContaminationIncident] = field(default_factory=list)

    @property
    def is_clean(self) -> Optional[bool]:
        if self.status == ContaminationStatus.NOT_EVALUABLE:
            return None
        return self.status == ContaminationStatus.CLEAN


class ContaminationChecker:
    """
    Detects train-test overlap and verbatim leakage across:
    1. Raw exact matches
    2. Normalized exact matches (Unicode NFC + whitespace collapsed)
    3. Sentence family leakage
    4. Semantic template leakage
    5. N-gram verbatim overlap
    """

    def __init__(self, ngram_size: int = 8) -> None:
        self.ngram_size = ngram_size

    @staticmethod
    def _normalize(text: str) -> str:
        import unicodedata
        nfc = unicodedata.normalize("NFC", text)
        return re.sub(r"\s+", " ", nfc).strip()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"[\u0980-\u09FF\w]+", text)

    def _extract_ngrams(self, tokens: List[str]) -> Set[Tuple[str, ...]]:
        if len(tokens) < self.ngram_size:
            return set()
        return {tuple(tokens[i : i + self.ngram_size]) for i in range(len(tokens) - self.ngram_size + 1)}

    def audit(
        self,
        test_items: List[Dict[str, Any]],
        training_items: List[Dict[str, Any]],
    ) -> ContaminationReport:
        if not test_items or not training_items:
            return ContaminationReport(
                total_test_items=len(test_items),
                total_training_items=len(training_items),
                clean_items_count=0,
                contaminated_items_count=0,
                contamination_rate=0.0,
                status=ContaminationStatus.NOT_EVALUABLE,
                incidents=[],
            )

        # Build training indexes
        train_raw_exact: Dict[str, str] = {}
        train_norm_exact: Dict[str, str] = {}
        train_ngrams: Dict[Tuple[str, ...], str] = {}
        train_families: Dict[str, str] = {}
        train_templates: Dict[str, str] = {}

        for tr in training_items:
            tr_id = tr.get("item_id") or tr.get("record_id") or "tr_item"
            raw_text = tr.get("text", "")
            if raw_text:
                train_raw_exact[raw_text] = tr_id
                norm_text = self._normalize(raw_text)
                train_norm_exact[norm_text] = tr_id

                tokens = self._tokenize(norm_text)
                for ng in self._extract_ngrams(tokens):
                    train_ngrams[ng] = tr_id

            fam_id = tr.get("sentence_family_id") or tr.get("family_id")
            if fam_id:
                train_families[fam_id] = tr_id

            tmpl_id = tr.get("semantic_template_id") or tr.get("template_id")
            if tmpl_id:
                train_templates[tmpl_id] = tr_id

        incidents: List[ContaminationIncident] = []
        contaminated_test_ids: Set[str] = set()

        for te in test_items:
            te_id = te.get("item_id") or te.get("record_id") or "te_item"
            raw_text = te.get("text", "")
            norm_text = self._normalize(raw_text) if raw_text else ""
            te_fam_id = te.get("sentence_family_id") or te.get("family_id")
            te_tmpl_id = te.get("semantic_template_id") or te.get("template_id")

            # 1. Raw Exact Match
            if raw_text in train_raw_exact:
                incidents.append(
                    ContaminationIncident(
                        test_item_id=te_id,
                        training_item_id=train_raw_exact[raw_text],
                        incident_type="RAW_EXACT_MATCH",
                        matched_content=raw_text,
                        similarity_score=1.0,
                    )
                )
                contaminated_test_ids.add(te_id)
                continue

            # 2. Normalized Exact Match
            if norm_text and norm_text in train_norm_exact:
                incidents.append(
                    ContaminationIncident(
                        test_item_id=te_id,
                        training_item_id=train_norm_exact[norm_text],
                        incident_type="NORMALIZED_EXACT_MATCH",
                        matched_content=norm_text,
                        similarity_score=1.0,
                    )
                )
                contaminated_test_ids.add(te_id)
                continue

            # 3. Sentence Family Leakage
            if te_fam_id and te_fam_id in train_families:
                incidents.append(
                    ContaminationIncident(
                        test_item_id=te_id,
                        training_item_id=train_families[te_fam_id],
                        incident_type="FAMILY_LEAKAGE",
                        matched_content=f"Shared Family ID: {te_fam_id}",
                        similarity_score=1.0,
                    )
                )
                contaminated_test_ids.add(te_id)
                continue

            # 4. Semantic Template Leakage
            if te_tmpl_id and te_tmpl_id in train_templates:
                incidents.append(
                    ContaminationIncident(
                        test_item_id=te_id,
                        training_item_id=train_templates[te_tmpl_id],
                        incident_type="TEMPLATE_LEAKAGE",
                        matched_content=f"Shared Template ID: {te_tmpl_id}",
                        similarity_score=1.0,
                    )
                )
                contaminated_test_ids.add(te_id)
                continue

            # 5. N-gram Verbatim Overlap
            if norm_text:
                tokens = self._tokenize(norm_text)
                te_ngrams = self._extract_ngrams(tokens)
                overlap_ngrams = te_ngrams.intersection(train_ngrams.keys())
                if overlap_ngrams:
                    first_ng = list(overlap_ngrams)[0]
                    incidents.append(
                        ContaminationIncident(
                            test_item_id=te_id,
                            training_item_id=train_ngrams[first_ng],
                            incident_type="NGRAM_OVERLAP",
                            matched_content=" ".join(first_ng),
                            similarity_score=len(first_ng) / max(len(tokens), 1),
                        )
                    )
                    contaminated_test_ids.add(te_id)

        clean_count = len(test_items) - len(contaminated_test_ids)
        rate = len(contaminated_test_ids) / len(test_items) if test_items else 0.0
        status = ContaminationStatus.CONTAMINATED if contaminated_test_ids else ContaminationStatus.CLEAN

        return ContaminationReport(
            total_test_items=len(test_items),
            total_training_items=len(training_items),
            clean_items_count=clean_count,
            contaminated_items_count=len(contaminated_test_ids),
            contamination_rate=rate,
            status=status,
            incidents=incidents,
        )
