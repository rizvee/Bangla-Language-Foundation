"""
BLF Inter-Annotator Agreement (IAA) & Adjudication Module.

Provides standard statistical metrics (Raw Agreement, Cohen's Kappa, Confusion Matrices)
and reconciliation workflows for multi-rater linguistic reviews.
"""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple


def compute_raw_agreement(pair_judgments: List[Tuple[str, str]]) -> float:
    """Computes observed percent agreement between two raters over identical items."""
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

    if p_e >= 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def build_confusion_matrix(r1: List[str], r2: List[str]) -> Dict[str, Dict[str, int]]:
    """Builds a 2D contingency table of categorical judgments between rater 1 and rater 2."""
    categories = sorted(list(set(r1) | set(r2)))
    matrix = {c1: {c2: 0 for c2 in categories} for c1 in categories}
    for j1, j2 in zip(r1, r2):
        matrix[j1][j2] += 1
    return matrix


def evaluate_reviewer_pair(
    reviews: List[Dict[str, Any]],
    reviewer_a: str,
    reviewer_b: str,
    category_lookup: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Computes rigorous pairwise IAA statistics over the exact intersection of items
    reviewed by both reviewer_a and reviewer_b.
    """
    revs_a = {r["item_id"]: r for r in reviews if r.get("reviewer_id_pseudonymous") == reviewer_a}
    revs_b = {r["item_id"]: r for r in reviews if r.get("reviewer_id_pseudonymous") == reviewer_b}

    items_a = set(revs_a.keys())
    items_b = set(revs_b.keys())
    common_items = sorted(list(items_a & items_b))
    only_a = sorted(list(items_a - items_b))
    only_b = sorted(list(items_b - items_a))

    paired_judgments_a = []
    paired_judgments_b = []
    paired_tuples = []
    disagreements = []

    # Category breakdown tracking
    cat_pairs = defaultdict(list)

    for iid in common_items:
        ra = revs_a[iid]
        rb = revs_b[iid]
        ja = ra["judgment"]
        jb = rb["judgment"]

        paired_judgments_a.append(ja)
        paired_judgments_b.append(jb)
        paired_tuples.append((ja, jb))

        cat = category_lookup.get(iid, "GENERAL") if category_lookup else "GENERAL"
        cat_pairs[cat].append((ja, jb))

        # Check for disagreement in judgment or preferred candidate
        pref_a = ra.get("canonical_candidate_id") or ra.get("preferred_displayed_candidate")
        pref_b = rb.get("canonical_candidate_id") or rb.get("preferred_displayed_candidate")

        if ja != jb or pref_a != pref_b:
            disagreements.append({
                "item_id": iid,
                "category": cat,
                "reviewer_a": reviewer_a,
                "judgment_a": ja,
                "preferred_a": pref_a,
                "comments_a": ra.get("comments"),
                "reviewer_b": reviewer_b,
                "judgment_b": jb,
                "preferred_b": pref_b,
                "comments_b": rb.get("comments"),
                "disagreement_type": "JUDGMENT_MISMATCH" if ja != jb else "PREFERENCE_MISMATCH",
                "status": "FLAGGED_FOR_ADJUDICATION",
            })

    raw_agr = compute_raw_agreement(paired_tuples) if paired_tuples else 0.0
    kappa = compute_cohens_kappa(paired_judgments_a, paired_judgments_b) if paired_tuples else 0.0
    conf_matrix = build_confusion_matrix(paired_judgments_a, paired_judgments_b) if paired_tuples else {}

    per_category = {}
    for cat, pairs in cat_pairs.items():
        per_category[cat] = {
            "item_count": len(pairs),
            "raw_agreement": compute_raw_agreement(pairs),
            "agreed_count": sum(1 for j1, j2 in pairs if j1 == j2),
        }

    return {
        "reviewer_a": reviewer_a,
        "reviewer_b": reviewer_b,
        "total_items_reviewed_a": len(items_a),
        "total_items_reviewed_b": len(items_b),
        "common_evaluated_items": len(common_items),
        "items_only_a": only_a,
        "items_only_b": only_b,
        "raw_agreement": raw_agr,
        "cohens_kappa": kappa,
        "category_breakdown": per_category,
        "confusion_matrix": conf_matrix,
        "total_disagreements": len(disagreements),
        "disagreement_items": disagreements,
    }
