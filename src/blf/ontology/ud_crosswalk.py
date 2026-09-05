"""
Universal Dependencies (UD) Crosswalk for Bangla Language Foundation.

Provides formal mappings between BLF linguistic taxonomy/features and
Universal Dependencies (UD) standards, targeting:
  - UD_Bengali-BRU (BRAC University Treebank)
  - UD_Bengali-PUD (Parallel Universal Dependencies)

Enforces explicit crosswalk relation vocabulary:
  EXACT, CLOSE, BROADER, NARROWER, NO_DIRECT_MAPPING, PROVISIONAL.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CrosswalkRelation(str, Enum):
    EXACT = "EXACT"
    CLOSE = "CLOSE"
    BROADER = "BROADER"
    NARROWER = "NARROWER"
    NO_DIRECT_MAPPING = "NO_DIRECT_MAPPING"
    PROVISIONAL = "PROVISIONAL"


class UDCategory(str, Enum):
    UPOS = "UPOS"
    FEATS = "FEATS"
    DEPREL = "DEPREL"


class UDTreebank(str, Enum):
    UD_BENGALI_BRU = "UD_Bengali-BRU"
    UD_BENGALI_PUD = "UD_Bengali-PUD"


@dataclass(frozen=True)
class CrosswalkEntry:
    blf_category: str
    blf_tag: str
    ud_category: UDCategory
    ud_tag: str
    relation: CrosswalkRelation
    treebank: UDTreebank
    notes: Optional[str] = None


# Canonical Mapping Registries

UPOS_MAPPINGS: List[CrosswalkEntry] = [
    # Nominal
    CrosswalkEntry("pos", "noun", UDCategory.UPOS, "NOUN", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "noun", UDCategory.UPOS, "NOUN", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_PUD),
    CrosswalkEntry("pos", "proper_noun", UDCategory.UPOS, "PROPN", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "proper_noun", UDCategory.UPOS, "PROPN", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_PUD),
    CrosswalkEntry("pos", "pronoun", UDCategory.UPOS, "PRON", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "pronoun", UDCategory.UPOS, "PRON", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_PUD),
    # Verbal
    CrosswalkEntry("pos", "finite_verb", UDCategory.UPOS, "VERB", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "non_finite_verb", UDCategory.UPOS, "VERB", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU, "UD distinguishes VerbForm=Part/Conv/Inf in FEATS rather than UPOS"),
    CrosswalkEntry("pos", "auxiliary_verb", UDCategory.UPOS, "AUX", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "auxiliary_verb", UDCategory.UPOS, "AUX", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_PUD),
    CrosswalkEntry("pos", "vector_verb", UDCategory.UPOS, "AUX", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU, "In complex predicates, vector verbs often annotated as AUX or compound:lvc"),
    # Modifiers
    CrosswalkEntry("pos", "adjective", UDCategory.UPOS, "ADJ", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "adverb", UDCategory.UPOS, "ADV", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "determiner", UDCategory.UPOS, "DET", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "numeral", UDCategory.UPOS, "NUM", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    # Postpositions & Particles
    CrosswalkEntry("pos", "postposition", UDCategory.UPOS, "ADP", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "postposition", UDCategory.UPOS, "ADP", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_PUD),
    CrosswalkEntry("pos", "classifier", UDCategory.UPOS, "PART", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU, "Bangla classifiers (-ta, -khana) often tagged PART or NOUN/clf"),
    CrosswalkEntry("pos", "discourse_particle", UDCategory.UPOS, "PART", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "emphatic_particle", UDCategory.UPOS, "PART", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU),
    # Connectives & Punctuation
    CrosswalkEntry("pos", "coordinating_conjunction", UDCategory.UPOS, "CCONJ", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "subordinating_conjunction", UDCategory.UPOS, "SCONJ", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "interjection", UDCategory.UPOS, "INTJ", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("pos", "punctuation", UDCategory.UPOS, "PUNCT", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
]

FEATS_MAPPINGS: List[CrosswalkEntry] = [
    # Case
    CrosswalkEntry("case", "nominative", UDCategory.FEATS, "Case=Nom", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("case", "accusative_objective", UDCategory.FEATS, "Case=Acc", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU, "BLF Differential Object Marking maps to Acc"),
    CrosswalkEntry("case", "genitive", UDCategory.FEATS, "Case=Gen", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("case", "locative", UDCategory.FEATS, "Case=Loc", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("case", "instrumental", UDCategory.FEATS, "Case=Ins", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU, "Instrumental in Bangla realized via postposition (diye) or locative-instrumental"),
    # Number
    CrosswalkEntry("number", "singular", UDCategory.FEATS, "Number=Sing", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("number", "plural", UDCategory.FEATS, "Number=Plur", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    # Person
    CrosswalkEntry("person", "first", UDCategory.FEATS, "Person=1", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("person", "second_intimate", UDCategory.FEATS, "Person=2|Polite=Infm", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("person", "second_familiar", UDCategory.FEATS, "Person=2|Polite=Form", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU, "Mid-honorific mapping"),
    CrosswalkEntry("person", "second_honorific", UDCategory.FEATS, "Person=2|Polite=Elev", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("person", "third_ordinary", UDCategory.FEATS, "Person=3|Polite=Infm", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("person", "third_honorific", UDCategory.FEATS, "Person=3|Polite=Elev", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    # Tense and Aspect
    CrosswalkEntry("tense", "present", UDCategory.FEATS, "Tense=Pres", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("tense", "past", UDCategory.FEATS, "Tense=Past", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("tense", "future", UDCategory.FEATS, "Tense=Fut", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("aspect", "simple", UDCategory.FEATS, "Aspect=Imp", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("aspect", "progressive", UDCategory.FEATS, "Aspect=Prog", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("aspect", "perfect", UDCategory.FEATS, "Aspect=Perf", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    # VerbForm
    CrosswalkEntry("verb_form", "finite", UDCategory.FEATS, "VerbForm=Fin", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("verb_form", "infinitive", UDCategory.FEATS, "VerbForm=Inf", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("verb_form", "conjunctive_participle", UDCategory.FEATS, "VerbForm=Conv", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU, "Bangla -e participle as converb"),
    CrosswalkEntry("verb_form", "conditional_participle", UDCategory.FEATS, "VerbForm=Conv", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU, "Bangla -le conditional converb"),
]

DEPREL_MAPPINGS: List[CrosswalkEntry] = [
    CrosswalkEntry("dependency", "subject", UDCategory.DEPREL, "nsubj", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "direct_object", UDCategory.DEPREL, "obj", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "indirect_object", UDCategory.DEPREL, "iobj", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "oblique", UDCategory.DEPREL, "obl", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "temporal_oblique", UDCategory.DEPREL, "obl:tmod", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "nominal_modifier", UDCategory.DEPREL, "nmod", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "adverbial_clause", UDCategory.DEPREL, "advcl", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "adnominal_clause", UDCategory.DEPREL, "acl", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "light_verb_compound", UDCategory.DEPREL, "compound:lvc", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "serial_verb_compound", UDCategory.DEPREL, "compound:svc", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "case_marker", UDCategory.DEPREL, "case", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "classifier_attachment", UDCategory.DEPREL, "clf", CrosswalkRelation.CLOSE, UDTreebank.UD_BENGALI_BRU, "UD clf dependency relation"),
    CrosswalkEntry("dependency", "discourse_particle", UDCategory.DEPREL, "discourse", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    CrosswalkEntry("dependency", "root_predicate", UDCategory.DEPREL, "root", CrosswalkRelation.EXACT, UDTreebank.UD_BENGALI_BRU),
    # Provisional or Unmapped items
    CrosswalkEntry("dependency", "echo_reduplication", UDCategory.DEPREL, "compound:redup", CrosswalkRelation.PROVISIONAL, UDTreebank.UD_BENGALI_BRU, "Proposed extension for South Asian reduplicative morphology"),
    CrosswalkEntry("dependency", "differential_object_flag", UDCategory.DEPREL, "NO_DIRECT_DEPREL", CrosswalkRelation.NO_DIRECT_MAPPING, UDTreebank.UD_BENGALI_BRU, "DOM in Bangla is morphosyntactic (Case=Acc marking condition), not a distinct dependency relation"),
]


class UDCrosswalkEngine:
    """Provides querying, translation, and validation of BLF to UD mappings."""

    def __init__(self) -> None:
        self.entries: List[CrosswalkEntry] = list(UPOS_MAPPINGS + FEATS_MAPPINGS + DEPREL_MAPPINGS)

    def find_mappings(
        self,
        blf_category: Optional[str] = None,
        blf_tag: Optional[str] = None,
        ud_category: Optional[UDCategory] = None,
        treebank: Optional[UDTreebank] = None,
    ) -> List[CrosswalkEntry]:
        results = self.entries
        if blf_category is not None:
            results = [e for e in results if e.blf_category.lower() == blf_category.lower()]
        if blf_tag is not None:
            results = [e for e in results if e.blf_tag.lower() == blf_tag.lower()]
        if ud_category is not None:
            results = [e for e in results if e.ud_category == ud_category]
        if treebank is not None:
            results = [e for e in results if e.treebank == treebank]
        return results

    def map_blf_to_ud(
        self,
        blf_category: str,
        blf_tag: str,
        treebank: UDTreebank = UDTreebank.UD_BENGALI_BRU,
    ) -> Optional[CrosswalkEntry]:
        matches = self.find_mappings(blf_category=blf_category, blf_tag=blf_tag, treebank=treebank)
        if matches:
            return matches[0]
        # Fallback to any treebank if specific one not found
        generic_matches = self.find_mappings(blf_category=blf_category, blf_tag=blf_tag)
        return generic_matches[0] if generic_matches else None

    def map_ud_to_blf(
        self,
        ud_category: UDCategory,
        ud_tag: str,
        treebank: Optional[UDTreebank] = None,
    ) -> List[CrosswalkEntry]:
        results = [e for e in self.entries if e.ud_category == ud_category and e.ud_tag == ud_tag]
        if treebank is not None:
            results = [e for e in results if e.treebank == treebank]
        return results

    def get_relation_statistics(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in self.entries:
            counts[e.relation.value] = counts.get(e.relation.value, 0) + 1
        return counts
