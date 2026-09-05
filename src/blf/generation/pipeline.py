"""
BLF Constrained Synthetic Generation Pipeline.

Orchestrates:
  Semantic Frame -> Construction -> Lexicon with Selectional Restrictions -> Morphology -> Surface Realization
with mandatory synthetic provenance logging, canonical schema validation,
and strict safety tagging ('SYNTHETIC_SOFTWARE_TEST_ONLY', production_eligible=False).
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from blf.generation.realizer import ConstrainedRealizer, RealizationError
from blf.linguistics.dom import AnimacyTier, DefinitenessTier, ObjectFeatures, SpecificityTier
from blf.validation.validators import load_schema, validate_dict_against_schema


class GenerationConstraintError(ValueError):
    """Base exception for synthetic generation constraint violations or unknown inputs."""
    pass


class SelectionalRestrictionError(GenerationConstraintError):
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


# Software Test Fixture Lexicon.
# NOTE: Semantic features below are configured for deterministic software test fixtures
# and anti-Cartesian pipeline verification. They must NOT be treated as empirical ground truth.
FIXTURE_LEXICON: Dict[str, LexicalItem] = {
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

# Backward compatibility alias
DEFAULT_LEXICON = FIXTURE_LEXICON

# Canonical Bangla verb root to predicate mapping for compatibility auditing
VERB_ROOT_PREDICATE_MAP: Dict[str, List[str]] = {
    "খা": ["খাওয়া", "আহার করা", "পান করা"],
    "পান কর": ["পান করা"],
    "লিখ": ["লেখা", "রচনা করা"],
    "পড়": ["পড়া"],
    "দেখ": ["দেখা", "তাকানো"],
    "শোন": ["শোনা", "মনোযোগ দেওয়া"],
    "শুন": ["শোনা"],
    "বল": ["বলা", "কথা বলা", "জানানো"],
    "কর": ["করা", "কাজ করা", "সাহায্য করা", "পরিশ্রম করা", "সহযোগিতা করা", "রচনা করা", "আহার করা", "পান করা"],
    "যা": ["যাওয়া"],
    "আস": ["আসা", "ফিরে আসা"],
    "দে": ["দেওয়া", "উপহার দেওয়া", "মনোযোগ দেওয়া"],
    "নে": ["নেওয়া", "বিশ্রাম নেওয়া"],
    "পা": ["পাওয়া", "ভয় পাওয়া", "আনন্দ পাওয়া", "ক্ষিদে পাওয়া", "পিপাসা পাওয়া"],
    "ঘুমা": ["ঘুমানো"],
    "কিন": ["কেনা"],
    "কেন": ["কেনা"],
    "জান": ["জানা", "জানানো"],
    "ভাব": ["ভাবা", "চিন্তা করা"],
    "থাক": ["থাকা"],
    "বস": ["বসা"],
    "হাঁট": ["হাঁটা"],
    "দৌড়া": ["দৌড়ানো"],
}


def _load_ontology_entities(repo_root: Path) -> Tuple[Dict[str, Any], Dict[str, Any], Optional[Dict[str, Any]]]:
    """Loads known frames, constructions, and provenance schema from ontology repository."""
    frames_path = repo_root / "ontology" / "frames" / "core_frames.json"
    consts_path = repo_root / "ontology" / "constructions" / "constructions.json"
    schema_path = repo_root / "schemas" / "v0_1" / "synthetic_provenance.schema.json"

    frames: Dict[str, Any] = {}
    if frames_path.exists():
        with open(frames_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.get("frames", []):
                frames[item["frame_id"]] = item

    constructions: Dict[str, Any] = {}
    if consts_path.exists():
        with open(consts_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.get("constructions", []):
                constructions[item["construction_id"]] = item

    schema: Optional[Dict[str, Any]] = None
    if schema_path.exists():
        schema = load_schema(schema_path)

    return frames, constructions, schema


class ConstrainedGenerationPipeline:
    """
    Generation pipeline that enforces frame selectional restrictions, anti-Cartesian product rules,
    fails closed on unknown inputs, and attaches verified provenance metadata.
    """

    def __init__(
        self,
        lexicon: Optional[Dict[str, LexicalItem]] = None,
        repo_root: Optional[Path] = None,
        quarantined_exploratory_mode: bool = False,
    ) -> None:
        self.lexicon = lexicon or dict(FIXTURE_LEXICON)
        self.realizer = ConstrainedRealizer()
        self.quarantined_exploratory_mode = quarantined_exploratory_mode

        root = repo_root or Path(__file__).resolve().parents[3]
        self.known_frames, self.known_constructions, self.provenance_schema = _load_ontology_entities(root)

    def is_root_compatible_with_frame(self, frame_id: str, verb_root: str) -> bool:
        """Audits verb root compatibility against the frame's declared compatible predicates."""
        frame_obj = self.known_frames.get(frame_id)
        if not frame_obj:
            return False
        compatible_predicates = frame_obj.get("compatible_predicates", [])
        if not compatible_predicates:
            return True

        for pred in compatible_predicates:
            if verb_root == pred or pred.startswith(verb_root) or verb_root in pred:
                return True
            mapped = VERB_ROOT_PREDICATE_MAP.get(verb_root, [])
            if any(m in compatible_predicates or m in pred for m in mapped):
                return True
        return False

    def check_selectional_restrictions(
        self,
        frame_id: str,
        agent_lemma: str,
        patient_lemma: Optional[str] = None,
        verb_root: Optional[str] = None,
        construction_id: Optional[str] = None,
        quarantined_exploratory_mode: bool = False,
    ) -> None:
        """
        Validates selectional restrictions and fails closed on unknown entities unless
        quarantined exploratory mode is explicitly enabled.
        """
        is_exploratory = quarantined_exploratory_mode or self.quarantined_exploratory_mode

        if not is_exploratory:
            # Fail closed on unknown frame
            if self.known_frames and frame_id not in self.known_frames:
                raise GenerationConstraintError(
                    f"Unknown frame_id '{frame_id}' not found in ontology. Fail-closed."
                )

            # Fail closed on unknown construction
            if construction_id and self.known_constructions and construction_id not in self.known_constructions:
                raise GenerationConstraintError(
                    f"Unknown construction_id '{construction_id}' not found in ontology. Fail-closed."
                )

            # Fail closed on construction incompatibility with frame
            if frame_id in self.known_frames and construction_id:
                frame_obj = self.known_frames[frame_id]
                compat_consts = frame_obj.get("compatible_constructions", [])
                if compat_consts and construction_id not in compat_consts:
                    raise GenerationConstraintError(
                        f"Construction '{construction_id}' is not in compatible constructions for '{frame_id}': {compat_consts}"
                    )

            # Fail closed on unknown agent lemma
            if agent_lemma not in self.lexicon:
                raise GenerationConstraintError(
                    f"Unknown agent lemma '{agent_lemma}' not found in lexicon. Fail-closed on unverified lexicon."
                )

            # Fail closed on unknown patient lemma
            if patient_lemma and patient_lemma not in self.lexicon:
                raise GenerationConstraintError(
                    f"Unknown patient lemma '{patient_lemma}' not found in lexicon. Fail-closed on unverified lexicon."
                )

            # Fail closed on incompatible verb root
            if verb_root and self.known_frames and frame_id in self.known_frames:
                if not self.is_root_compatible_with_frame(frame_id, verb_root):
                    compat_preds = self.known_frames[frame_id].get("compatible_predicates", [])
                    raise GenerationConstraintError(
                        f"Verb root '{verb_root}' is not compatible with frame '{frame_id}' (compatible: {compat_preds})."
                    )

        agent = self.lexicon.get(agent_lemma)
        patient = self.lexicon.get(patient_lemma) if patient_lemma else None

        # Check Agent/Experiencer requirements
        if (
            frame_id.startswith("FRAME-INGESTION")
            or frame_id.startswith("FRAME-COGNITION")
            or frame_id.startswith("FRAME-PERCEPTION")
        ):
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
        seed: Optional[int] = None,
        sentence_family_id: Optional[str] = None,
        quarantined_exploratory_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Generates a single synthetic record with full provenance tracking and test-only tagging.
        Fails closed on unknown frames, constructions, lemmas, or incompatible verb roots.
        """
        is_exploratory = quarantined_exploratory_mode or self.quarantined_exploratory_mode

        # 1. Enforce Selectional Restrictions & Compatibility (Fail closed)
        self.check_selectional_restrictions(
            frame_id=frame_id,
            agent_lemma=agent_lemma,
            patient_lemma=patient_lemma,
            verb_root=verb_root,
            construction_id=construction_id,
            quarantined_exploratory_mode=is_exploratory,
        )

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
        prompt_content = f"{frame_id}|{construction_id}|{agent_lemma}|{patient_lemma}|{verb_root}|{polarity}|{seed}"
        prompt_hash = hashlib.sha256(prompt_content.encode("utf-8")).hexdigest()

        const_info = self.known_constructions.get(construction_id, {})
        rule_ids = const_info.get("supporting_rule_ids", [])
        claim_ids = const_info.get("supporting_claim_ids", [])

        provenance_metadata: Dict[str, Any] = {
            "source_type": "synthetic_rule",
            "generator": "BLF-ConstrainedRealizer-v1.0",
            "generator_version": "1.0.0",
            "generation_timestamp": timestamp_str,
            "code_sha": None,
            "config_hash": prompt_hash[:16],
            "seed": seed,
            "rule_ids": rule_ids,
            "claim_ids": claim_ids,
            "lexeme_ids": [],
            "evidence_dependencies": [],
            "sentence_family_id": sentence_family_id,
            "production_eligible": False,
            "execution_tag": "SYNTHETIC_SOFTWARE_TEST_ONLY",
            "human_review_status": "DEFERRED_PRE_HUMAN",
            "validation_results": {
                "selectional_restrictions": "PASSED",
                "morphotactic_invariants": "PASSED",
                "dom_verification": "PASSED",
            },
            "prompt_or_rule_provenance": {
                "template_id": f"RULE-GEN-{construction_id}",
                "generation_template_id": f"RULE-GEN-{construction_id}",
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

        # 5. Validate against canonical schema
        if self.provenance_schema is not None:
            valid, errors = validate_dict_against_schema(provenance_metadata, self.provenance_schema)
            if not valid:
                raise GenerationConstraintError(
                    f"Generated synthetic provenance failed schema validation: {errors}"
                )

        record = {
            "record_id": f"SYN-{prompt_hash[:12]}",
            "text": surface_text,
            "quality_tier": "SYNTHETIC",
            "provenance_class": "RULE_GENERATED",
            "execution_tag": "SYNTHETIC_SOFTWARE_TEST_ONLY",
            "production_eligible": False,
            "provenance": provenance_metadata,
        }

        return record
