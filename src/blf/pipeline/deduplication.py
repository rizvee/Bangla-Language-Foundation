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
    TIER_4_SEMANTIC_NEAR_DUPLICATE = "TIER_4_SEMANTIC_NEAR_DUPLICATE"
    UNIQUE = "UNIQUE"


@dataclass
class DedupResult:
    record_id: str
    tier: DeduplicationTier
    is_duplicate: bool
    duplicate_of: Optional[str] = None
    similarity_score: float = 1.0
    signature: str = ""


class MultiTierDeduplicator:
    """
    Stateful multi-tier deduplicator for corpus and pilot evaluation records.
    """

    def __init__(self, near_duplicate_threshold: float = 0.85) -> None:
        self.threshold = near_duplicate_threshold
        # Indexes
        self.raw_hashes: Dict[str, str] = {}         # sha256 -> record_id
        self.norm_hashes: Dict[str, str] = {}        # sha256 -> record_id
        self.morpho_signatures: Dict[str, str] = {}  # signature -> record_id
        self.token_sets: Dict[str, Set[str]] = {}    # record_id -> set of tokens

    @staticmethod
    def compute_sha256(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def normalize_for_tier2(text: str) -> str:
        nfc = unicodedata.normalize("NFC", text)
        collapsed = re.sub(r"\s+", " ", nfc).strip()
        return collapsed

    @staticmethod
    def generate_token_signature(text: str) -> Tuple[str, Set[str]]:
        """Splits on whitespace/punctuation to produce sorted token key and token set."""
        tokens = re.findall(r"[\u0980-\u09FF\w]+", text)
        tokens_set = set(tokens)
        sig = " ".join(sorted(tokens))
        return sig, tokens_set

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

        # Tier 3: Morphosyntactic / Lemma Sequence
        token_sig, tokens_set = self.generate_token_signature(norm_text)
        tier3_key = morpho_tag_sequence if morpho_tag_sequence else token_sig
        if tier3_key and tier3_key in self.morpho_signatures:
            return DedupResult(
                record_id=record_id,
                tier=DeduplicationTier.TIER_3_MORPHOSYNTACTIC,
                is_duplicate=True,
                duplicate_of=self.morpho_signatures[tier3_key],
                similarity_score=0.95,
                signature=tier3_key,
            )

        # Tier 4: Semantic / Token Jaccard Near-Duplicate
        for existing_id, existing_tokens in self.token_sets.items():
            sim = self.compute_jaccard(tokens_set, existing_tokens)
            if sim >= self.threshold:
                return DedupResult(
                    record_id=record_id,
                    tier=DeduplicationTier.TIER_4_SEMANTIC_NEAR_DUPLICATE,
                    is_duplicate=True,
                    duplicate_of=existing_id,
                    similarity_score=sim,
                    signature=f"jaccard:{sim:.3f}",
                )

        # Unique - register all signatures
        self.raw_hashes[h1] = record_id
        self.norm_hashes[h2] = record_id
        if tier3_key:
            self.morpho_signatures[tier3_key] = record_id
        self.token_sets[record_id] = tokens_set

        return DedupResult(
            record_id=record_id,
            tier=DeduplicationTier.UNIQUE,
            is_duplicate=False,
            duplicate_of=None,
            similarity_score=0.0,
            signature=h1,
        )
