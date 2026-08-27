"""
Core Data Models for BLF Entities using Standard Dataclasses.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from blf.linguistics.tags import Register, Dialect, CodeSwitchingType, QualityTier, ValidationStatus


@dataclass
class Token:
    token_id: int
    surface_form: str
    lemma: str
    pos_tag: str
    morphology: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticFrameInstance:
    frame_id: str
    frame_name: str
    roles: Dict[str, str] = field(default_factory=dict)


@dataclass
class ConstructionInstance:
    construction_id: str
    name: str
    voice: str = "active"
    word_order: str = "SOV"


@dataclass
class NamedEntity:
    entity_text: str
    label: str
    start_char: int
    end_char: int


@dataclass
class SyntheticProvenance:
    source_type: str
    generator: str
    generation_timestamp: str
    prompt_or_rule_provenance: Dict[str, Any]
    conditioning_inputs: Dict[str, Any]
    validation_methods: List[str]
    human_review: Optional[Dict[str, Any]] = None


@dataclass
class Utterance:
    utterance_id: str
    sentence_family_id: str
    raw_text: str
    normalized_text: str
    canonical_bangla: str
    english_translation: str
    register: str = Register.COLLOQUIAL_STANDARD.value
    dialect: str = Dialect.BDSB_STANDARD.value
    code_switching_type: str = CodeSwitchingType.PURE_BANGLA.value
    quality_tier: str = QualityTier.SILVER.value
    validation_status: str = ValidationStatus.PASSED.value
    transliteration_banglish: Optional[str] = None
    domain: Optional[str] = None
    intent: Optional[str] = None
    semantic_frame: Optional[SemanticFrameInstance] = None
    construction: Optional[ConstructionInstance] = None
    tokens: List[Token] = field(default_factory=list)
    polarity: str = "affirmative"
    named_entities: List[NamedEntity] = field(default_factory=list)
    difficulty_level: str = "beginner"
    source_id: Optional[str] = None
    quality_score: float = 1.0
    synthetic_provenance: Optional[SyntheticProvenance] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert utterance to dictionary, excluding None values."""
        raw = asdict(self)
        return {k: v for k, v in raw.items() if v is not None}


@dataclass
class SentenceFamily:
    sentence_family_id: str
    proposition_description: str
    semantic_frame_id: str
    canonical_utterance_id: str
    realization_utterance_ids: List[str]
    quality_tier: str = QualityTier.GOLD.value
    domain: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        raw = asdict(self)
        return {k: v for k, v in raw.items() if v is not None}
