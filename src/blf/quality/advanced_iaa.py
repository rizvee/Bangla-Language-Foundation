"""
BLF Multi-Rater Inter-Annotator Agreement (IAA) Engine.

Implements Fleiss' Kappa and Krippendorff's Alpha for multi-annotator studies.
Fails closed with InsufficientDataError when reviewer data is missing or empty.
"""

from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple


class InsufficientDataError(ValueError):
    """Raised when an agreement metric is computed without adequate raters or items."""
    pass


def compute_fleiss_kappa(
    ratings_matrix: List[List[str]],
    categories: Optional[List[str]] = None,
) -> float:
    """
    Computes Fleiss' Kappa for N items rated by k raters each into m categories.
    ratings_matrix: list of rows (one per item), where each row is a list of ratings from k raters.
    Each row MUST have the exact same number of raters k >= 2.
    """
    if not ratings_matrix:
        raise InsufficientDataError("Cannot compute Fleiss' Kappa on empty ratings matrix.")

    n_items = len(ratings_matrix)
    k_raters = len(ratings_matrix[0])

    if n_items < 2:
        raise InsufficientDataError("Fleiss' Kappa requires at least 2 items.")
    if k_raters < 2:
        raise InsufficientDataError("Fleiss' Kappa requires at least 2 raters per item.")

    # Validate that all items have the same number of raters
    for i, row in enumerate(ratings_matrix):
        if len(row) != k_raters:
            raise InsufficientDataError(
                f"Inconsistent rater count at item index {i}: expected {k_raters}, got {len(row)}"
            )

    # Determine unique categories
    if categories is None:
        cats_set: Set[str] = set()
        for row in ratings_matrix:
            cats_set.update(row)
        categories = sorted(list(cats_set))

    if len(categories) < 2:
        # Trivial agreement on single category
        return 1.0

    # Build count matrix: n_items x n_categories
    cat_to_idx = {cat: idx for idx, cat in enumerate(categories)}
    counts = [[0] * len(categories) for _ in range(n_items)]
    for i, row in enumerate(ratings_matrix):
        for val in row:
            if val in cat_to_idx:
                counts[i][cat_to_idx[val]] += 1

    # p_j: proportion of all assignments to category j
    total_ratings = n_items * k_raters
    p_j = [sum(counts[i][j] for i in range(n_items)) / total_ratings for j in range(len(categories))]

    # P_i: degree of agreement on item i
    # P_i = (1 / (k * (k - 1))) * (sum(n_ij^2) - k)
    P_i = []
    for i in range(n_items):
        sum_sq = sum(counts[i][j] ** 2 for j in range(len(categories)))
        P_i.append((sum_sq - k_raters) / (k_raters * (k_raters - 1)))

    P_bar = sum(P_i) / n_items
    P_bar_e = sum(pj ** 2 for pj in p_j)

    if P_bar_e >= 1.0:
        return 1.0

    return (P_bar - P_bar_e) / (1.0 - P_bar_e)


def compute_krippendorff_alpha_nominal(
    reliability_data: List[List[Optional[str]]],
) -> float:
    """
    Computes Krippendorff's Alpha for nominal data.
    reliability_data: list of rows (raters) x columns (units), where entries can be None if unrated.
    """
    if not reliability_data or not reliability_data[0]:
        raise InsufficientDataError("Cannot compute Krippendorff's Alpha on empty matrix.")

    n_raters = len(reliability_data)
    n_units = len(reliability_data[0])

    if n_raters < 2 or n_units < 2:
        raise InsufficientDataError("Krippendorff's Alpha requires >= 2 raters and >= 2 units.")

    # Collect all values per unit
    unit_values: List[List[str]] = []
    all_values: Set[str] = set()
    for u in range(n_units):
        vals = [reliability_data[r][u] for r in range(n_raters) if reliability_data[r][u] is not None]
        unit_values.append(vals)
        all_values.update(vals)

    # Filter out units with < 2 ratings (no pair comparison possible)
    valid_units = [vals for vals in unit_values if len(vals) >= 2]
    if not valid_units:
        raise InsufficientDataError("No units have at least two concurrent ratings.")

    categories = sorted(list(all_values))
    if len(categories) < 2:
        return 1.0

    # Coincidence matrix for nominal metric
    # Total pair comparisons
    n_total = sum(len(vals) for vals in valid_units)

    # Observed disagreement D_o
    d_o_sum = 0.0
    for vals in valid_units:
        m = len(vals)
        c = Counter(vals)
        # Pairs of different values
        mismatches = sum(c[v1] * c[v2] for v1 in c for v2 in c if v1 != v2) / 2.0
        d_o_sum += mismatches / (m - 1)

    D_o = d_o_sum / sum(len(vals) for vals in valid_units)

    # Expected disagreement D_e
    marginal_counts = Counter([v for vals in valid_units for v in vals])
    total_valid_ratings = sum(marginal_counts.values())
    d_e_sum = sum(marginal_counts[v1] * marginal_counts[v2] for v1 in marginal_counts for v2 in marginal_counts if v1 != v2) / 2.0
    D_e = d_e_sum / (total_valid_ratings * (total_valid_ratings - 1)) if total_valid_ratings > 1 else 1.0

    if D_e == 0:
        return 1.0

    alpha = 1.0 - (D_o / D_e)
    return alpha
