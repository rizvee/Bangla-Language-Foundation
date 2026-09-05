"""
BLF Complex Predicates, Vector Verbs & Light Verb Construction Engine.

Provides deterministic validation, selectional restriction enforcement, and
morphosyntactic realization for Bangla complex predicates.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine, ConjugationError
from blf.linguistics.normalizer import normalize_bangla_text

conjugator = VerbalConjugatorEngine()


class VectorCompatibilityStatus(str, Enum):
    """Epistemic compatibility status between a pole verb and an aspectual vector verb."""
    ALLOWED = "ALLOWED"
    CONTEXT_DEPENDENT = "CONTEXT_DEPENDENT"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


class VectorVerbSpec:
    def __init__(
        self,
        vector_lemma: str,
        vector_root: str,
        aspectual_functions: List[str],
        allowed_pole_types: List[str],
        valency_effect: str,
        description: str,
        context_dependent_pole_types: Optional[List[str]] = None,
    ):
        self.vector_lemma = vector_lemma
        self.vector_root = vector_root
        self.aspectual_functions = aspectual_functions
        self.allowed_pole_types = allowed_pole_types
        self.valency_effect = valency_effect
        self.description = description
        self.context_dependent_pole_types = context_dependent_pole_types or []


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
        context_dependent_pole_types=[
            "STATIVE_POSTURE",
            "STATIVE_BEING",
            "STATIVE_COGNITION",
            "STATIVE",
        ],
        valency_effect="NO_VALENCY_CHANGE",
        description="Telic completion, irreversible achievement, cognitive boundary transition, or inadvertent utterance; statives license context-dependent telic coercion or unexpectedness.",
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

    def assess_vector_compatibility(
        self, pole_verb: str, vector_verb: str, pole_semantic_type: str
    ) -> Dict[str, Any]:
        """
        Evaluates graded compatibility between a pole verb and an aspectual vector verb.
        Distinguishes auto-generation safety from linguistic impossibility.
        """
        v_norm = normalize_bangla_text(vector_verb)
        p_norm = normalize_bangla_text(pole_verb)

        if v_norm not in VECTOR_INVENTORY:
            return {
                "pole_verb": p_norm,
                "vector_verb": v_norm,
                "pole_semantic_type": pole_semantic_type,
                "status": VectorCompatibilityStatus.UNKNOWN,
                "auto_generation_safe": False,
                "evidence_state": "UNKNOWN",
                "reason": f"Unknown vector verb: '{vector_verb}'",
                "coercion_factors": [],
            }

        spec = VECTOR_INVENTORY[v_norm]

        if pole_semantic_type in spec.allowed_pole_types:
            return {
                "pole_verb": p_norm,
                "vector_verb": v_norm,
                "pole_semantic_type": pole_semantic_type,
                "status": VectorCompatibilityStatus.ALLOWED,
                "auto_generation_safe": True,
                "evidence_state": "VERIFIED_STANDARD",
                "reason": f"Pole type '{pole_semantic_type}' is canonically licensed with vector '{v_norm}'.",
                "coercion_factors": [],
            }

        if pole_semantic_type in spec.context_dependent_pole_types:
            return {
                "pole_verb": p_norm,
                "vector_verb": v_norm,
                "pole_semantic_type": pole_semantic_type,
                "status": VectorCompatibilityStatus.CONTEXT_DEPENDENT,
                "auto_generation_safe": False,
                "evidence_state": "NEEDS_HUMAN_REVIEW",
                "reason": (
                    f"Context-dependent vector combination: pole '{p_norm}' ({pole_semantic_type}) with vector '{v_norm}' "
                    f"requires contextual licensing/coercion (telic coercion, unexpectedness, or evaluative stance); "
                    f"not universally ungrammatical, but blocked from automatic unconstrained standard generation."
                ),
                "coercion_factors": [
                    "event_boundedness",
                    "telicity_coercion",
                    "speaker_evaluation",
                    "unexpectedness",
                    "affectedness",
                ],
            }

        return {
            "pole_verb": p_norm,
            "vector_verb": v_norm,
            "pole_semantic_type": pole_semantic_type,
            "status": VectorCompatibilityStatus.UNSUPPORTED,
            "auto_generation_safe": False,
            "evidence_state": "UNSUPPORTED",
            "reason": (
                f"Selectional restriction violation: Vector '{v_norm}' requires pole types "
                f"{spec.allowed_pole_types}, got '{pole_semantic_type}'."
            ),
            "coercion_factors": [],
        }

    def validate_vector_combination(
        self,
        pole_verb: str,
        vector_verb: str,
        pole_semantic_type: str,
        allow_context_dependent: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates whether a pole verb is selectionally compatible with a vector verb.
        By default, requires ALLOWED (auto-generation safe). If allow_context_dependent=True,
        also permits CONTEXT_DEPENDENT combinations.
        """
        assessment = self.assess_vector_compatibility(pole_verb, vector_verb, pole_semantic_type)
        status = assessment["status"]

        if status == VectorCompatibilityStatus.ALLOWED:
            return True, None

        if status == VectorCompatibilityStatus.CONTEXT_DEPENDENT:
            if allow_context_dependent:
                return True, None
            return False, assessment["reason"]

        return False, assessment["reason"]

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
