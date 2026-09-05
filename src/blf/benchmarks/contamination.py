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


@dataclass
class ContaminationIncident:
    test_item_id: str
    training_item_id: str
    incident_type: str  # "EXACT_MATCH", "NGRAM_OVERLAP", "FAMILY_LEAKAGE"
    matched_content: str
    similarity_score: float


@dataclass
class ContaminationReport:
    total_test_items: int
    total_training_items: int
    clean_items_count: int
    contaminated_items_count: int
    contamination_rate: float
    incidents: List[ContaminationIncident] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.contaminated_items_count == 0


class ContaminationChecker:
    """Detects train-test overlap and verbatim leakage."""

    def __init__(self, ngram_size: int = 8) -> None:
        self.ngram_size = ngram_size

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
                clean_items_count=len(test_items),
                contaminated_items_count=0,
                contamination_rate=0.0,
                incidents=[],
            )

        # Build training indexes
        train_exact: Dict[str, str] = {}  # text -> train_id
        train_ngrams: Dict[Tuple[str, ...], str] = {}  # ngram -> train_id
        train_families: Dict[str, str] = {}  # family_id -> train_id

        for tr in training_items:
            tr_id = tr.get("item_id", "tr_item")
            tr_text = tr.get("text", "").strip()
            if tr_text:
                train_exact[tr_text] = tr_id
                tokens = self._tokenize(tr_text)
                for ng in self._extract_ngrams(tokens):
                    train_ngrams[ng] = tr_id
            fam_id = tr.get("sentence_family_id") or tr.get("family_id")
            if fam_id:
                train_families[fam_id] = tr_id

        incidents: List[ContaminationIncident] = []
        contaminated_test_ids: Set[str] = set()

        for te in test_items:
            te_id = te.get("item_id", "te_item")
            te_text = te.get("text", "").strip()
            te_fam_id = te.get("sentence_family_id") or te.get("family_id")

            # 1. Exact Match
            if te_text in train_exact:
                incidents.append(
                    ContaminationIncident(
                        test_item_id=te_id,
                        training_item_id=train_exact[te_text],
                        incident_type="EXACT_MATCH",
                        matched_content=te_text,
                        similarity_score=1.0,
                    )
                )
                contaminated_test_ids.add(te_id)
                continue

            # 2. Sentence Family Leakage
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

            # 3. N-gram verbatim overlap
            tokens = self._tokenize(te_text)
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

        return ContaminationReport(
            total_test_items=len(test_items),
            total_training_items=len(training_items),
            clean_items_count=clean_count,
            contaminated_items_count=len(contaminated_test_ids),
            contamination_rate=rate,
            incidents=incidents,
        )
