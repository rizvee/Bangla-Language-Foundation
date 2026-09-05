"""
BLF Leakage-Safe Dataset Splitter.

Enforces zero-leakage invariant by strictly grouping all variant sentences
of the same Sentence Family into the exact same partition (Train, Dev, or Test).
"""

from collections import defaultdict
from dataclasses import dataclass, field
import hashlib
import random
from typing import Any, Dict, List, Optional, Set, Tuple


class LeakageViolationError(Exception):
    """Raised when sentence families or propositions cross split boundaries."""
    pass


@dataclass
class SplitResult:
    train_items: List[Dict[str, Any]]
    dev_items: List[Dict[str, Any]]
    test_items: List[Dict[str, Any]]
    train_family_ids: Set[str]
    dev_family_ids: Set[str]
    test_family_ids: Set[str]

    def verify_no_leakage(self) -> None:
        """Verifies pairwise disjointness of family IDs across splits."""
        if self.train_family_ids & self.dev_family_ids:
            overlap = self.train_family_ids & self.dev_family_ids
            raise LeakageViolationError(f"Train and Dev share sentence family IDs: {overlap}")
        if self.train_family_ids & self.test_family_ids:
            overlap = self.train_family_ids & self.test_family_ids
            raise LeakageViolationError(f"Train and Test share sentence family IDs: {overlap}")
        if self.dev_family_ids & self.test_family_ids:
            overlap = self.dev_family_ids & self.test_family_ids
            raise LeakageViolationError(f"Dev and Test share sentence family IDs: {overlap}")


class FamilyGroupedSplitter:
    """
    Splits items into Train/Dev/Test splits while guaranteeing that all variants
    sharing the same sentence_family_id remain strictly co-located in the same partition.
    """

    def __init__(
        self,
        train_ratio: float = 0.70,
        dev_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42,
    ) -> None:
        if round(train_ratio + dev_ratio + test_ratio, 4) != 1.0:
            raise ValueError(f"Split ratios must sum to 1.0 (got {train_ratio + dev_ratio + test_ratio})")
        self.train_ratio = train_ratio
        self.dev_ratio = dev_ratio
        self.test_ratio = test_ratio
        self.seed = seed

    def split(self, items: List[Dict[str, Any]]) -> SplitResult:
        if not items:
            return SplitResult([], [], [], set(), set(), set())

        # Group items by sentence_family_id
        families: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for it in items:
            fam_id = it.get("sentence_family_id") or it.get("family_id") or it.get("item_id")
            families[fam_id].append(it)

        # Sort family IDs deterministically
        sorted_fam_ids = sorted(families.keys())
        rng = random.Random(self.seed)
        rng.shuffle(sorted_fam_ids)

        total_fams = len(sorted_fam_ids)
        train_count = int(total_fams * self.train_ratio)
        dev_count = int(total_fams * self.dev_ratio)

        # Allocate
        train_fams = set(sorted_fam_ids[:train_count])
        dev_fams = set(sorted_fam_ids[train_count : train_count + dev_count])
        test_fams = set(sorted_fam_ids[train_count + dev_count :])

        train_items = [it for fid in train_fams for it in families[fid]]
        dev_items = [it for fid in dev_fams for it in families[fid]]
        test_items = [it for fid in test_fams for it in families[fid]]

        result = SplitResult(
            train_items=train_items,
            dev_items=dev_items,
            test_items=test_items,
            train_family_ids=train_fams,
            dev_family_ids=dev_fams,
            test_family_ids=test_fams,
        )
        result.verify_no_leakage()
        return result
