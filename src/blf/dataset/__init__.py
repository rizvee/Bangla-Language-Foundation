"""
BLF Dataset Assembly, Split Policy, and Distribution Audit Framework.

Provides leakage-safe sentence family grouping for train/dev/test splits
and stratified distribution calculators.
"""

from blf.dataset.distribution_audit import DistributionAuditor, QuotaSpecification
from blf.dataset.split_policy import FamilyGroupedSplitter, LeakageViolationError, SplitResult

__all__ = [
    "DistributionAuditor",
    "FamilyGroupedSplitter",
    "LeakageViolationError",
    "QuotaSpecification",
    "SplitResult",
]
