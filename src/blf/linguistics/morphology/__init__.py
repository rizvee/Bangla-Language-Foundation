"""
BLF Morphology Package.
"""

from .nominal_declension import (
    NominalDeclensionEngine,
    MorphotacticStatus,
    assess_nominal_morphotactics,
    is_vowel_final,
    get_genitive_suffix,
    get_locative_suffix,
)
from .pronominal_paradigms import PronominalParadigmEngine
from .verbal_conjugator import VerbalConjugatorEngine

__all__ = [
    "NominalDeclensionEngine",
    "MorphotacticStatus",
    "assess_nominal_morphotactics",
    "PronominalParadigmEngine",
    "VerbalConjugatorEngine",
    "is_vowel_final",
    "get_genitive_suffix",
    "get_locative_suffix",
]
