"""
BLF Nominal Declension Engine.

Generates complete morphosyntactic declension paradigms for Bangla nouns
according to BDSB standards, incorporating case allomorphy, classifier
attachment, number inflection, animacy constraints, and affix ordering.
"""

from typing import Any, Dict, List, Optional
from blf.linguistics.normalizer import normalize_bangla_text

VOWEL_SIGNS = {"া", "ি", "ী", "ু", "ূ", "ৃ", "ে", "ৈ", "ো", "ৌ"}
INDEPENDENT_VOWELS = {"অ", "আ", "ই", "ঈ", "উ", "ঊ", "ঋ", "এ", "ঐ", "ও", "ঔ"}


def is_vowel_final(stem: str) -> bool:
    """Detects whether a Bengali noun stem ends with a vowel sign or independent vowel."""
    if not stem:
        return False
    normalized = normalize_bangla_text(stem)
    last_char = normalized[-1]
    return last_char in VOWEL_SIGNS or last_char in INDEPENDENT_VOWELS or last_char in {"য়", "ও", "ই"}


def get_genitive_suffix(stem: str) -> str:
    """Returns -r for vowel-kar stems, -yer for independent-vowel stems, -er for consonant-final stems."""
    normalized = normalize_bangla_text(stem)
    last_char = normalized[-1] if normalized else ""
    if last_char in INDEPENDENT_VOWELS or last_char in {"ই", "উ", "ও", "য়"}:
        return "য়ের"
    elif last_char in VOWEL_SIGNS:
        return "র"
    return "ের"


def get_locative_suffix(stem: str) -> str:
    """Returns -te for vowel-final non-a stems, -y for -a/-o vowel stems, -ye for independent vowels, -e for consonant stems."""
    normalized = normalize_bangla_text(stem)
    last_char = normalized[-1] if normalized else ""
    if last_char == "া" or last_char == "আ" or last_char == "ও":
        return "য়"
    elif last_char in INDEPENDENT_VOWELS or last_char in {"ই", "উ", "য়"}:
        return "য়ে"
    elif last_char in VOWEL_SIGNS:
        return "তে"
    else:
        return "ে"


class NominalDeclensionEngine:
    """Deterministic noun declension engine for Bangladesh Standard Bangla."""

    def __init__(self):
        pass

    def decline_noun(
        self,
        lemma: str,
        is_human: bool = False,
        classifier: str = "টা",
    ) -> Dict[str, str]:
        """
        Generates a comprehensive declension table across Case, Number, and Definiteness.
        
        Dimensions:
        - Case: NOM (Nominative), ACC (Accusative/Objective), GEN (Genitive), LOC (Locative)
        - Number: SG (Singular), PL (Plural)
        - Definiteness: INDEF (Indefinite/Bare), DEF (Definite with classifier)
        """
        stem = normalize_bangla_text(lemma)
        vowel_fin = is_vowel_final(stem)

        cells = {}

        # 1. Singular Indefinite
        cells["NOM.SG.INDEF"] = stem
        cells["ACC.SG.INDEF"] = stem + "কে" if is_human else stem
        cells["GEN.SG.INDEF"] = stem + get_genitive_suffix(stem)
        cells["LOC.SG.INDEF"] = stem + get_locative_suffix(stem)

        # 2. Singular Definite (Root + Classifier + Case)
        clf = classifier
        def_stem = stem + clf
        cells["NOM.SG.DEF"] = def_stem
        cells["ACC.SG.DEF"] = def_stem + "কে" if is_human else def_stem
        cells["GEN.SG.DEF"] = def_stem + "র"  # Classifiers like -ta, -ti, -khana end in vowel -> takes -r
        cells["LOC.SG.DEF"] = def_stem + "তে" if clf.endswith(("া", "ি")) else def_stem + "ে"

        # 3. Plural Indefinite / Collective
        if is_human:
            # Human plural uses -ra / -era
            nom_pl_suffix = "রা" if vowel_fin else "েরা"
            cells["NOM.PL.INDEF"] = stem + nom_pl_suffix
            cells["ACC.PL.INDEF"] = stem + "দের" + "কে"
            cells["GEN.PL.INDEF"] = stem + "দের"
            cells["LOC.PL.INDEF"] = stem + "দের" + "তে"
        else:
            # Inanimate plural uses -gulo
            pl_stem = stem + "গুলো"
            cells["NOM.PL.INDEF"] = pl_stem
            cells["ACC.PL.INDEF"] = pl_stem
            cells["GEN.PL.INDEF"] = pl_stem + "র"
            cells["LOC.PL.INDEF"] = pl_stem + "তে"

        # 4. Plural Definite
        pl_def_stem = stem + "গুলো"
        cells["NOM.PL.DEF"] = pl_def_stem
        cells["ACC.PL.DEF"] = pl_def_stem + "কে" if is_human else pl_def_stem
        cells["GEN.PL.DEF"] = pl_def_stem + "র"
        cells["LOC.PL.DEF"] = pl_def_stem + "তে"

        return cells
