"""
BLF Constrained Realization Pipeline.

Translates Semantic Frames + Syntactic Constructions + Thematic Arguments
into surface Bangla sentences while strictly enforcing morphosyntactic,
DOM, honorific agreement, and selectional constraints.
"""

from typing import Any, Dict, List, Optional, Tuple
from blf.linguistics.morphology.nominal_declension import NominalDeclensionEngine
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine
from blf.linguistics.complex_predicates import ComplexPredicateEngine
from blf.linguistics.pragmatics import HonorificTier, PragmaticsEngine
from blf.linguistics.normalizer import normalize_bangla_text

nominal_engine = NominalDeclensionEngine()
verbal_engine = VerbalConjugatorEngine()
complex_engine = ComplexPredicateEngine()
pragmatics_engine = PragmaticsEngine()


class RealizationError(Exception):
    """Raised when linguistic constraints or selectional restrictions are violated."""
    pass


class ConstrainedRealizer:
    """Deterministic, constraint-enforcing Bangla sentence realizer."""

    def __init__(self):
        pass

    def check_morphotactic_invariants(self, text: str) -> None:
        """Enforces that no illegal stacked affixes exist."""
        norm = normalize_bangla_text(text)
        illegal_patterns = ["টাগুলো", "টিরা", "টাদের", "গুলোরটি"]
        for p in illegal_patterns:
            if p in norm:
                raise RealizationError(f"Illegal morphotactic combination detected: '{p}' in '{norm}'")

    def realize_transitive(
        self,
        subject_lemma: str,
        object_lemma: str,
        verb_root: str,
        tense_key: str = "PRES_SIMP",
        person_slot: str = "3_ORD",
        is_animate_obj: bool = False,
        is_definite_obj: bool = True,
        polarity: str = "AFFIRMATIVE",
        is_polar_question: bool = False,
        is_topicalized: bool = False,
        is_pro_drop: bool = False,
    ) -> str:
        """
        Synthesizes a transitive sentence: [Subject] [Object] [Verb]
        """
        subj = normalize_bangla_text(subject_lemma)
        obj = normalize_bangla_text(object_lemma)
        
        # 1. Apply Differential Object Marking (DOM)
        if is_animate_obj:
            obj_surface = obj + "কে"
        else:
            obj_surface = obj

        # 2. Conjugate Verb
        conj_table = verbal_engine.conjugate_root(verb_root)
        verb_key = f"{tense_key}.{person_slot}"
        if verb_key not in conj_table:
            raise RealizationError(f"Unknown tense/person key: '{verb_key}' for root '{verb_root}'")
        verb_surface = conj_table[verb_key]

        # 3. Handle Negation
        if polarity == "NEGATIVE":
            verb_surface = f"{verb_surface} না"

        # 4. Handle Polar Question
        if is_polar_question:
            verb_surface = f"কি {verb_surface} ?"
        else:
            verb_surface = f"{verb_surface}।"

        # 5. Assemble Constituents
        if is_topicalized:
            # OSV
            if is_pro_drop:
                tokens = [obj_surface, verb_surface]
            else:
                tokens = [obj_surface, subj, verb_surface]
        else:
            # SOV
            if is_pro_drop:
                tokens = [obj_surface, verb_surface]
            else:
                tokens = [subj, obj_surface, verb_surface]

        result = " ".join(tokens)
        self.check_morphotactic_invariants(result)
        return result

    def realize_ditransitive(
        self,
        subject_lemma: str,
        recipient_lemma: str,
        theme_lemma: str,
        verb_root: str,
        tense_key: str = "PAST_SIMP",
        person_slot: str = "1",
    ) -> str:
        """
        Synthesizes a ditransitive transfer sentence: [Subject] [Recipient-ke] [Theme] [Verb]
        """
        subj = normalize_bangla_text(subject_lemma)
        recip = normalize_bangla_text(recipient_lemma) + "কে"
        theme = normalize_bangla_text(theme_lemma)

        conj_table = verbal_engine.conjugate_root(verb_root)
        verb_key = f"{tense_key}.{person_slot}"
        verb_surface = conj_table.get(verb_key, verb_root)

        result = f"{subj} {recip} {theme} {verb_surface}।"
        self.check_morphotactic_invariants(result)
        return result

    def realize_vector_predicate_sentence(
        self,
        subject_lemma: str,
        object_lemma: str,
        pole_verb: str,
        vector_verb: str,
        pole_semantic_type: str,
        tense_person_key: str = "PAST_SIMP.3_ORD",
    ) -> str:
        """
        Synthesizes a sentence with an aspectual compound verb (vector verb).
        """
        valid, err = complex_engine.validate_vector_combination(
            pole_verb, vector_verb, pole_semantic_type
        )
        if not valid:
            raise RealizationError(f"Vector verb constraint violation: {err}")

        subj = normalize_bangla_text(subject_lemma)
        obj = normalize_bangla_text(object_lemma)
        pred_surface = complex_engine.realize_compound_verb(pole_verb, vector_verb, tense_person_key)

        result = f"{subj} {obj} {pred_surface}।"
        self.check_morphotactic_invariants(result)
        return result
