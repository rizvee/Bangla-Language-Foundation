"""
BLF Complex Predicates, Vector Verbs & Light Verb Construction Engine.

Provides deterministic validation, selectional restriction enforcement, and
morphosyntactic realization for Bangla complex predicates.
"""

from typing import Any, Dict, List, Optional, Tuple
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine, ConjugationError
from blf.linguistics.normalizer import normalize_bangla_text

conjugator = VerbalConjugatorEngine()


class VectorVerbSpec:
    def __init__(
        self,
        vector_lemma: str,
        vector_root: str,
        aspectual_functions: List[str],
        allowed_pole_types: List[str],
        valency_effect: str,
        description: str,
    ):
        self.vector_lemma = vector_lemma
        self.vector_root = vector_root
        self.aspectual_functions = aspectual_functions
        self.allowed_pole_types = allowed_pole_types
        self.valency_effect = valency_effect
        self.description = description


VECTOR_INVENTORY: Dict[str, VectorVerbSpec] = {
    "ফেলা": VectorVerbSpec(
        vector_lemma="ফেলা",
        vector_root="fel",
        aspectual_functions=[
            "TELIC_COMPLETION",
            "COGNITIVE_ACHIEVEMENT",
            "INADVERTENT_UTTERANCE",
            "IRREVERSIBLE_CHANGE",
        ],
        allowed_pole_types=[
            "TRANSITIVE_DYNAMIC",
            "UNERGATIVE_DYNAMIC",
            "COGNITIVE_ACHIEVEMENT",
            "INGESTION",
            "PERCEPTION",
            "COMMUNICATION_RELEASE",
        ],
        valency_effect="NO_VALENCY_CHANGE",
        description="Telic completion, irreversible achievement, cognitive boundary transition, or inadvertent utterance.",
    ),
    "নেওয়া": VectorVerbSpec(
        vector_lemma="নেওয়া",
        vector_root="ne",
        aspectual_functions=[
            "SELF_BENEFACTIVE_INTERNAL",
            "DELIBERATIVE_CONSIDERATION",
            "ACCEPTANCE_ACQUISITION",
        ],
        allowed_pole_types=[
            "TRANSITIVE_AGENTIVE",
            "COGNITIVE_AGENTIVE",
            "DELIBERATIVE",
            "ACQUISITION",
        ],
        valency_effect="NO_VALENCY_CHANGE",
        description="Self-benefactive focus, internal absorption, or deliberate reflective evaluation.",
    ),
    "দেওয়া": VectorVerbSpec(
        vector_lemma="দেওয়া",
        vector_root="de",
        aspectual_functions=[
            "OTHER_BENEFACTIVE_EXTERNAL",
            "PERMISSIVE_CAUSATIVE",
            "DISMISSIVE_RELEASE",
        ],
        allowed_pole_types=[
            "TRANSITIVE_AGENTIVE",
            "TRANSFER_ACTION",
            "PERMISSIVE_COMPLEX",
            "RELEASE_ACTION",
        ],
        valency_effect="ADD_BENEFICIARY_OR_RECIPIENT",
        description="Other-benefactive orientation, external transfer, permission, or dismissive outward release.",
    ),
    "উঠা": VectorVerbSpec(
        vector_lemma="উঠা",
        vector_root="uth",
        aspectual_functions=[
            "SUDDEN_INCEPTION",
            "VOCAL_OUTBURST",
            "CAPACITY_COMPLETION",
            "VERTICAL_MOTION",
        ],
        allowed_pole_types=[
            "INCHOATIVE_EMOTION",
            "VOCALIZATION",
            "CAPACITY_ACTION",
            "MOTION_DIRECTIONAL",
        ],
        valency_effect="NO_VALENCY_CHANGE",
        description="Spontaneous inception, emotional/vocal eruption, or constrained capacity achievement.",
    ),
    "বসা": VectorVerbSpec(
        vector_lemma="বসা",
        vector_root="bosh",
        aspectual_functions=[
            "INADVERTENT_RASH_ACTION",
            "OBSTINATE_ACTION",
            "CONTINUOUS_POSTURE",
        ],
        allowed_pole_types=[
            "VOLITIONAL_RASH_ACTION",
            "SPEECH_ACTION",
            "POSTURE_TRANSITION",
        ],
        valency_effect="NO_VALENCY_CHANGE",
        description="Precipitous or rash action, unadvised speech, or sustained bodily posture.",
    ),
    "পড়া": VectorVerbSpec(
        vector_lemma="পড়া",
        vector_root="por",
        aspectual_functions=[
            "INVOLUNTARY_STATE_TRANSITION",
            "PHYSICAL_COLLAPSE",
            "COGNITIVE_RECALL",
        ],
        allowed_pole_types=[
            "INCHOATIVE_STATE",
            "POSTURE_COLLAPSE",
            "COGNITIVE_RECALL",
            "PHYSICAL_DESCENT",
        ],
        valency_effect="NO_VALENCY_CHANGE",
        description="Involuntary state transition, falling into sleep/collapse, or sudden cognitive recall (mone pora).",
    ),
    "রাখা": VectorVerbSpec(
        vector_lemma="রাখা",
        vector_root="rakh",
        aspectual_functions=[
            "ANTICIPATORY_PRESERVATIVE",
            "RESULT_MAINTENANCE",
        ],
        allowed_pole_types=[
            "TRANSITIVE_AGENTIVE",
            "PREPARATORY_ACTION",
            "MEMORY_MAINTENANCE",
        ],
        valency_effect="NO_VALENCY_CHANGE",
        description="Anticipatory performance with preservative intention (rekhe dewa, likhe rakha).",
    ),
    "থাকা": VectorVerbSpec(
        vector_lemma="থাকা",
        vector_root="thak",
        aspectual_functions=[
            "HABITUAL_CONTINUOUS_DURATION",
            "SUSTAINED_POSTURE",
        ],
        allowed_pole_types=[
            "DURATIVE_ACTION",
            "CONTINUOUS_POSTURE",
            "SUSTAINED_STATE",
        ],
        valency_effect="NO_VALENCY_CHANGE",
        description="Habitual duration, continuous sustained state, or bodily posture maintenance (bose thaka).",
    ),
}


class ComplexPredicateEngine:
    """Validates and realizes complex predicates (compound verbs and LVCs)."""

    def __init__(self):
        pass

    def get_conjunctive_participle(self, pole_verb: str) -> str:
        """
        Returns the verified non-finite conjunctive participle in -e for a pole verb.
        Uses the strict lexicon mapping in VerbalConjugatorEngine.
        """
        return conjugator.get_conjunctive_participle(pole_verb)

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
                f"Selectional restriction violation: Vector '{v_norm}' "
                f"requires pole semantic types {spec.allowed_pole_types}, got '{pole_semantic_type}'"
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
        Handles 'করা', 'হওয়া', 'পাওয়া', etc.
        """
        host = normalize_bangla_text(nominal_host)
        lv_norm = normalize_bangla_text(light_verb)
        lv_conj = conjugator.conjugate_root(lv_norm)
        lv_inflected = lv_conj.get(tense_person_key, lv_norm)
        return f"{host} {lv_inflected}"
