"""
BLF Dataset Distribution Audit & Quota Verification.

Calculates representation distributions across registers, dialects,
semantic frames, constructions, and polarity, and audits against target quotas.
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class QuotaSpecification:
    min_registers_count: int = 4
    min_dialects_count: int = 3
    min_frames_count: int = 5
    min_constructions_count: int = 5
    required_registers: Set[str] = field(
        default_factory=lambda: {
            "formal_standard",
            "colloquial_standard",
            "intimate_conversational",
            "social_chat_shorthand",
        }
    )


@dataclass
class AuditReport:
    total_records: int
    register_distribution: Dict[str, int]
    dialect_distribution: Dict[str, int]
    frame_distribution: Dict[str, int]
    construction_distribution: Dict[str, int]
    polarity_distribution: Dict[str, int]
    passed_quotas: bool
    violations: List[str] = field(default_factory=list)


class DistributionAuditor:
    """Audits a collection of linguistic records against demographic and grammatical quotas."""

    def __init__(self, quota_spec: Optional[QuotaSpecification] = None) -> None:
        self.spec = quota_spec or QuotaSpecification()

    def audit(self, records: List[Dict[str, Any]]) -> AuditReport:
        reg_counts: Dict[str, int] = Counter()
        dia_counts: Dict[str, int] = Counter()
        frm_counts: Dict[str, int] = Counter()
        cst_counts: Dict[str, int] = Counter()
        pol_counts: Dict[str, int] = Counter()

        for r in records:
            if "register" in r:
                reg_counts[r["register"].lower()] += 1
            if "dialect" in r or "variety" in r:
                dia = r.get("dialect") or r.get("variety")
                dia_counts[dia.lower()] += 1
            if "semantic_frame_id" in r or "frame_id" in r:
                fid = r.get("semantic_frame_id") or r.get("frame_id")
                frm_counts[fid] += 1
            if "construction_id" in r or "primary_construction_id" in r:
                cid = r.get("construction_id") or r.get("primary_construction_id")
                cst_counts[cid] += 1
            if "polarity" in r:
                pol_counts[r["polarity"].upper()] += 1

        violations: List[str] = []

        # Check register breadth
        if len(reg_counts) < self.spec.min_registers_count:
            violations.append(
                f"Register count ({len(reg_counts)}) below minimum requirement ({self.spec.min_registers_count})"
            )

        # Check required registers
        missing_req_regs = self.spec.required_registers - set(reg_counts.keys())
        if missing_req_regs:
            violations.append(f"Missing required registers: {sorted(list(missing_req_regs))}")

        # Check dialect breadth
        if len(dia_counts) < self.spec.min_dialects_count:
            violations.append(
                f"Dialect count ({len(dia_counts)}) below minimum requirement ({self.spec.min_dialects_count})"
            )

        # Check frame breadth
        if len(frm_counts) < self.spec.min_frames_count:
            violations.append(
                f"Frame count ({len(frm_counts)}) below minimum requirement ({self.spec.min_frames_count})"
            )

        # Check construction breadth
        if len(cst_counts) < self.spec.min_constructions_count:
            violations.append(
                f"Construction count ({len(cst_counts)}) below minimum requirement ({self.spec.min_constructions_count})"
            )

        return AuditReport(
            total_records=len(records),
            register_distribution=dict(reg_counts),
            dialect_distribution=dict(dia_counts),
            frame_distribution=dict(frm_counts),
            construction_distribution=dict(cst_counts),
            polarity_distribution=dict(pol_counts),
            passed_quotas=len(violations) == 0,
            violations=violations,
        )
