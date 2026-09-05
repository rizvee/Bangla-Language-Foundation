"""
BLF Inter-Annotator Agreement (IAA) & Adjudication Module — Phase 2A.2d.

Provides dual-target statistical metrics:
1. Candidate-Level Acceptability Agreement (Pooled Cohen's Kappa, Raw Agreement, Confusion Matrices)
2. Preferred-Candidate Set Agreement (Exact Matches, Partial Overlaps, Disjoint Preferences, NONE Agreement)

Enforces strict study completeness gates for official studies.
"""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple


def compute_raw_agreement(pair_judgments: List[Tuple[str, str]]) -> float:
    """Computes observed percent agreement between two raters over identical pairs."""
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
    p_o = sum(1 for a, b in zip(r1, r2) if a == b) / n

    categories = list(set(r1) | set(r2))
    c1 = Counter(r1)
    c2 = Counter(r2)

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


def evaluate_dual_iaa(
    decoded_reviews_a: List[Dict[str, Any]],
    decoded_reviews_b: List[Dict[str, Any]],
    reviewer_a: str,
    reviewer_b: str,
    enforce_official_completeness: bool = False,
) -> Dict[str, Any]:
    """
    Computes rigorous dual IAA statistics between two reviewers across decoded review records:
    A. Candidate-Level Acceptability Agreement (per canonical item x candidate)
    B. Preferred-Candidate Set Agreement (per canonical item)

    If enforce_official_completeness is True, fails closed if study criteria are not met.
    """
    # Build lookup by canonical_item_id
    dict_a = {}
    duplicate_a = []
    for r in decoded_reviews_a:
        cid = r["canonical_item_id"]
        if cid in dict_a:
            duplicate_a.append(cid)
        dict_a[cid] = r

    dict_b = {}
    duplicate_b = []
    for r in decoded_reviews_b:
        cid = r["canonical_item_id"]
        if cid in dict_b:
            duplicate_b.append(cid)
        dict_b[cid] = r

    items_a = set(dict_a.keys())
    items_b = set(dict_b.keys())
    common_items = sorted(list(items_a & items_b))
    only_a = sorted(list(items_a - items_b))
    only_b = sorted(list(items_b - items_a))

    # Completeness verification
    sess_a = {r.get("session_id") for r in decoded_reviews_a}
    sess_b = {r.get("session_id") for r in decoded_reviews_b}
    same_session = bool(sess_a and sess_b and sess_a == sess_b)
    has_duplicates = bool(duplicate_a or duplicate_b)
    full_40_both = len(items_a) == 40 and len(items_b) == 40
    identical_item_sets = items_a == items_b and len(common_items) == 40

    completeness_report = {
        "same_private_session": same_session,
        "session_ids_a": sorted(list(sess_a)),
        "session_ids_b": sorted(list(sess_b)),
        "reviewer_pair": [reviewer_a, reviewer_b],
        "unique_items_a": len(items_a),
        "unique_items_b": len(items_b),
        "common_items_count": len(common_items),
        "items_only_a": only_a,
        "items_only_b": only_b,
        "has_duplicates_a": duplicate_a,
        "has_duplicates_b": duplicate_b,
        "is_official_study_complete": same_session and full_40_both and identical_item_sets and not has_duplicates,
    }

    if enforce_official_completeness:
        if not same_session:
            raise ValueError(f"Official IAA failure: Reviewers belong to different sessions: {sess_a} vs {sess_b}")
        if has_duplicates:
            raise ValueError(f"Official IAA failure: Duplicate canonical records detected: A={duplicate_a}, B={duplicate_b}")
        if not full_40_both or not identical_item_sets:
            raise ValueError(
                f"Official IAA failure: Non-identical or incomplete canonical item sets: "
                f"A has {len(items_a)}, B has {len(items_b)}, common={len(common_items)}"
            )

    # Target A: Candidate Acceptability
    cand_pairs_a = []
    cand_pairs_b = []
    cand_tuples = []
    cat_cand_pairs = defaultdict(list)
    cand_disagreements = []

    # Target B: Preferred-Candidate Sets
    exact_pref_matches = 0
    partial_pref_overlaps = 0
    disjoint_prefs = 0
    none_agreements = 0
    pref_disagreements = []

    for item_id in common_items:
        rec_a = dict_a[item_id]
        rec_b = dict_b[item_id]
        cat = rec_a.get("category", "GENERAL")

        # 1. Candidate-level judgments
        judg_map_a = rec_a.get("canonical_candidate_judgments", {})
        judg_map_b = rec_b.get("canonical_candidate_judgments", {})
        common_cands = sorted(list(set(judg_map_a.keys()) & set(judg_map_b.keys())))

        for cand_id in common_cands:
            ja = judg_map_a[cand_id].get("acceptability") if isinstance(judg_map_a[cand_id], dict) else judg_map_a[cand_id]
            jb = judg_map_b[cand_id].get("acceptability") if isinstance(judg_map_b[cand_id], dict) else judg_map_b[cand_id]

            if ja and jb:
                cand_pairs_a.append(ja)
                cand_pairs_b.append(jb)
                cand_tuples.append((ja, jb))
                cat_cand_pairs[cat].append((ja, jb))

                if ja != jb:
                    cand_disagreements.append({
                        "canonical_item_id": item_id,
                        "canonical_candidate_id": cand_id,
                        "category": cat,
                        "judgment_a": ja,
                        "judgment_b": jb,
                        "disagreement_type": "CANDIDATE_ACCEPTABILITY_MISMATCH",
                        "status": "FLAGGED_FOR_ADJUDICATION",
                    })

        # 2. Preferred-candidate set comparison
        pref_a = set(rec_a.get("canonical_preferred_candidates", []))
        pref_b = set(rec_b.get("canonical_preferred_candidates", []))

        if pref_a == pref_b:
            exact_pref_matches += 1
            if pref_a == {"NONE"}:
                none_agreements += 1
        elif pref_a & pref_b:
            partial_pref_overlaps += 1
            pref_disagreements.append({
                "canonical_item_id": item_id,
                "category": cat,
                "preferred_a": sorted(list(pref_a)),
                "preferred_b": sorted(list(pref_b)),
                "relationship": "PARTIAL_OVERLAP",
            })
        else:
            disjoint_prefs += 1
            pref_disagreements.append({
                "canonical_item_id": item_id,
                "category": cat,
                "preferred_a": sorted(list(pref_a)),
                "preferred_b": sorted(list(pref_b)),
                "relationship": "DISJOINT",
            })

    # Candidate Acceptability Stats
    cand_raw_agr = compute_raw_agreement(cand_tuples) if cand_tuples else 0.0
    cand_kappa = compute_cohens_kappa(cand_pairs_a, cand_pairs_b) if cand_tuples else 0.0
    cand_conf_mat = build_confusion_matrix(cand_pairs_a, cand_pairs_b) if cand_tuples else {}

    cat_breakdown = {}
    for cat, pairs in cat_cand_pairs.items():
        cat_breakdown[cat] = {
            "candidate_pairs_count": len(pairs),
            "raw_agreement": compute_raw_agreement(pairs),
            "agreed_count": sum(1 for j1, j2 in pairs if j1 == j2),
        }

    # Preferred Candidate Stats
    total_items = len(common_items)
    exact_pref_rate = exact_pref_matches / total_items if total_items else 0.0

    return {
        "reviewer_a": reviewer_a,
        "reviewer_b": reviewer_b,
        "completeness_report": completeness_report,
        "total_items_reviewed_a": len(items_a),
        "total_items_reviewed_b": len(items_b),
        "common_evaluated_items": total_items,
        "items_only_a": only_a,
        "items_only_b": only_b,
        "candidate_acceptability": {
            "metric_name": "POOLED_CANDIDATE_LEVEL_COHENS_KAPPA",
            "total_candidate_pairs": len(cand_tuples),
            "raw_agreement": cand_raw_agr,
            "cohens_kappa": cand_kappa,
            "judgment_distribution_a": dict(Counter(cand_pairs_a)),
            "judgment_distribution_b": dict(Counter(cand_pairs_b)),
            "category_breakdown": cat_breakdown,
            "confusion_matrix": cand_conf_mat,
            "total_candidate_disagreements": len(cand_disagreements),
            "disagreements": cand_disagreements,
            "epistemic_note": "Candidate observations are nested inside items and are not fully independent; metric represents exploratory pilot reliability evidence.",
        },
        "preferred_candidates": {
            "total_items": total_items,
            "exact_matches": exact_pref_matches,
            "exact_match_rate": exact_pref_rate,
            "none_agreements": none_agreements,
            "partial_overlaps": partial_pref_overlaps,
            "disjoint_preferences": disjoint_prefs,
            "disagreements": pref_disagreements,
        },
    }
