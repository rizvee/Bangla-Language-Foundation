"""
BLF Complex Predicates, Vector Verbs & Light Verb Construction Engine.

Provides deterministic validation, selectional restriction enforcement, and
morphosyntactic realization for Bangla complex predicates.
"""

from typing import Any, Dict, List, Optional, Tuple
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine
from blf.linguistics.normalizer import normalize_bangla_text

conjugator = VerbalConjugatorEngine()


class VectorVerbSpec:
    def __init__(
        self,
        vector_lemma: str,
        vector_root: str,
        aspectual_function: str,
        allowed_pole_types: List[str],
        valency_effect: str,
    ):
        self.vector_lemma = vector_lemma
        self.vector_root = vector_root
        self.aspectual_function = aspectual_function
        self.allowed_pole_types = allowed_pole_types
        self.valency_effect = valency_effect


VECTOR_INVENTORY: Dict[str, VectorVerbSpec] = {
    "ফেলা": VectorVerbSpec(
        vector_lemma="ফেলা",
        vector_root="fel",
        aspectual_function="TELIC_COMPLETION_IRREVERSIBILITY",
        allowed_pole_types=["TRANSITIVE_DYNAMIC", "UNERGATIVE_DYNAMIC"],
        valency_effect="NO_VALENCY_CHANGE",
    ),
    "নেওয়া": VectorVerbSpec(
        vector_lemma="নেওয়া",
        vector_root="ne",
        aspectual_function="SELF_BENEFACTIVE_INTERNAL",
        allowed_pole_types=["TRANSITIVE_AGENTIVE", "COGNITIVE_AGENTIVE"],
        valency_effect="NO_VALENCY_CHANGE",
    ),
    "দেওয়া": VectorVerbSpec(
        vector_lemma="দেওয়া",
        vector_root="de",
        aspectual_function="OTHER_BENEFACTIVE_EXTERNAL",
        allowed_pole_types=["TRANSITIVE_AGENTIVE", "TRANSFER_ACTION"],
        valency_effect="ADD_BENEFICIARY_ROLE",
    ),
    "উঠা": VectorVerbSpec(
        vector_lemma="উঠা",
        vector_root="uth",
        aspectual_function="SUDDEN_INCEPTION_SPONTANEOUS",
        allowed_pole_types=["INCHOATIVE", "EMOTION_EXPRESSION", "STATIVE_TRANSITION"],
        valency_effect="NO_VALENCY_CHANGE",
    ),
    "বসা": VectorVerbSpec(
        vector_lemma="বসা",
        vector_root="bosh",
        aspectual_function="INADVERTENT_RASH_ACTION",
        allowed_pole_types=["VOLITIONAL_SPEECH_ACTION", "AGENTIVE_ACTION"],
        valency_effect="NO_VALENCY_CHANGE",
    ),
    "পড়া": VectorVerbSpec(
        vector_lemma="পড়া",
        vector_root="por",
        aspectual_function="INVOLUNTARY_STATE_TRANSITION",
        allowed_pole_types=["TELIC_INTRANSITIVE", "PHYSIOLOGICAL_STATE"],
        valency_effect="NO_VALENCY_CHANGE",
    ),
    "রাখা": VectorVerbSpec(
        vector_lemma="রাখা",
        vector_root="rakh",
        aspectual_function="ANTICIPATORY_PRESERVATIVE",
        allowed_pole_types=["TRANSITIVE_AGENTIVE", "PREPARATORY_ACTION"],
        valency_effect="NO_VALENCY_CHANGE",
    ),
    "থাকা": VectorVerbSpec(
        vector_lemma="থাকা",
        vector_root="thak",
        aspectual_function="HABITUAL_CONTINUOUS_DURATION",
        allowed_pole_types=["DURATIVE_ACTION", "CONTINUOUS_POSTURE"],
        valency_effect="NO_VALENCY_CHANGE",
    ),
}

# Known pole participle map
POLE_CONJUNCTIVE_FORMS: Dict[str, str] = {
    "খা": "খেয়ে",
    "খাওয়া": "খেয়ে",
    "দে": "দিয়ে",
    "দেওয়া": "দিয়ে",
    "নে": "নিয়ে",
    "নেওয়া": "নিয়ে",
    "যা": "গিয়ে",
    "যাওয়া": "গিয়ে",
    "কর": "করে",
    "করা": "করে",
    "বল": "বলে",
    "বলা": "বলে",
    "লিখ": "লিখে",
    "লেখা": "লিখে",
    "দেখ": "দেখে",
    "দেখা": "দেখে",
    "পড়": "পড়ে",
    "পড়া": "পড়ে",
    "কেন": "কিনে",
    "কেনা": "কিনে",
    "কিন": "কিনে",
    "কিনা": "কিনে",
    "শোন": "শুনে",
    "শোনা": "শুনে",
    "ঘুমা": "ঘুমিয়ে",
    "ঘুমানো": "ঘুমিয়ে",
    "হাস": "হেসে",
    "হাসা": "হেসে",
    "কাদ": "কেঁদে",
    "কাঁদা": "কেঁদে",
}


class ComplexPredicateEngine:
    """Validates and realizes complex predicates (compound verbs and LVCs)."""

    def __init__(self):
        pass

    def get_conjunctive_participle(self, pole_verb: str) -> str:
        """Returns the non-finite conjunctive participle in -e for a pole verb."""
        norm = normalize_bangla_text(pole_verb)
        if norm in POLE_CONJUNCTIVE_FORMS:
            return POLE_CONJUNCTIVE_FORMS[norm]
        # Regular fallback: stem + e
        if norm.endswith("া"):
            stem = norm[:-1]
            return stem + "িয়ে"
        return norm + "ে"

    def validate_vector_combination(
        self, pole_verb: str, vector_verb: str, pole_semantic_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates whether a pole verb is selectionally compatible with a vector verb.
        """
        v_norm = normalize_bangla_text(vector_verb)
        if v_norm not in VECTOR_INVENTORY:
            return False, f"Unknown vector verb: '{vector_verb}'"

        spec = VECTOR_INVENTORY[v_norm]
        if pole_semantic_type not in spec.allowed_pole_types:
            return False, (
                f"Selectional restriction violation: Vector '{v_norm}' ({spec.aspectual_function}) "
                f"requires pole types {spec.allowed_pole_types}, got '{pole_semantic_type}'"
            )

        return True, None

    def realize_compound_verb(
        self, pole_verb: str, vector_verb: str, tense_person_key: str
    ) -> str:
        """
        Synthesizes a full surface compound verb: [Pole-e] [Vector+Inflection].
        """
        pole_participle = self.get_conjunctive_participle(pole_verb)
        v_norm = normalize_bangla_text(vector_verb)
        
        # Conjugate vector verb
        v_conj = conjugator.conjugate_root(v_norm)
        v_inflected = v_conj.get(tense_person_key, v_norm)
        
        return f"{pole_participle} {v_inflected}"

    def realize_light_verb_construction(
        self, nominal_host: str, light_verb: str, tense_person_key: str
    ) -> str:
        """
        Synthesizes a Light Verb Construction: [Noun/Adj] [LightVerb+Inflection].
        """
        host = normalize_bangla_text(nominal_host)
        lv_norm = normalize_bangla_text(light_verb)
        lv_conj = conjugator.conjugate_root(lv_norm)
        lv_inflected = lv_conj.get(tense_person_key, lv_norm)
        return f"{host} {lv_inflected}"
