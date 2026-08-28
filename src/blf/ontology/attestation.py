"""
BLF Corpus Attestation Domain Models.

Provides dataclasses and validators for empirical corpus attestations
linking real-world usage excerpts to linguistic rules, constructions, and frames.
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


class AttestationStatus(str, Enum):
    VERIFIED_EMPIRICAL = "VERIFIED_EMPIRICAL"
    CROSS_VALIDATED = "CROSS_VALIDATED"
    PROVISIONAL_SAMPLE = "PROVISIONAL_SAMPLE"
    ARCHIVAL_NOTE = "ARCHIVAL_NOTE"


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
    frame_ids: List[str] = field(default_factory=list)
    source_locator: Optional[str] = None
    copyright_handling: str = "SHORT_EXCERPT_RESEARCH_FAIR_USE"
    attestation_status: AttestationStatus = AttestationStatus.VERIFIED_EMPIRICAL
    gloss: Optional[str] = None
    notes: Optional[str] = None
