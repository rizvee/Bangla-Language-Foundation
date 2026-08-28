"""
BLF Corpus Attestation Domain Models.

Provides dataclasses and validators for empirical corpus and literature attestations,
separating schema validity from external verification status.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AttestationSourceType(str, Enum):
    SCHOLARLY_GRAMMAR = "SCHOLARLY_GRAMMAR"
    CONTEMPORARY_NEWS_PUBLIC = "CONTEMPORARY_NEWS_PUBLIC"
    GOVERNMENT_PUBLIC_PORTAL = "GOVERNMENT_PUBLIC_PORTAL"
    OPEN_ACCESS_RESEARCH_CORPUS = "OPEN_ACCESS_RESEARCH_CORPUS"
    SPOKEN_SPEECH_TRANSCRIPT = "SPOKEN_SPEECH_TRANSCRIPT"
    LITERARY_PUBLIC_DOMAIN = "LITERARY_PUBLIC_DOMAIN"


class ExactOrDerivedText(str, Enum):
    EXACT_QUOTATION = "EXACT_QUOTATION"
    SCHOLARLY_EXAMPLE_DERIVED = "SCHOLARLY_EXAMPLE_DERIVED"
    CORPUS_TOKEN_STREAM = "CORPUS_TOKEN_STREAM"
    SYNTHESIZED_MINIMAL_PAIR = "SYNTHESIZED_MINIMAL_PAIR"


class LocatorType(str, Enum):
    PAGE = "PAGE"
    PARAGRAPH = "PARAGRAPH"
    SECTION = "SECTION"
    CORPUS_RECORD = "CORPUS_RECORD"
    LINE = "LINE"
    DOCUMENT = "DOCUMENT"
    UNINDEXED_SPLIT_QUARANTINED = "UNINDEXED_SPLIT_QUARANTINED"


class AttestationVerificationMethod(str, Enum):
    INDEPENDENT_PAGE_AUDIT = "INDEPENDENT_PAGE_AUDIT"
    DIRECT_CORPUS_TOKEN_MATCH = "DIRECT_CORPUS_TOKEN_MATCH"
    METADATA_ONLY_BIBLIOGRAPHIC_LOCATOR = "METADATA_ONLY_BIBLIOGRAPHIC_LOCATOR"
    UNINDEXED_QUARANTINE = "UNINDEXED_QUARANTINE"
    HUMAN_EXPERT_VERIFIED = "HUMAN_EXPERT_VERIFIED"


class AttestationVerificationStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    PROVISIONAL = "PROVISIONAL"
    LOCATOR_VERIFIED = "LOCATOR_VERIFIED"
    TEXT_VERIFIED = "TEXT_VERIFIED"
    FEATURE_VERIFIED = "FEATURE_VERIFIED"
    HUMAN_REVIEWED = "HUMAN_REVIEWED"
    REJECTED = "REJECTED"


@dataclass
class CorpusAttestation:
    attestation_id: str
    text: str
    normalized_text: str
    source_id: str
    source_type: AttestationSourceType
    language_variety: str
    register: str
    construction_ids: List[str]
    rule_ids: List[str]
    exact_or_derived_text: ExactOrDerivedText
    locator: str
    locator_type: LocatorType
    canonical_url_or_artifact: str
    retrieval_date: str
    verification_method: AttestationVerificationMethod
    verification_status: AttestationVerificationStatus
    artifact_id: Optional[str] = None
    frame_ids: List[str] = field(default_factory=list)
    content_hash: Optional[str] = None
    metadata_hash: Optional[str] = None
    copyright_handling: str = "SHORT_EXCERPT_RESEARCH_FAIR_USE"
    gloss: Optional[str] = None
    notes: Optional[str] = None
