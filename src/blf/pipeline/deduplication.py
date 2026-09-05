"""
BLF 4-Tier Deduplication Engine.

Provides hierarchical deduplication across:
  Tier 1: Exact Raw Hash (SHA-256)
  Tier 2: Normalized Hash (Unicode NFC + whitespace collapsed)
  Tier 3: Morphosyntactic / Lemma Signature
  Tier 4: Semantic / Token Jaccard Near-Duplicate
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import unicodedata


class DeduplicationTier(str, Enum):
    TIER_1_EXACT = "TIER_1_EXACT"
    TIER_2_NORMALIZED = "TIER_2_NORMALIZED"
    TIER_3_MORPHOSYNTACTIC = "TIER_3_MORPHOSYNTACTIC"
    TIER_4_LEXICAL_OVERLAP = "TIER_4_LEXICAL_OVERLAP"
    # Backward compatible alias
    TIER_4_SEMANTIC_NEAR_DUPLICATE = "TIER_4_LEXICAL_OVERLAP"
    UNIQUE = "UNIQUE"


@dataclass
class DedupResult:
    record_id: str
    tier: DeduplicationTier
    is_duplicate: bool
    duplicate_of: Optional[str] = None
    similarity_score: float = 1.0
    signature: str = ""
    requires_review: bool = False
    candidate_similarity: bool = False
    notes: Optional[str] = None


class MultiTierDeduplicator:
    """
    Stateful multi-tier deduplicator for corpus and pilot evaluation records.
    Protects linguistic minimal pairs, word order permutations, and negative polarity pairs.
    """

    def __init__(self, near_duplicate_threshold: float = 0.85) -> None:
        self.threshold = near_duplicate_threshold
        # Indexes
        self.raw_hashes: Dict[str, str] = {}         # sha256 -> record_id
        self.norm_hashes: Dict[str, str] = {}        # sha256 -> record_id
        self.morpho_signatures: Dict[str, str] = {}  # signature -> record_id
        self.token_sets: Dict[str, Set[str]] = {}    # record_id -> set of tokens
        self.record_meta: Dict[str, Dict[str, Any]] = {}  # record_id -> metadata (families, minimal pairs)

    @staticmethod
    def compute_sha256(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def normalize_for_tier2(text: str) -> str:
        nfc = unicodedata.normalize("NFC", text)
        collapsed = re.sub(r"\s+", " ", nfc).strip()
        return collapsed

    @staticmethod
    def generate_token_set(text: str) -> Set[str]:
        """Extracts Bengali and word tokens as an unordered set for lexical overlap analysis."""
        tokens = re.findall(r"[\u0980-\u09FF\w]+", text)
        return set(tokens)

    @staticmethod
    def compute_jaccard(set1: Set[str], set2: Set[str]) -> float:
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0

    def check_and_add(
        self,
        record_id: str,
        text: str,
        morpho_tag_sequence: Optional[str] = None,
        *,
        sentence_family_id: Optional[str] = None,
        minimal_pair_id: Optional[str] = None,
        negative_pair_id: Optional[str] = None,
        semantic_template_id: Optional[str] = None,
    ) -> DedupResult:
        # Tier 1: Exact Hash
        h1 = self.compute_sha256(text)
        if h1 in self.raw_hashes:
            return DedupResult(
                record_id=record_id,
                tier=DeduplicationTier.TIER_1_EXACT,
                is_duplicate=True,
                duplicate_of=self.raw_hashes[h1],
                similarity_score=1.0,
                signature=h1,
            )

        # Tier 2: Normalized Hash
        norm_text = self.normalize_for_tier2(text)
        h2 = self.compute_sha256(norm_text)
        if h2 in self.norm_hashes:
            return DedupResult(
                record_id=record_id,
                tier=DeduplicationTier.TIER_2_NORMALIZED,
                is_duplicate=True,
                duplicate_of=self.norm_hashes[h2],
                similarity_score=1.0,
                signature=h2,
            )

        # Tier 3: Morphosyntactic Sequence
        # If morpho_tag_sequence is not available, Tier 3 is SKIPPED (NEVER fall back to bag-of-words)
        # Even when present, identical POS sequence produces similarity flag, NEVER automatic deletion.
        candidate_sim = False
        notes = None
        if morpho_tag_sequence:
            if morpho_tag_sequence in self.morpho_signatures:
                candidate_sim = True
                notes = f"Shares morphosyntactic POS sequence with {self.morpho_signatures[morpho_tag_sequence]}"
        else:
            notes = "Tier 3 morphosyntactic check skipped (no POS sequence provided)"

        # Tier 4: Lexical Overlap (Jaccard Near-Duplicate Candidate)
        tokens_set = self.generate_token_set(norm_text)
        for existing_id, existing_tokens in self.token_sets.items():
            sim = self.compute_jaccard(tokens_set, existing_tokens)
            if sim >= self.threshold:
                # Check whether existing and candidate are documented minimal pairs or family variants
                prev_meta = self.record_meta.get(existing_id, {})
                shares_family = (
                    (sentence_family_id and sentence_family_id == prev_meta.get("sentence_family_id"))
                    or (minimal_pair_id and minimal_pair_id == prev_meta.get("minimal_pair_id"))
                    or (negative_pair_id and negative_pair_id == prev_meta.get("negative_pair_id"))
                    or (semantic_template_id and semantic_template_id == prev_meta.get("semantic_template_id"))
                )
                if shares_family:
                    # Legitimate minimal pair or family variant: protected from deduplication
                    notes = f"Protected minimal pair / family variant of {existing_id}"
                else:
                    # Lexical overlap candidate: flagged for review, NEVER automatically deleted
                    # Register into index so subsequent records can compare
                    self._register_record(
                        record_id, h1, h2, morpho_tag_sequence, tokens_set,
                        sentence_family_id, minimal_pair_id, negative_pair_id, semantic_template_id,
                    )
                    return DedupResult(
                        record_id=record_id,
                        tier=DeduplicationTier.TIER_4_LEXICAL_OVERLAP,
                        is_duplicate=False,
                        duplicate_of=existing_id,
                        similarity_score=sim,
                        signature=f"jaccard:{sim:.3f}",
                        requires_review=True,
                        candidate_similarity=candidate_sim,
                        notes="High lexical overlap candidate flagged for manual inspection; not deleted",
                    )

        # Unique or non-duplicate: register
        self._register_record(
            record_id, h1, h2, morpho_tag_sequence, tokens_set,
            sentence_family_id, minimal_pair_id, negative_pair_id, semantic_template_id,
        )

        return DedupResult(
            record_id=record_id,
            tier=DeduplicationTier.UNIQUE,
            is_duplicate=False,
            duplicate_of=None,
            similarity_score=0.0,
            signature=h1,
            candidate_similarity=candidate_sim,
            notes=notes,
        )

    def _register_record(
        self,
        record_id: str,
        h1: str,
        h2: str,
        morpho_tag_sequence: Optional[str],
        tokens_set: Set[str],
        sentence_family_id: Optional[str],
        minimal_pair_id: Optional[str],
        negative_pair_id: Optional[str],
        semantic_template_id: Optional[str],
    ) -> None:
        self.raw_hashes[h1] = record_id
        self.norm_hashes[h2] = record_id
        if morpho_tag_sequence and morpho_tag_sequence not in self.morpho_signatures:
            self.morpho_signatures[morpho_tag_sequence] = record_id
        self.token_sets[record_id] = tokens_set
        self.record_meta[record_id] = {
            "sentence_family_id": sentence_family_id,
            "minimal_pair_id": minimal_pair_id,
            "negative_pair_id": negative_pair_id,
            "semantic_template_id": semantic_template_id,
        }
