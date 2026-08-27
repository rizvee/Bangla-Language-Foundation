"""
BLF Ontology & Linguistic Knowledge Domain Models.

Provides strongly typed dataclasses, enums, and relationship models for
evidence, claims, rules, paradigms, examples, and cross-framework terminology.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class LinguisticLevel(str, Enum):
    ORTHOGRAPHY = "ORTHOGRAPHY"
    PHONOLOGY = "PHONOLOGY"
    MORPHOLOGY = "MORPHOLOGY"
    MORPHOSYNTAX = "MORPHOSYNTAX"
    SYNTAX = "SYNTAX"
    SEMANTICS = "SEMANTICS"
    PRAGMATICS = "PRAGMATICS"
    DISCOURSE = "DISCOURSE"
    LEXICON = "LEXICON"
    TRANSLITERATION = "TRANSLITERATION"
    CODE_SWITCHING = "CODE_SWITCHING"
    DIALECT = "DIALECT"


class EpistemicClass(str, Enum):
    SOURCE_ASSERTED = "SOURCE_ASSERTED"
    BLF_NORMALIZED = "BLF_NORMALIZED"
    BLF_INFERRED = "BLF_INFERRED"
    BLF_HYPOTHESIS = "BLF_HYPOTHESIS"


class LanguageVariety(str, Enum):
    BDSB_STANDARD = "BDSB_STANDARD"
    BDSB_FORMAL = "BDSB_FORMAL"
    BDSB_COLLOQUIAL = "BDSB_COLLOQUIAL"
    BANGLADESH_CONVERSATIONAL = "BANGLADESH_CONVERSATIONAL"
    WEST_BENGAL_STANDARD = "WEST_BENGAL_STANDARD"
    REGIONAL = "REGIONAL"
    HISTORICAL = "HISTORICAL"
    CROSS_VARIETY = "CROSS_VARIETY"
    UNKNOWN = "UNKNOWN"


class Productivity(str, Enum):
    FULLY_PRODUCTIVE = "FULLY_PRODUCTIVE"
    HIGHLY_PRODUCTIVE = "HIGHLY_PRODUCTIVE"
    RESTRICTED = "RESTRICTED"
    LEXICALLY_CONDITIONED = "LEXICALLY_CONDITIONED"
    IDIOSYNCRATIC = "IDIOSYNCRATIC"
    HISTORICAL = "HISTORICAL"
    UNKNOWN = "UNKNOWN"


class Grammaticality(str, Enum):
    GRAMMATICAL = "GRAMMATICAL"
    UNGRAMMATICAL = "UNGRAMMATICAL"
    MARKED = "MARKED"
    ARCHAIC = "ARCHAIC"
    UNNATURAL = "UNNATURAL"
    REGISTER_MISMATCH = "REGISTER_MISMATCH"
    DIALECT_SPECIFIC = "DIALECT_SPECIFIC"
    SEMANTICALLY_INVALID = "SEMANTICALLY_INVALID"


class ProvenanceClass(str, Enum):
    SOURCE_EXAMPLE = "SOURCE_EXAMPLE"
    PUBLIC_DOMAIN_EXAMPLE = "PUBLIC_DOMAIN_EXAMPLE"
    HUMAN_CREATED = "HUMAN_CREATED"
    RULE_GENERATED = "RULE_GENERATED"
    MODEL_GENERATED = "MODEL_GENERATED"


class ReviewStatus(str, Enum):
    AUTO_EXTRACTED = "AUTO_EXTRACTED"
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    LINGUIST_REVIEW_REQUIRED = "LINGUIST_REVIEW_REQUIRED"
    HUMAN_APPROVED = "HUMAN_APPROVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class RuleRelationType(str, Enum):
    SUPPORTS = "SUPPORTS"
    REFINES = "REFINES"
    CONTRADICTS = "CONTRADICTS"
    LIMITS = "LIMITS"
    SUPERSEDES = "SUPERSEDES"
    HISTORICAL_VARIANT = "HISTORICAL_VARIANT"
    TERMINOLOGY_EQUIVALENT = "TERMINOLOGY_EQUIVALENT"


class MappingType(str, Enum):
    EXACT_EQUIVALENT = "EXACT_EQUIVALENT"
    BROADER_CONCEPT = "BROADER_CONCEPT"
    NARROWER_CONCEPT = "NARROWER_CONCEPT"
    PARTIAL_OVERLAP = "PARTIAL_OVERLAP"
    FRAMEWORK_SPECIFIC = "FRAMEWORK_SPECIFIC"


@dataclass
class LinguisticEvidence:
    evidence_id: str
    source_id: str
    evidence_type: str
    locator: str
    page_or_section: str
    excerpt_or_paraphrase: str
    copyright_handling: str
    verification_status: str
    artifact_id: Optional[str] = None
    content_hash: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class LinguisticClaim:
    claim_id: str
    evidence_ids: List[str]
    linguistic_level: LinguisticLevel
    claim_type: str
    source_assertion: str
    normalized_claim: str
    epistemic_class: EpistemicClass
    language_variety: LanguageVariety
    confidence: str
    verification_status: str
    human_review_status: ReviewStatus
    register: Optional[str] = None
    scope: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class RuleException:
    exception_type: str
    description: str
    examples: List[str] = field(default_factory=list)


@dataclass
class LinguisticRule:
    rule_id: str
    supporting_claim_ids: List[str]
    rule_type: str
    structural_pattern: str
    language_variety: LanguageVariety
    productivity: Productivity
    confidence: str
    status: str
    input_conditions: Dict[str, Any] = field(default_factory=dict)
    morphological_features: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    output_relation: Optional[str] = None
    register: Optional[str] = None
    exceptions: List[RuleException] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class LinguisticExample:
    example_id: str
    text: str
    normalized_text: str
    language_variety: LanguageVariety
    grammaticality: Grammaticality
    naturalness_status: str
    provenance: Dict[str, Any]
    review_status: ReviewStatus
    rule_ids: List[str] = field(default_factory=list)
    claim_ids: List[str] = field(default_factory=list)
    evidence_id: Optional[str] = None
    gloss_en: Optional[str] = None
    register: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class TerminologyMapping:
    mapping_id: str
    source_term: str
    source_term_bn: str
    source_id: str
    canonical_term: str
    canonical_category: str
    mapping_type: MappingType
    confidence: str
    source_definition: Optional[str] = None
    ud_equivalent: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class RuleRelation:
    relation_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: RuleRelationType
    description: str
    recorded_by: str
    confidence: str


@dataclass
class Paradigm:
    paradigm_id: str
    category: str
    lemma: str
    pos: str
    dimensions: List[str]
    cells: Dict[str, str]
    supporting_claim_ids: List[str]
    variety: LanguageVariety
    status: str


@dataclass
class ConstructionPattern:
    construction_id: str
    name: str
    syntactic_frame: str
    semantic_function: str
    slots: List[Dict[str, Any]]
    supporting_rule_ids: List[str]
    variety: LanguageVariety
    productivity: Productivity
