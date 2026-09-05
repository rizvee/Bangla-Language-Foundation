"""
BLF Diagnostic Probes for Morphosyntactic & Semantic Phenomena.

Implements unit-level probes to evaluate linguistic capabilities on:
  1. Differential Object Marking (DOM)
  2. Complex Predicate vector verb selection
  3. Polarity & Polar question placement
  4. Honorific subject-verb agreement
  5. Nominal morphotactic classifier stacking
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from blf.linguistics.complex_predicates import ComplexPredicateEngine
from blf.linguistics.dom import AnimacyTier, DefinitenessTier, DOMEngine, ObjectFeatures, SpecificityTier
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine
from blf.linguistics.normalizer import normalize_bangla_text


class ProbeType(str, Enum):
    DOM = "DIFFERENTIAL_OBJECT_MARKING"
    COMPLEX_PREDICATE = "COMPLEX_PREDICATE"
    POLARITY = "POLARITY_AND_PARTICLES"
    HONORIFIC_AGREEMENT = "HONORIFIC_AGREEMENT"
    MORPHOTACTICS = "NOMINAL_MORPHOTACTICS"


@dataclass
class ProbeResult:
    probe_id: str
    probe_type: ProbeType
    target_sentence: str
    is_correct: bool
    expected_output: str
    predicted_output: str
    error_type: Optional[str] = None
    notes: Optional[str] = None


class BaseProbe(ABC):
    @property
    @abstractmethod
    def probe_type(self) -> ProbeType:
        pass

    @abstractmethod
    def evaluate(self, instance: Dict[str, Any]) -> ProbeResult:
        pass


class DOMProbe(BaseProbe):
    """Evaluates Differential Object Marking (-ke vs bare object)."""

    def __init__(self) -> None:
        self.dom_engine = DOMEngine()

    @property
    def probe_type(self) -> ProbeType:
        return ProbeType.DOM

    def evaluate(self, instance: Dict[str, Any]) -> ProbeResult:
        lemma = instance.get("lemma", "")
        anim = AnimacyTier(instance.get("animacy", AnimacyTier.INANIMATE.value))
        defin = DefinitenessTier(instance.get("definiteness", DefinitenessTier.BARE_GENERIC.value))
        spec = SpecificityTier.SPECIFIC if defin == DefinitenessTier.DEFINITE or anim == AnimacyTier.HUMAN else SpecificityTier.NON_SPECIFIC
        has_clf = instance.get("has_classifier", False)
        clf = instance.get("classifier")

        feat = ObjectFeatures(
            lemma=lemma,
            animacy=anim,
            definiteness=defin,
            specificity=spec,
            has_classifier=has_clf,
            classifier=clf,
        )
        decision = self.dom_engine.evaluate_dom(feat)
        expected = decision.surface_form
        predicted = instance.get("predicted_form", "")

        is_corr = (normalize_bangla_text(predicted) == normalize_bangla_text(expected))
        return ProbeResult(
            probe_id=instance.get("probe_id", "dom_probe"),
            probe_type=self.probe_type,
            target_sentence=instance.get("sentence", f"... {predicted} ..."),
            is_correct=is_corr,
            expected_output=expected,
            predicted_output=predicted,
            error_type=None if is_corr else "DOM_MARKING_MISMATCH",
        )


class ComplexPredicateProbe(BaseProbe):
    """Evaluates vector verb compatibility in complex predicates."""

    def __init__(self) -> None:
        self.engine = ComplexPredicateEngine()

    @property
    def probe_type(self) -> ProbeType:
        return ProbeType.COMPLEX_PREDICATE

    def evaluate(self, instance: Dict[str, Any]) -> ProbeResult:
        pole = instance.get("pole_verb", "")
        vector = instance.get("vector_verb", "")
        pole_type = instance.get("pole_semantic_type", "TRANSITIVE_DYNAMIC")
        is_valid, reason = self.engine.validate_vector_combination(pole, vector, pole_type)
        expected_status = "VERIFIED_COMBINATION" if is_valid else "INVALID_OR_UNKNOWN"
        predicted_status = instance.get("predicted_status", "INVALID_OR_UNKNOWN")

        is_corr = (predicted_status == expected_status)
        return ProbeResult(
            probe_id=instance.get("probe_id", "cpred_probe"),
            probe_type=self.probe_type,
            target_sentence=f"{pole} {vector}",
            is_correct=is_corr,
            expected_output=expected_status,
            predicted_output=predicted_status,
            error_type=None if is_corr else "VECTOR_SELECTION_ERROR",
        )


class PolarityProbe(BaseProbe):
    """Evaluates placement and morphology of Bengali negation."""

    def __init__(self) -> None:
        self.verbal_engine = VerbalConjugatorEngine()

    @property
    def probe_type(self) -> ProbeType:
        return ProbeType.POLARITY

    def evaluate(self, instance: Dict[str, Any]) -> ProbeResult:
        verb_root = instance.get("verb_root", "")
        tense_person = instance.get("tense_person", "PRES_SIMP.3_ORD")
        expected_neg = self.verbal_engine.conjugate_negative(verb_root, tense_person)
        predicted_neg = instance.get("predicted_negation", "")

        is_corr = (normalize_bangla_text(predicted_neg) == normalize_bangla_text(expected_neg))
        return ProbeResult(
            probe_id=instance.get("probe_id", "polarity_probe"),
            probe_type=self.probe_type,
            target_sentence=predicted_neg,
            is_correct=is_corr,
            expected_output=expected_neg,
            predicted_output=predicted_neg,
            error_type=None if is_corr else "NEGATION_SYNTAX_ERROR",
        )


class HonorificAgreementProbe(BaseProbe):
    """Evaluates subject-verb agreement across honorific tiers (tui, tumi, apni)."""

    def __init__(self) -> None:
        self.verbal_engine = VerbalConjugatorEngine()

    @property
    def probe_type(self) -> ProbeType:
        return ProbeType.HONORIFIC_AGREEMENT

    def evaluate(self, instance: Dict[str, Any]) -> ProbeResult:
        verb_root = instance.get("verb_root", "")
        tier = instance.get("person_slot", "3_ORD")
        tense_key = instance.get("tense_key", "PRES_SIMP")
        conj = self.verbal_engine.conjugate_root(verb_root)
        key = f"{tense_key}.{tier}"
        expected_verb = conj.get(key, "")
        predicted_verb = instance.get("predicted_verb", "")

        is_corr = (normalize_bangla_text(predicted_verb) == normalize_bangla_text(expected_verb))
        return ProbeResult(
            probe_id=instance.get("probe_id", "hon_probe"),
            probe_type=self.probe_type,
            target_sentence=f"[Subject] {predicted_verb}",
            is_correct=is_corr,
            expected_output=expected_verb,
            predicted_output=predicted_verb,
            error_type=None if is_corr else "HONORIFIC_AGREEMENT_MISMATCH",
        )


class MorphotacticsProbe(BaseProbe):
    """Evaluates nominal morphotactic validity (e.g. classifier stacking)."""

    @property
    def probe_type(self) -> ProbeType:
        return ProbeType.MORPHOTACTICS

    def evaluate(self, instance: Dict[str, Any]) -> ProbeResult:
        form = instance.get("form", "")
        # Genuinely ungrammatical inverted stacking
        is_invalid = "গুলোটি" in form or "গুলোরটি" in form
        expected_status = "UNGRAMMATICAL" if is_invalid else "GRAMMATICAL"
        predicted_status = instance.get("predicted_status", "GRAMMATICAL")

        is_corr = (predicted_status == expected_status)
        return ProbeResult(
            probe_id=instance.get("probe_id", "morphotactics_probe"),
            probe_type=self.probe_type,
            target_sentence=form,
            is_correct=is_corr,
            expected_output=expected_status,
            predicted_output=predicted_status,
            error_type=None if is_corr else "MORPHOTACTIC_CLASSIFIER_ERROR",
        )
