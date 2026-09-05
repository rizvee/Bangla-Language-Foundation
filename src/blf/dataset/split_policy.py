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
    total_records_by_partition: Dict[str, int] = field(default_factory=dict)
    total_groups_by_partition: Dict[str, int] = field(default_factory=dict)
    cross_partition_group_leakage: int = 0
    unassigned_orphan_records: int = 0
    excluded_unknown_group_records: List[Dict[str, Any]] = field(default_factory=list)

    def verify_no_leakage(self) -> None:
        """Verifies pairwise disjointness of family IDs across splits."""
        if self.train_family_ids & self.dev_family_ids:
            overlap = self.train_family_ids & self.dev_family_ids
            raise LeakageViolationError(f"Train and Dev share group IDs: {overlap}")
        if self.train_family_ids & self.test_family_ids:
            overlap = self.train_family_ids & self.test_family_ids
            raise LeakageViolationError(f"Train and Test share group IDs: {overlap}")
        if self.dev_family_ids & self.test_family_ids:
            overlap = self.dev_family_ids & self.test_family_ids
            raise LeakageViolationError(f"Dev and Test share group IDs: {overlap}")


class FamilyGroupedSplitter:
    """
    Splits items into Train/Dev/Test splits while guaranteeing zero-leakage:
    All variants sharing a sentence_family_id, semantic_template_id,
    source_semantic_unit_id, or near_duplicate_cluster_id are grouped via
    connected components into the exact same partition.
    """

    def __init__(
        self,
        train_ratio: float = 0.70,
        dev_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42,
        fail_closed: bool = True,
    ) -> None:
        if round(train_ratio + dev_ratio + test_ratio, 4) != 1.0:
            raise ValueError(f"Split ratios must sum to 1.0 (got {train_ratio + dev_ratio + test_ratio})")
        self.train_ratio = train_ratio
        self.dev_ratio = dev_ratio
        self.test_ratio = test_ratio
        self.seed = seed
        self.fail_closed = fail_closed

    def _extract_grouping_keys(self, item: Dict[str, Any]) -> Set[str]:
        keys = set()
        for field_name in (
            "sentence_family_id",
            "family_id",
            "semantic_template_id",
            "template_id",
            "source_semantic_unit_id",
            "unit_id",
            "near_duplicate_cluster_id",
            "cluster_id",
        ):
            val = item.get(field_name)
            if val and isinstance(val, str) and val.strip():
                keys.add(f"{field_name}:{val.strip()}")
        return keys

    def split(self, items: List[Dict[str, Any]]) -> SplitResult:
        if not items:
            return SplitResult([], [], [], set(), set(), set())

        # 1. Connected Component Grouping
        valid_items: List[Dict[str, Any]] = []
        excluded_items: List[Dict[str, Any]] = []

        item_keys_list: List[Set[str]] = []
        for idx, it in enumerate(items):
            keys = self._extract_grouping_keys(it)
            if not keys:
                if self.fail_closed:
                    item_identifier = it.get("record_id") or it.get("item_id") or f"index_{idx}"
                    raise LeakageViolationError(
                        f"Record '{item_identifier}' has LEAKAGE_GROUP_UNKNOWN: missing all grouping identifiers "
                        "(sentence_family_id, semantic_template_id, source_semantic_unit_id, near_duplicate_cluster_id)."
                    )
                else:
                    it_copy = dict(it)
                    it_copy["leakage_group"] = "LEAKAGE_GROUP_UNKNOWN"
                    excluded_items.append(it_copy)
            else:
                valid_items.append(it)
                item_keys_list.append(keys)

        if not valid_items:
            return SplitResult(
                train_items=[],
                dev_items=[],
                test_items=[],
                train_family_ids=set(),
                dev_family_ids=set(),
                test_family_ids=set(),
                total_records_by_partition={"train": 0, "dev": 0, "test": 0},
                total_groups_by_partition={"train": 0, "dev": 0, "test": 0},
                cross_partition_group_leakage=0,
                unassigned_orphan_records=len(excluded_items),
                excluded_unknown_group_records=excluded_items,
            )

        # Build key-to-items mapping for connected components
        key_to_item_indices: Dict[str, List[int]] = defaultdict(list)
        for i, keys in enumerate(item_keys_list):
            for k in keys:
                key_to_item_indices[k].append(i)

        # BFS / DFS connected components across items
        visited_items: Set[int] = set()
        connected_components: List[List[int]] = []

        for i in range(len(valid_items)):
            if i in visited_items:
                continue
            component: List[int] = []
            queue = [i]
            visited_items.add(i)

            while queue:
                curr = queue.pop(0)
                component.append(curr)
                for k in item_keys_list[curr]:
                    for neighbor in key_to_item_indices[k]:
                        if neighbor not in visited_items:
                            visited_items.add(neighbor)
                            queue.append(neighbor)

            connected_components.append(component)

        # Name each component by its canonical sorted keys
        component_groups: Dict[str, List[Dict[str, Any]]] = {}
        for comp in connected_components:
            all_comp_keys = sorted(set.union(*(item_keys_list[idx] for idx in comp)))
            canonical_group_id = "|".join(all_comp_keys)
            component_groups[canonical_group_id] = [valid_items[idx] for idx in comp]

        # 2. Deterministic Shuffle & Allocation
        sorted_group_ids = sorted(component_groups.keys())
        rng = random.Random(self.seed)
        rng.shuffle(sorted_group_ids)

        total_groups = len(sorted_group_ids)
        train_count = int(total_groups * self.train_ratio)
        dev_count = int(total_groups * self.dev_ratio)

        train_groups = set(sorted_group_ids[:train_count])
        dev_groups = set(sorted_group_ids[train_count : train_count + dev_count])
        test_groups = set(sorted_group_ids[train_count + dev_count :])

        train_items = [it for gid in train_groups for it in component_groups[gid]]
        dev_items = [it for gid in dev_groups for it in component_groups[gid]]
        test_items = [it for gid in test_groups for it in component_groups[gid]]

        def _extract_clean_fams(groups: Set[str]) -> Set[str]:
            fams = set()
            for gid in groups:
                for part in gid.split("|"):
                    if ":" in part:
                        fams.add(part.split(":", 1)[1])
                    else:
                        fams.add(part)
            return fams

        train_fams = _extract_clean_fams(train_groups)
        dev_fams = _extract_clean_fams(dev_groups)
        test_fams = _extract_clean_fams(test_groups)

        result = SplitResult(
            train_items=train_items,
            dev_items=dev_items,
            test_items=test_items,
            train_family_ids=train_fams,
            dev_family_ids=dev_fams,
            test_family_ids=test_fams,
            total_records_by_partition={
                "train": len(train_items),
                "dev": len(dev_items),
                "test": len(test_items),
            },
            total_groups_by_partition={
                "train": len(train_groups),
                "dev": len(dev_groups),
                "test": len(test_groups),
            },
            cross_partition_group_leakage=0,
            unassigned_orphan_records=len(excluded_items),
            excluded_unknown_group_records=excluded_items,
        )
        result.verify_no_leakage()
        return result
