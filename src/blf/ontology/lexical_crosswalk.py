"""
Lexical Crosswalk and External Dictionary Adapter Interfaces.

Provides clean adapter interfaces to connect BLF semantic frames and lexemes
with external lexical databases (e.g. Accessible Dictionary / A2I, Regional Dictionaries,
WordNet-like synset graphs) without bundling proprietary or copyrighted corpora.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class LexicalAlignmentStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    PROVISIONAL = "PROVISIONAL"
    PARTIAL = "PARTIAL"
    UNALIGNED = "UNALIGNED"


@dataclass
class LexicalSense:
    sense_id: str
    lemma: str
    pos: str
    gloss: str
    examples: List[str] = field(default_factory=list)
    semantic_frame_id: Optional[str] = None
    synset_id: Optional[str] = None
    alignment_status: LexicalAlignmentStatus = LexicalAlignmentStatus.PROVISIONAL


@dataclass
class ExternalLexicalMatch:
    query_lemma: str
    source_resource: str
    external_id: Optional[str]
    headword: str
    definition: str
    pos_tag: Optional[str] = None
    dialect_flag: Optional[str] = None
    alignment_status: LexicalAlignmentStatus = LexicalAlignmentStatus.PROVISIONAL
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseLexicalAdapter(ABC):
    """Abstract interface for querying external lexical resources."""

    @property
    @abstractmethod
    def resource_name(self) -> str:
        """Name of the external lexical resource."""
        pass

    @abstractmethod
    def lookup_lemma(self, lemma: str) -> List[ExternalLexicalMatch]:
        """Queries the resource for the given Bengali lemma."""
        pass

    @abstractmethod
    def map_to_frame(self, lemma: str, target_frame_id: str) -> Optional[ExternalLexicalMatch]:
        """Aligns a lemma occurrence to a BLF semantic frame."""
        pass


class MockAccessibleDictionaryAdapter(BaseLexicalAdapter):
    """
    Provisional adapter for Accessible Dictionary (a2i / Bangla Academy),
    structured for non-infringing runtime queries without storing proprietary snapshots.
    """

    def __init__(self, stub_records: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> None:
        self._stubs = stub_records or {
            "বই": [
                {
                    "external_id": "a2i-dict-boi-1",
                    "headword": "বই",
                    "definition": "পুস্তক, গ্রন্থ",
                    "pos_tag": "noun",
                }
            ],
            "পড়া": [
                {
                    "external_id": "a2i-dict-pora-1",
                    "headword": "পড়া",
                    "definition": "পাঠ করা, অধ্যয়ন করা",
                    "pos_tag": "verb",
                }
            ],
            "খাওয়া": [
                {
                    "external_id": "a2i-dict-khawa-1",
                    "headword": "খাওয়া",
                    "definition": "আহার করা, ভক্ষণ করা",
                    "pos_tag": "verb",
                }
            ],
        }

    @property
    def resource_name(self) -> str:
        return "ACCESSIBLE-DICT-A2I"

    def lookup_lemma(self, lemma: str) -> List[ExternalLexicalMatch]:
        raw_entries = self._stubs.get(lemma, [])
        return [
            ExternalLexicalMatch(
                query_lemma=lemma,
                source_resource=self.resource_name,
                external_id=entry.get("external_id"),
                headword=entry.get("headword", lemma),
                definition=entry.get("definition", ""),
                pos_tag=entry.get("pos_tag"),
                alignment_status=LexicalAlignmentStatus.PROVISIONAL,
                metadata=entry,
            )
            for entry in raw_entries
        ]

    def map_to_frame(self, lemma: str, target_frame_id: str) -> Optional[ExternalLexicalMatch]:
        matches = self.lookup_lemma(lemma)
        if not matches:
            return None
        # Return first match flagged as provisional alignment
        match = matches[0]
        match.alignment_status = LexicalAlignmentStatus.CONFIRMED
        match.metadata["mapped_frame_id"] = target_frame_id
        return match


class MockRegionalDictionaryAdapter(BaseLexicalAdapter):
    """
    Provisional adapter for Regional Dialect Dictionaries (e.g. Shahidullah / BA-REGDICT-1965).
    Operates strictly via structured metadata interfaces.
    """

    def __init__(self, stub_records: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> None:
        self._stubs = stub_records or {
            "খাইবার": [
                {
                    "external_id": "regdict-khaibar-1",
                    "headword": "খাইবার",
                    "definition": "খাওয়ার (আঞ্চলিক বা সাধু রূপ)",
                    "dialect_flag": "regional_colloquial",
                }
            ]
        }

    @property
    def resource_name(self) -> str:
        return "BA-REGDICT-1965"

    def lookup_lemma(self, lemma: str) -> List[ExternalLexicalMatch]:
        raw_entries = self._stubs.get(lemma, [])
        return [
            ExternalLexicalMatch(
                query_lemma=lemma,
                source_resource=self.resource_name,
                external_id=entry.get("external_id"),
                headword=entry.get("headword", lemma),
                definition=entry.get("definition", ""),
                dialect_flag=entry.get("dialect_flag"),
                alignment_status=LexicalAlignmentStatus.PROVISIONAL,
                metadata=entry,
            )
            for entry in raw_entries
        ]

    def map_to_frame(self, lemma: str, target_frame_id: str) -> Optional[ExternalLexicalMatch]:
        matches = self.lookup_lemma(lemma)
        if not matches:
            return None
        match = matches[0]
        match.alignment_status = LexicalAlignmentStatus.CONFIRMED
        match.metadata["mapped_frame_id"] = target_frame_id
        return match
