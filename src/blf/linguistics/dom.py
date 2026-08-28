"""
BLF Differential Object Marking (DOM) Engine.

Evaluates semantic, pragmatic, and morphosyntactic features of direct objects in BDSB
to determine overt accusative marking (-কে) vs bare unmarked zero-case (-Ø).

Grounded in:
- Klaiman (1981): Volitionality and Animacy in Bengali
- Azad (1984): Bakkototto (Bangla Syntax)
- Thompson (2012): Bengali: A Comprehensive Grammar
- Bangla Academy (2011): Pramita Bangla Bhashar Byakaran (Vol. 2)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from blf.linguistics.normalizer import normalize_bangla_text


class AnimacyTier(str, Enum):
    HUMAN = "HUMAN"
    ANIMATE_NON_HUMAN = "ANIMATE_NON_HUMAN"
    INANIMATE = "INANIMATE"


class DefinitenessTier(str, Enum):
    DEFINITE = "DEFINITE"
    INDEFINITE = "INDEFINITE"
    BARE_GENERIC = "BARE_GENERIC"


class SpecificityTier(str, Enum):
    SPECIFIC = "SPECIFIC"
    NON_SPECIFIC = "NON_SPECIFIC"


class ReferentialityTier(str, Enum):
    REFERENTIAL = "REFERENTIAL"
    NON_REFERENTIAL = "NON_REFERENTIAL"


class FocusProminence(str, Enum):
    NEUTRAL = "NEUTRAL"
    CONTRASTIVE = "CONTRASTIVE"
    TOPICALIZED = "TOPICALIZED"


@dataclass
class ObjectFeatures:
    """Semantic and grammatical feature bundle for an object nominal."""
    lemma: str
    animacy: AnimacyTier = AnimacyTier.INANIMATE
    definiteness: DefinitenessTier = DefinitenessTier.DEFINITE
    specificity: SpecificityTier = SpecificityTier.SPECIFIC
    referentiality: ReferentialityTier = ReferentialityTier.REFERENTIAL
    prominence: FocusProminence = FocusProminence.NEUTRAL
    has_classifier: bool = False
    classifier: Optional[str] = None
    is_plural: bool = False
    is_demonstrative: bool = False


@dataclass
class DOMDecision:
    """Decision output containing synthesized surface forms, case markers, and epistemic status."""
    surface_form: str
    case_marker: str
    rule_id: str
    reason: str
    confidence: str  # HIGH, MEDIUM, LOW
    confidence_basis: str
    status: str = "CONFIRMED"
    accepted_variant: Optional[str] = None
    source_conflict: Optional[str] = None


class DOMEngine:
    """Multi-factor Differential Object Marking evaluator for BDSB."""

    def __init__(self):
        pass

    def evaluate_dom(self, features: ObjectFeatures) -> DOMDecision:
        """
        Determines the overt accusative case marker and surface string for a direct object,
        accounting for animacy, specificity, definiteness, prominence, and source conflicts.
        """
        stem = normalize_bangla_text(features.lemma)
        already_classified = stem.endswith(("টা", "টি", "গুলো", "গুলি"))
        if already_classified:
            clf = ""
        else:
            clf = features.classifier if features.has_classifier and features.classifier else ("টা" if features.has_classifier else "")

        # 1. Human Objects
        if features.animacy == AnimacyTier.HUMAN:
            # Human + Non-specific + Bare generic (e.g. ami daktar khujchi, lok pathao)
            if (
                features.specificity == SpecificityTier.NON_SPECIFIC
                and features.definiteness == DefinitenessTier.BARE_GENERIC
                and not features.has_classifier
                and not features.is_plural
            ):
                return DOMDecision(
                    surface_form=stem,
                    case_marker="Ø",
                    rule_id="RUL-DOM-HUMAN-NONSPECIFIC-BARE",
                    reason="Non-specific, non-referential human objects license bare unmarked accusative -Ø.",
                    confidence="HIGH",
                    confidence_basis="Standard descriptive consensus across BA-GRAM-2011, Thompson 2012, and Azad 1984.",
                    status="CONFIRMED",
                )

            # Human + Specific / Definite (e.g. shikkhok-ke, manush-ti-ke, manush-der-ke)
            if features.is_plural:
                base = f"{stem}দের"
                marker = "কে"
                surface = f"{base}{marker}"
            elif clf:
                base = f"{stem}{clf}"
                marker = "কে"
                surface = f"{base}{marker}"
            else:
                marker = "কে"
                surface = f"{stem}{marker}"

            return DOMDecision(
                surface_form=surface,
                case_marker="-কে",
                rule_id="RUL-DOM-HUMAN-SPECIFIC-ACC",
                reason="Specific human direct objects obligatorily take overt accusative marker -কে.",
                confidence="HIGH",
                confidence_basis="Universal consensus across all reference grammars.",
                status="CONFIRMED",
            )

        # 2. Animate Non-Human Objects (Animals)
        elif features.animacy == AnimacyTier.ANIMATE_NON_HUMAN:
            # Specific / Individualized with classifier (e.g. goru-ta-ke khawao)
            if features.specificity == SpecificityTier.SPECIFIC or features.has_classifier:
                base = f"{stem}{clf}" if clf else stem
                marker = "কে"
                return DOMDecision(
                    surface_form=f"{base}{marker}",
                    case_marker="-কে",
                    rule_id="RUL-DOM-ANIMATE-SPECIFIC-KE",
                    reason="Specific animate non-human objects taking classifier receive overt -কে.",
                    confidence="HIGH",
                    confidence_basis="Attested in BA-GRAM-2011 Vol. 2 and Thompson 2012.",
                    status="CONFIRMED",
                )
            # Generic / Non-specific (e.g. pakhi dekhchi, goru choracche)
            else:
                return DOMDecision(
                    surface_form=stem,
                    case_marker="Ø",
                    rule_id="RUL-DOM-ANIMATE-GENERIC-BARE",
                    reason="Generic animate non-human objects appear bare without overt -কে.",
                    confidence="HIGH",
                    confidence_basis="Attested in standard descriptive literature.",
                    status="CONFIRMED",
                )

        # 3. Inanimate Objects
        else:
            # Demonstratives and Contrastive/Topicalized Specific Inanimates (e.g., এটাকে, বইটাকে, চিঠিটাকে)
            is_dem = features.is_demonstrative or stem in ["এটা", "ওটা", "সেটা", "এইটা", "ওইটা"]
            is_prominent = features.prominence in [FocusProminence.CONTRASTIVE, FocusProminence.TOPICALIZED]

            if is_dem or is_prominent or (features.has_classifier and features.specificity == SpecificityTier.SPECIFIC and features.prominence != FocusProminence.NEUTRAL):
                base = f"{stem}{clf}" if clf else stem
                canonical_bare = base
                overt_form = f"{base}কে"
                return DOMDecision(
                    surface_form=canonical_bare,
                    accepted_variant=overt_form,
                    case_marker="Ø / -কে",
                    rule_id="RUL-DOM-INANIMATE-SPECIFIC-PROMINENT",
                    reason="Specific/demonstrative inanimate objects under contrastive focus or topicalization license overt -কে alongside canonical bare Ø.",
                    confidence="MEDIUM",
                    confidence_basis="Source divergence: BA-GRAM-2011 prefers bare Ø, whereas Klaiman 1981, Azad 1984, and empirical corpus data document overt -কে on specific inanimates.",
                    status="ATTESTED_CONTEXT_DEPENDENT",
                    source_conflict="Divergence between formal normative grammars (animate-only -ke) and descriptive/corpus usage (specific/contrastive inanimate -ke).",
                )

            # Definite classified in neutral context (e.g. boi-ta, chithi-ta)
            if features.has_classifier and clf:
                surface = f"{stem}{clf}"
                return DOMDecision(
                    surface_form=surface,
                    case_marker="Ø",
                    rule_id="RUL-DOM-INANIMATE-DEF-BARE",
                    reason="Definite inanimate direct objects in neutral context take classifier with zero case suffix -Ø.",
                    confidence="HIGH",
                    confidence_basis="Consensus in BA-GRAM-2011 and Thompson 2012 for neutral contexts.",
                    status="CONFIRMED",
                )
            elif features.is_plural:
                surface = f"{stem}গুলো"
                return DOMDecision(
                    surface_form=surface,
                    case_marker="Ø",
                    rule_id="RUL-DOM-INANIMATE-PL-BARE",
                    reason="Plural inanimate direct objects take plural classifier with zero case suffix -Ø.",
                    confidence="HIGH",
                    confidence_basis="Morphotactic consensus in BDSB.",
                    status="CONFIRMED",
                )
            # Bare generic (e.g. bhat, boi, pani)
            else:
                return DOMDecision(
                    surface_form=stem,
                    case_marker="Ø",
                    rule_id="RUL-DOM-INANIMATE-BARE",
                    reason="Bare generic inanimate direct objects appear unmarked with zero suffix -Ø.",
                    confidence="HIGH",
                    confidence_basis="Universal descriptive consensus.",
                    status="CONFIRMED",
                )
