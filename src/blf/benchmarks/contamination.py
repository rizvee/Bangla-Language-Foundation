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
    checked_dimensions: List[str] = field(default_factory=list)
    skipped_dimensions_missing_metadata: List[str] = field(default_factory=list)
    all_required_checks_passed: bool = False
    clean_on_available_checks_only: bool = False

    @property
    def is_clean(self) -> Optional[bool]:
        if self.status == ContaminationStatus.NOT_EVALUABLE:
            return None
        return self.status == ContaminationStatus.CLEAN


class ContaminationChecker:
    """
    Detects train-test overlap and verbatim leakage across 9 dimensions:
    1. RAW_EXACT_MATCH
    2. NORMALIZED_EXACT_MATCH
    3. FAMILY_LEAKAGE
    4. TEMPLATE_LEAKAGE
    5. SOURCE_UNIT_LEAKAGE
    6. NEAR_DUPLICATE_CLUSTER_LEAKAGE
    7. GENERATION_TEMPLATE_LEAKAGE
    8. CONVERSATION_LEAKAGE
    9. NGRAM_OVERLAP
    """

    ALL_DIMENSIONS = (
        "RAW_EXACT_MATCH",
        "NORMALIZED_EXACT_MATCH",
        "FAMILY_LEAKAGE",
        "TEMPLATE_LEAKAGE",
        "SOURCE_UNIT_LEAKAGE",
        "NEAR_DUPLICATE_CLUSTER_LEAKAGE",
        "GENERATION_TEMPLATE_LEAKAGE",
        "CONVERSATION_LEAKAGE",
        "NGRAM_OVERLAP",
    )

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
                checked_dimensions=[],
                skipped_dimensions_missing_metadata=list(self.ALL_DIMENSIONS),
                all_required_checks_passed=False,
                clean_on_available_checks_only=False,
            )

        # Build training indexes across dimensions
        train_raw_exact: Dict[str, str] = {}
        train_norm_exact: Dict[str, str] = {}
        train_ngrams: Dict[Tuple[str, ...], str] = {}
        train_families: Dict[str, str] = {}
        train_templates: Dict[str, str] = {}
        train_source_units: Dict[str, str] = {}
        train_clusters: Dict[str, str] = {}
        train_gen_templates: Dict[str, str] = {}
        train_conversations: Dict[str, str] = {}

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
                train_families[str(fam_id).strip()] = tr_id

            tmpl_id = tr.get("semantic_template_id") or tr.get("template_id")
            if tmpl_id:
                train_templates[str(tmpl_id).strip()] = tr_id

            unit_id = tr.get("source_semantic_unit_id") or tr.get("unit_id")
            if unit_id:
                train_source_units[str(unit_id).strip()] = tr_id

            cluster_id = tr.get("near_duplicate_cluster_id") or tr.get("cluster_id")
            if cluster_id:
                train_clusters[str(cluster_id).strip()] = tr_id

            gen_tmpl = tr.get("generation_template_id")
            if gen_tmpl:
                train_gen_templates[str(gen_tmpl).strip()] = tr_id

            conv_id = tr.get("conversation_id")
            if conv_id:
                train_conversations[str(conv_id).strip()] = tr_id

        # Determine which dimensions have metadata in test or train
        has_text = bool(train_raw_exact) and any(te.get("text") for te in test_items)
        has_fam = bool(train_families) and any((te.get("sentence_family_id") or te.get("family_id")) for te in test_items)
        has_tmpl = bool(train_templates) and any((te.get("semantic_template_id") or te.get("template_id")) for te in test_items)
        has_unit = bool(train_source_units) and any((te.get("source_semantic_unit_id") or te.get("unit_id")) for te in test_items)
        has_cluster = bool(train_clusters) and any((te.get("near_duplicate_cluster_id") or te.get("cluster_id")) for te in test_items)
        has_gen_tmpl = bool(train_gen_templates) and any(te.get("generation_template_id") for te in test_items)
        has_conv = bool(train_conversations) and any(te.get("conversation_id") for te in test_items)

        checked_dims = []
        skipped_dims = []

        for dim, active in [
            ("RAW_EXACT_MATCH", has_text),
            ("NORMALIZED_EXACT_MATCH", has_text),
            ("FAMILY_LEAKAGE", has_fam),
            ("TEMPLATE_LEAKAGE", has_tmpl),
            ("SOURCE_UNIT_LEAKAGE", has_unit),
            ("NEAR_DUPLICATE_CLUSTER_LEAKAGE", has_cluster),
            ("GENERATION_TEMPLATE_LEAKAGE", has_gen_tmpl),
            ("CONVERSATION_LEAKAGE", has_conv),
            ("NGRAM_OVERLAP", has_text and bool(train_ngrams)),
        ]:
            if active:
                checked_dims.append(dim)
            else:
                skipped_dims.append(dim)

        incidents: List[ContaminationIncident] = []
        contaminated_test_ids: Set[str] = set()

        for te in test_items:
            te_id = te.get("item_id") or te.get("record_id") or "te_item"
            raw_text = te.get("text", "")
            norm_text = self._normalize(raw_text) if raw_text else ""
            te_fam_id = str(te.get("sentence_family_id") or te.get("family_id") or "").strip()
            te_tmpl_id = str(te.get("semantic_template_id") or te.get("template_id") or "").strip()
            te_unit_id = str(te.get("source_semantic_unit_id") or te.get("unit_id") or "").strip()
            te_cluster_id = str(te.get("near_duplicate_cluster_id") or te.get("cluster_id") or "").strip()
            te_gen_tmpl = str(te.get("generation_template_id") or "").strip()
            te_conv_id = str(te.get("conversation_id") or "").strip()

            # 1. Raw Exact Match
            if raw_text and raw_text in train_raw_exact:
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

            # 5. Source Semantic Unit Leakage
            if te_unit_id and te_unit_id in train_source_units:
                incidents.append(
                    ContaminationIncident(
                        test_item_id=te_id,
                        training_item_id=train_source_units[te_unit_id],
                        incident_type="SOURCE_UNIT_LEAKAGE",
                        matched_content=f"Shared Source Unit ID: {te_unit_id}",
                        similarity_score=1.0,
                    )
                )
                contaminated_test_ids.add(te_id)
                continue

            # 6. Near Duplicate Cluster Leakage
            if te_cluster_id and te_cluster_id in train_clusters:
                incidents.append(
                    ContaminationIncident(
                        test_item_id=te_id,
                        training_item_id=train_clusters[te_cluster_id],
                        incident_type="NEAR_DUPLICATE_CLUSTER_LEAKAGE",
                        matched_content=f"Shared Cluster ID: {te_cluster_id}",
                        similarity_score=1.0,
                    )
                )
                contaminated_test_ids.add(te_id)
                continue

            # 7. Generation Template Leakage
            if te_gen_tmpl and te_gen_tmpl in train_gen_templates:
                incidents.append(
                    ContaminationIncident(
                        test_item_id=te_id,
                        training_item_id=train_gen_templates[te_gen_tmpl],
                        incident_type="GENERATION_TEMPLATE_LEAKAGE",
                        matched_content=f"Shared Gen Template ID: {te_gen_tmpl}",
                        similarity_score=1.0,
                    )
                )
                contaminated_test_ids.add(te_id)
                continue

            # 8. Conversation Leakage
            if te_conv_id and te_conv_id in train_conversations:
                incidents.append(
                    ContaminationIncident(
                        test_item_id=te_id,
                        training_item_id=train_conversations[te_conv_id],
                        incident_type="CONVERSATION_LEAKAGE",
                        matched_content=f"Shared Conversation ID: {te_conv_id}",
                        similarity_score=1.0,
                    )
                )
                contaminated_test_ids.add(te_id)
                continue

            # 9. N-gram Verbatim Overlap
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

        all_passed = (status == ContaminationStatus.CLEAN) and (len(skipped_dims) == 0)
        clean_available_only = (status == ContaminationStatus.CLEAN) and (len(skipped_dims) > 0)

        return ContaminationReport(
            total_test_items=len(test_items),
            total_training_items=len(training_items),
            clean_items_count=clean_count,
            contaminated_items_count=len(contaminated_test_ids),
            contamination_rate=rate,
            status=status,
            incidents=incidents,
            checked_dimensions=checked_dims,
            skipped_dimensions_missing_metadata=skipped_dims,
            all_required_checks_passed=all_passed,
            clean_on_available_checks_only=clean_available_only,
        )
