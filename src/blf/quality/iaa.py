"""
BLF Inter-Annotator Agreement (IAA) & Adjudication Module.

Provides standard statistical metrics (Raw Agreement, Cohen's Kappa)
and reconciliation workflows for multi-annotator linguistic reviews.
"""

from collections import Counter
from typing import Any, Dict, List, Optional, Tuple


def compute_raw_agreement(pair_judgments: List[Tuple[str, str]]) -> float:
    """Computes simple observed percent agreement between two raters."""
    if not pair_judgments:
        return 0.0
    matches = sum(1 for j1, j2 in pair_judgments if j1 == j2)
    return matches / len(pair_judgments)


def compute_cohens_kappa(r1: List[str], r2: List[str]) -> float:
    """
    Computes Cohen's Kappa for categorical annotation judgments.
    kappa = (P_o - P_e) / (1 - P_e)
    """
    if len(r1) != len(r2) or not r1:
        return 0.0

    n = len(r1)
    # Observed agreement
    p_o = sum(1 for a, b in zip(r1, r2) if a == b) / n

    # Marginal category frequencies
    categories = list(set(r1) | set(r2))
    c1 = Counter(r1)
    c2 = Counter(r2)

    # Expected agreement by chance
    p_e = sum((c1[cat] / n) * (c2[cat] / n) for cat in categories)

    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def extract_disagreements(
    reviews_by_item: Dict[str, List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """
    Extracts all items with conflicting reviewer judgments into an adjudication queue.
    """
    disagreements = []
    for item_id, revs in reviews_by_item.items():
        if len(revs) >= 2:
            judgments = {r["judgment"] for r in revs}
            if len(judgments) > 1:
                disagreements.append({
                    "item_id": item_id,
                    "review_count": len(revs),
                    "conflicting_judgments": list(judgments),
                    "reviews": revs,
                    "status": "DISAGREEMENT_FLAGGED",
                })
    return disagreements


def adjudicate_review(
    item_id: str,
    final_judgment: str,
    adjudicator_id: str,
    notes: str,
    preferred_form: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Constructs an authoritative adjudicated review outcome for an item.
    """
    return {
        "item_id": item_id,
        "adjudication_status": "ADJUDICATED_GOLD",
        "adjudicator_id": adjudicator_id,
        "final_judgment": final_judgment,
        "preferred_form": preferred_form,
        "adjudication_notes": notes,
    }
