"""
BLF Constrained Synthetic Generation Pipeline.

Orchestrates:
  Semantic Frame -> Construction -> Lexicon with Selectional Restrictions -> Morphology -> Surface Realization
with mandatory synthetic provenance logging and tag 'SYNTHETIC_SOFTWARE_TEST_ONLY'.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional, Set, Tuple

from blf.generation.realizer import ConstrainedRealizer, RealizationError
from blf.linguistics.dom import AnimacyTier, DefinitenessTier, ObjectFeatures, SpecificityTier


class SelectionalRestrictionError(ValueError):
    """Raised when semantic arguments violate frame selectional constraints."""
    pass


@dataclass
class LexicalItem:
    lemma: str
    pos: str
    is_animate: bool = False
    is_human: bool = False
    is_edible: bool = False
    is_liquid: bool = False
    is_location: bool = False


# Baseline Lexicon with verified semantic features
DEFAULT_LEXICON: Dict[str, LexicalItem] = {
    # Humans
    "সে": LexicalItem("সে", "PRON", is_animate=True, is_human=True),
    "তিনি": LexicalItem("তিনি", "PRON", is_animate=True, is_human=True),
    "আমি": LexicalItem("আমি", "PRON", is_animate=True, is_human=True),
    "ছেলেটি": LexicalItem("ছেলেটি", "NOUN", is_animate=True, is_human=True),
    "শিক্ষক": LexicalItem("শিক্ষক", "NOUN", is_animate=True, is_human=True),
    "মা": LexicalItem("মা", "NOUN", is_animate=True, is_human=True),
    # Inanimate / Edible / Liquids / Objects
    "বই": LexicalItem("বই", "NOUN"),
    "বইটা": LexicalItem("বইটা", "NOUN"),
    "ভাত": LexicalItem("ভাত", "NOUN", is_edible=True),
    "রুটি": LexicalItem("রুটি", "NOUN", is_edible=True),
    "আম": LexicalItem("আম", "NOUN", is_edible=True),
    "জল": LexicalItem("জল", "NOUN", is_liquid=True),
    "পানি": LexicalItem("পানি", "NOUN", is_liquid=True),
    "চা": LexicalItem("চা", "NOUN", is_liquid=True),
    "পাথর": LexicalItem("পাথর", "NOUN"),
    "গাড়ি": LexicalItem("গাড়ি", "NOUN"),
}


class ConstrainedGenerationPipeline:
    """
    Generation pipeline that enforces frame selectional restrictions, anti-Cartesian product rules,
    and attaches verified provenance metadata.
    """

    def __init__(self, lexicon: Optional[Dict[str, LexicalItem]] = None) -> None:
        self.lexicon = lexicon or dict(DEFAULT_LEXICON)
        self.realizer = ConstrainedRealizer()

    def check_selectional_restrictions(
        self,
        frame_id: str,
        agent_lemma: str,
        patient_lemma: Optional[str] = None,
    ) -> None:
        agent = self.lexicon.get(agent_lemma)
        patient = self.lexicon.get(patient_lemma) if patient_lemma else None

        # Check Agent/Experiencer requirements
        if frame_id.startswith("FRAME-INGESTION") or frame_id.startswith("FRAME-COGNITION") or frame_id.startswith("FRAME-PERCEPTION"):
            if agent and not agent.is_animate:
                raise SelectionalRestrictionError(
                    f"Frame '{frame_id}' requires [+Animate] Agent/Experiencer; got '{agent_lemma}' (inanimate)."
                )

        # Check Patient/Theme requirements
        if frame_id == "FRAME-INGESTION-FOOD":
            if patient and not patient.is_edible:
                raise SelectionalRestrictionError(
                    f"Frame 'FRAME-INGESTION-FOOD' requires [+Edible] Patient; got '{patient_lemma}' (non-edible)."
                )

        if frame_id == "FRAME-INGESTION-LIQUID":
            if patient and not patient.is_liquid:
                raise SelectionalRestrictionError(
                    f"Frame 'FRAME-INGESTION-LIQUID' requires [+Liquid] Patient; got '{patient_lemma}' (non-liquid)."
                )

    def generate_synthetic_record(
        self,
        frame_id: str,
        construction_id: str,
        agent_lemma: str,
        patient_lemma: str,
        verb_root: str,
        tense_key: str = "PRES_SIMP",
        person_slot: str = "3_ORD",
        target_register: str = "COLLOQUIAL_STANDARD",
        target_dialect: str = "BDSB_STANDARD",
        polarity: str = "AFFIRMATIVE",
    ) -> Dict[str, Any]:
        """
        Generates a single synthetic record with full provenance tracking and test-only tagging.
        """
        # 1. Enforce Selectional Restrictions (Anti-Cartesian filter)
        self.check_selectional_restrictions(frame_id, agent_lemma, patient_lemma)

        # 2. Determine Object Features
        patient_item = self.lexicon.get(patient_lemma)
        is_anim = patient_item.is_animate if patient_item else False
        is_def = patient_lemma.endswith("টা") or patient_lemma.endswith("টি")
        obj_feat = ObjectFeatures(
            lemma=patient_lemma,
            animacy=AnimacyTier.HUMAN if is_anim else AnimacyTier.INANIMATE,
            definiteness=DefinitenessTier.DEFINITE if is_def else DefinitenessTier.BARE_GENERIC,
            specificity=SpecificityTier.SPECIFIC if (is_def or is_anim) else SpecificityTier.NON_SPECIFIC,
            has_classifier=is_def,
        )

        # 3. Realize Surface String
        surface_text = self.realizer.realize_transitive(
            subject_lemma=agent_lemma,
            object_lemma=patient_lemma,
            verb_root=verb_root,
            tense_key=tense_key,
            person_slot=person_slot,
            object_features=obj_feat,
            polarity=polarity,
        )

        # 4. Generate Reproducible Provenance
        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        prompt_content = f"{frame_id}|{construction_id}|{agent_lemma}|{patient_lemma}|{verb_root}|{polarity}"
        prompt_hash = hashlib.sha256(prompt_content.encode("utf-8")).hexdigest()

        provenance_metadata = {
            "source_type": "synthetic_rule",
            "generator": "BLF-ConstrainedRealizer-v1.0",
            "generation_timestamp": timestamp_str,
            "prompt_or_rule_provenance": {
                "template_id": f"RULE-GEN-{construction_id}",
                "prompt_hash": prompt_hash,
                "parameters": {
                    "verb_root": verb_root,
                    "tense_key": tense_key,
                    "person_slot": person_slot,
                    "polarity": polarity,
                },
            },
            "conditioning_inputs": {
                "semantic_frame_id": frame_id,
                "construction_id": construction_id,
                "target_register": target_register,
                "target_dialect": target_dialect,
                "lexical_constraints": [agent_lemma, patient_lemma],
            },
            "validation_methods": [
                "automated_selectional_restriction_check",
                "automated_morphotactic_invariant_check",
                "automated_dom_verification",
            ],
        }

        record = {
            "record_id": f"SYN-{prompt_hash[:12]}",
            "text": surface_text,
            "quality_tier": "SYNTHETIC",
            "provenance_class": "RULE_GENERATED",
            "execution_tag": "SYNTHETIC_SOFTWARE_TEST_ONLY",
            "provenance": provenance_metadata,
        }

        return record
