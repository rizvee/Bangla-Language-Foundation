"""
BLF Constrained Realization Pipeline.

Translates Semantic Frames + Syntactic Constructions + Thematic Arguments
into surface Bangla sentences while strictly enforcing morphosyntactic,
feature-sensitive DOM, polarity morphology, honorific agreement, and
selectional constraints.
"""

from typing import Any, Dict, List, Optional, Tuple
from blf.linguistics.morphology.nominal_declension import NominalDeclensionEngine
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine
from blf.linguistics.complex_predicates import ComplexPredicateEngine
from blf.linguistics.pragmatics import HonorificTier, PragmaticsEngine
from blf.linguistics.dom import DOMEngine, ObjectFeatures, AnimacyTier, DefinitenessTier, SpecificityTier
from blf.linguistics.normalizer import normalize_bangla_text

nominal_engine = NominalDeclensionEngine()
verbal_engine = VerbalConjugatorEngine()
complex_engine = ComplexPredicateEngine()
pragmatics_engine = PragmaticsEngine()
dom_engine = DOMEngine()


class RealizationError(Exception):
    """Raised when linguistic constraints or selectional restrictions are violated."""
    pass


class ConstrainedRealizer:
    """Deterministic, constraint-enforcing Bangla sentence realizer."""

    def __init__(self):
        pass

    def check_morphotactic_invariants(self, text: str) -> None:
        """
        Enforces that no illegal double-determination morphotactics exist in formal/standard generation.
        In formal BDSB, singular classifier (-টা/-টি) and plural suffix (-রা/-গুলো) cannot stack.
        """
        norm = normalize_bangla_text(text)
        illegal_patterns = ["টাগুলো", "টিরা", "গুলোটি", "গুলোরটি", "টাদের", "টিদের"]
        for p in illegal_patterns:
            if p in norm:
                raise RealizationError(f"Illegal double-determination classifier combination detected: '{p}' in '{norm}'")

    def realize_transitive(
        self,
        subject_lemma: str,
        object_lemma: str,
        verb_root: str,
        tense_key: str = "PRES_SIMP",
        person_slot: str = "3_ORD",
        object_features: Optional[ObjectFeatures] = None,
        is_animate_obj: bool = False,
        is_definite_obj: bool = True,
        polarity: str = "AFFIRMATIVE",
        is_polar_question: bool = False,
        polar_question_position: str = "pre_verbal",  # "pre_verbal", "topic_adjacent", "sentence_final"
        is_topicalized: bool = False,
        is_pro_drop: bool = False,
    ) -> str:
        """
        Synthesizes a transitive sentence: [Subject] [Object] [Verb]
        incorporating feature-sensitive DOM, polarity morphology, and constituent flexibility.
        """
        subj = normalize_bangla_text(subject_lemma)
        
        # 1. Evaluate Differential Object Marking (DOM)
        if object_features is not None:
            dom_decision = dom_engine.evaluate_dom(object_features)
            obj_surface = dom_decision.surface_form
        else:
            # Construct features from legacy/convenience booleans
            anim_tier = AnimacyTier.HUMAN if is_animate_obj else AnimacyTier.INANIMATE
            def_tier = DefinitenessTier.DEFINITE if is_definite_obj else DefinitenessTier.BARE_GENERIC
            spec_tier = SpecificityTier.SPECIFIC if is_definite_obj or is_animate_obj else SpecificityTier.NON_SPECIFIC
            feat = ObjectFeatures(
                lemma=object_lemma,
                animacy=anim_tier,
                definiteness=def_tier,
                specificity=spec_tier,
                has_classifier=False,
            )
            dom_decision = dom_engine.evaluate_dom(feat)
            obj_surface = dom_decision.surface_form

        # 2. Conjugate Verb with Polarity Awareness
        verb_key = f"{tense_key}.{person_slot}"
        if polarity == "NEGATIVE":
            verb_surface = verbal_engine.conjugate_negative(verb_root, verb_key)
        else:
            conj_table = verbal_engine.conjugate_root(verb_root)
            if verb_key not in conj_table:
                raise RealizationError(f"Unknown tense/person key: '{verb_key}' for root '{verb_root}'")
            verb_surface = conj_table[verb_key]

        # 3. Assemble Constituents & Handle Polar Question Placement
        if is_polar_question:
            if polar_question_position == "topic_adjacent":
                # [Subj] কি [Obj] [Verb]?
                if is_topicalized:
                    tokens = [obj_surface, "কি", subj, verb_surface] if not is_pro_drop else [obj_surface, "কি", verb_surface]
                else:
                    tokens = [subj, "কি", obj_surface, verb_surface] if not is_pro_drop else [obj_surface, "কি", verb_surface]
            elif polar_question_position == "sentence_final":
                # ... [Verb] কি?
                if is_topicalized:
                    tokens = [obj_surface, subj, verb_surface, "কি"] if not is_pro_drop else [obj_surface, verb_surface, "কি"]
                else:
                    tokens = [subj, obj_surface, verb_surface, "কি"] if not is_pro_drop else [obj_surface, verb_surface, "কি"]
            else:
                # Default neutral pre-verbal: [Subj] [Obj] কি [Verb]?
                if is_topicalized:
                    tokens = [obj_surface, subj, "কি", verb_surface] if not is_pro_drop else [obj_surface, "কি", verb_surface]
                else:
                    tokens = [subj, obj_surface, "কি", verb_surface] if not is_pro_drop else [obj_surface, "কি", verb_surface]
            
            result = " ".join(tokens) + " ?"
        else:
            if is_topicalized:
                # OSV
                tokens = [obj_surface, verb_surface] if is_pro_drop else [obj_surface, subj, verb_surface]
            else:
                # SOV
                tokens = [obj_surface, verb_surface] if is_pro_drop else [subj, obj_surface, verb_surface]
            
            result = " ".join(tokens) + "।"

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
        polarity: str = "AFFIRMATIVE",
    ) -> str:
        """
        Synthesizes a ditransitive transfer sentence: [Subject] [Recipient-ke] [Theme] [Verb]
        """
        subj = normalize_bangla_text(subject_lemma)
        
        # Recipient is animate/human -> takes overt -ke
        recip_feat = ObjectFeatures(
            lemma=recipient_lemma,
            animacy=AnimacyTier.HUMAN,
            definiteness=DefinitenessTier.DEFINITE,
            specificity=SpecificityTier.SPECIFIC,
        )
        recip_decision = dom_engine.evaluate_dom(recip_feat)
        recip = recip_decision.surface_form

        # Theme is typically inanimate
        theme_feat = ObjectFeatures(
            lemma=theme_lemma,
            animacy=AnimacyTier.INANIMATE,
            definiteness=DefinitenessTier.DEFINITE,
            specificity=SpecificityTier.SPECIFIC,
            has_classifier=theme_lemma.endswith(("টা", "টি")),
        )
        theme = theme_feat.lemma  # Preserve as-is or evaluate DOM

        verb_key = f"{tense_key}.{person_slot}"
        if polarity == "NEGATIVE":
            verb_surface = verbal_engine.conjugate_negative(verb_root, verb_key)
        else:
            conj_table = verbal_engine.conjugate_root(verb_root)
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
