"""
BLF Nominal Declension Engine.

Generates complete morphosyntactic declension paradigms for Bangla nouns
according to BDSB standards, incorporating case allomorphy, classifier
attachment, number inflection, animacy constraints, and affix ordering.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from blf.linguistics.normalizer import normalize_bangla_text

VOWEL_SIGNS = {"া", "ি", "ী", "ু", "ূ", "ৃ", "ে", "ৈ", "ো", "ৌ"}
INDEPENDENT_VOWELS = {"অ", "আ", "ই", "ঈ", "উ", "ঊ", "ঋ", "এ", "ঐ", "ও", "ঔ"}


class MorphotacticStatus(str, Enum):
    """Epistemic register and morphotactic status of nominal forms."""
    CANONICAL_STANDARD = "CANONICAL_STANDARD"
    ATTESTED_OFFICIAL_EDUCATIONAL_USAGE = "ATTESTED_OFFICIAL_EDUCATIONAL_USAGE"
    ATTESTED_BANGLADESH_USAGE = "ATTESTED_BANGLADESH_USAGE"
    ATTESTED_CONVERSATIONAL = "ATTESTED_CONVERSATIONAL"
    ATTESTED_REGIONAL = "ATTESTED_REGIONAL"
    MARKED = "MARKED"
    REGISTER_UNRESOLVED = "REGISTER_UNRESOLVED"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"
    UNASSESSED = "UNASSESSED"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"


# Positively recognized BDSB canonical nominal lexicon
CANONICAL_NOUN_LEXICON = {
    "মানুষ", "বই", "বাড়ি", "ঢাকা", "ছেলে", "মেয়ে", "কলম", "নদী", "পাখি",
    "শিক্ষক", "ছাত্র", "ছাত্রী", "গাছ", "ফল", "ফুল", "ঘর", "দেশ", "ছবি",
    "পানি", "জল", "মাটি", "বাতাস", "রাস্তা", "গাড়ি", "হাত", "পা", "চোখ",
    "মাথা", "বন্ধু", "ভাই", "বোন", "মা", "বাবা", "টেবিল", "চেয়ার", "কাগজ",
    "শহর", "গ্রাম", "বিদ্যালয়", "দরজা", "জানালা", "আকাশ", "সূর্য", "চাঁদ",
    "গরু", "ঘাস", "বিষয়", "ভাত", "পেন্সিল", "বাচ্চা", "বাজার", "লোক",
}

# Standard morphological suffix sequences in canonical BDSB
CANONICAL_SUFFIXES = [
    # Plural + case
    "গুলোর", "গুলোতে", "গুলোকে", "গুলো",
    "গুলির", "গুলিতে", "গুলিকে", "গুলি",
    "দেরকে", "দেরতে", "দের", "রা", "েরা",
    "গণ", "বৃন্দ", "বর্গ",
    # Classifier + case
    "টির", "টিতে", "টিকে", "টি",
    "টার", "টাতে", "টাকে", "টা",
    "খানার", "খানাতে", "খানাকে", "খানা",
    "খানির", "খানিতে", "খানিকে", "খানি",
    "জনের", "জনকে", "জন",
    # Direct case endings
    "য়ের", "ের", "র",
    "য়ে", "তে", "য়", "ে",
    "কে",
    "",  # Bare lemma
]


def assess_nominal_morphotactics(form: str) -> Dict[str, Any]:
    """
    Assesses the morphotactic and register status of a nominal form in BDSB.
    Distinguishes attested colloquial/educational variants from unsupported forms
    without imposing blanket substring blacklists.
    Fails closed on unknown or unmodeled forms to prevent accidental certification.
    """
    norm = normalize_bangla_text(form)

    # 1. Inverted unsupported plural + diminutive classifier (e.g. গুলোটি,গুলোরটি)
    if "গুলোটি" in norm or "গুলোরটি" in norm:
        return {
            "form": norm,
            "status": MorphotacticStatus.UNSUPPORTED,
            "pattern": "N+গুলো+টি",
            "is_universally_illegal": False,
            "auto_generation_safe": False,
            "evidence": "Inverted plural suffix + singular diminutive classifier inside standard genitive; unsupported in standard BDSB.",
            "review_priority": "LOW",
        }

    # 2. Inverted plural + classifier (বইগুলোটা)
    if "গুলোটা" in norm or "গুলারটা" in norm:
        return {
            "form": norm,
            "status": MorphotacticStatus.REGISTER_UNRESOLVED,
            "pattern": "N+গুলো+টা",
            "is_universally_illegal": False,
            "auto_generation_safe": False,
            "evidence": "Separate N+গুলো+টা pattern; status cannot be inferred from N+টা+গুলো; unresolved without independent evidence.",
            "review_priority": "MEDIUM",
        }

    # 3. Attested N + classifier + plural (e.g. ছবিটাগুলো, বইটাগুলো)
    if "টাগুলো" in norm or "টিগুলো" in norm:
        return {
            "form": norm,
            "status": MorphotacticStatus.ATTESTED_OFFICIAL_EDUCATIONAL_USAGE,
            "pattern": "N+টা+গুলো",
            "is_universally_illegal": False,
            "auto_generation_safe": False,
            "evidence": "Independently attested in official Bangladesh DPE/NCTB teacher-edition material ('ছবিটাগুলো'); occurrence in educational usage confirmed but general BDSB productive status is unverified.",
            "review_priority": "CRITICAL",
        }

    # 4. Colloquial/historical plural + case (e.g. ছেলেগুলাকে, বইগুলা)
    if "গুলাকে" in norm or "গুলাতে" in norm or "গুলার" in norm:
        return {
            "form": norm,
            "status": MorphotacticStatus.ATTESTED_CONVERSATIONAL,
            "pattern": "N+গুলা+CASE",
            "is_universally_illegal": False,
            "auto_generation_safe": False,
            "evidence": "Attested in historical literary Bangla and contemporary Bangladesh conversational usage; not ungrammatical.",
            "review_priority": "HIGH",
        }

    # 5. Colloquial/spoken stacked human oblique (e.g. ছেলেটাদেরকে, মানুষটাদের)
    if "টাদের" in norm or "টিদের" in norm:
        return {
            "form": norm,
            "status": MorphotacticStatus.REGISTER_UNRESOLVED,
            "pattern": "N+টা+দের+CASE",
            "is_universally_illegal": False,
            "auto_generation_safe": False,
            "evidence": "Attested in colloquial spoken patterns; BDSB standard register status remains unresolved; requires human review.",
            "review_priority": "HIGH",
        }

    # 6. Positive evidence rule: Verify against positively recognized canonical morphology
    # Strips valid canonical standard suffixes and checks if stem is in recognized lexicon
    for suffix in CANONICAL_SUFFIXES:
        if suffix and norm.endswith(suffix):
            stem = norm[: -len(suffix)]
            if stem in CANONICAL_NOUN_LEXICON:
                return {
                    "form": norm,
                    "status": MorphotacticStatus.CANONICAL_STANDARD,
                    "pattern": f"STEM+{suffix}",
                    "is_universally_illegal": False,
                    "auto_generation_safe": True,
                    "evidence": "Positively verified canonical standard BDSB nominal morphology.",
                    "review_priority": "NONE",
                }
        elif not suffix and norm in CANONICAL_NOUN_LEXICON:
            return {
                "form": norm,
                "status": MorphotacticStatus.CANONICAL_STANDARD,
                "pattern": "BARE_STEM",
                "is_universally_illegal": False,
                "auto_generation_safe": True,
                "evidence": "Positively verified canonical standard BDSB nominal lemma.",
                "review_priority": "NONE",
            }

    # 7. Fail closed on unrecognized/unmodeled forms
    return {
        "form": norm,
        "status": MorphotacticStatus.UNKNOWN,
        "pattern": "UNKNOWN",
        "is_universally_illegal": False,
        "auto_generation_safe": False,
        "evidence": "Unrecognized or unmodeled nominal form; fails closed without positive canonical evidence.",
        "review_priority": "MEDIUM",
    }



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
