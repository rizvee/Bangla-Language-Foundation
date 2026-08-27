"""
BLF Construction Grammar Domain Models.

Provides strongly typed dataclasses and structures for clause-level constructions,
constituent constraints, argument realization patterns, and complex predicates.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from blf.ontology.models import LanguageVariety, Productivity, ReviewStatus


class ConstructionType(str, Enum):
    DECLARATIVE_TRANSITIVE = "DECLARATIVE_TRANSITIVE"
    DECLARATIVE_INTRANSITIVE = "DECLARATIVE_INTRANSITIVE"
    DECLARATIVE_DITRANSITIVE = "DECLARATIVE_DITRANSITIVE"
    COPULAR_EQUATIVE = "COPULAR_EQUATIVE"
    EXISTENTIAL_POSSESSIVE = "EXISTENTIAL_POSSESSIVE"
    EXPERIENCER_DATIVE_SUBJECT = "EXPERIENCER_DATIVE_SUBJECT"
    POLAR_INTERROGATIVE = "POLAR_INTERROGATIVE"
    WH_INTERROGATIVE = "WH_INTERROGATIVE"
    IMPERATIVE_DIRECT = "IMPERATIVE_DIRECT"
    PROHIBITIVE_NEGATIVE = "PROHIBITIVE_NEGATIVE"
    COMPLEX_CONJUNCTIVE = "COMPLEX_CONJUNCTIVE"
    COMPLEX_CONDITIONAL = "COMPLEX_CONDITIONAL"
    COMPLEX_CORRELATIVE = "COMPLEX_CORRELATIVE"
    INFORMATION_TOPICALIZATION = "INFORMATION_TOPICALIZATION"
    INFORMATION_PRODROP = "INFORMATION_PRODROP"
    COMPLEX_PREDICATE_VECTOR = "COMPLEX_PREDICATE_VECTOR"
    COMPLEX_PREDICATE_LIGHT_VERB = "COMPLEX_PREDICATE_LIGHT_VERB"


class WordOrder(str, Enum):
    SOV = "SOV"
    SV = "SV"
    S_IO_DO_V = "S_IO_DO_V"
    OSV_TOPICAL = "OSV_TOPICAL"
    OVS_MARKED = "OVS_MARKED"
    VSO_EMPHATIC = "VSO_EMPHATIC"
    CORRELATIVE_J_T = "CORRELATIVE_J_T"
    PRO_DROP_OV = "PRO_DROP_OV"
    PRO_DROP_V = "PRO_DROP_V"


@dataclass
class LinguisticConstruction:
    construction_id: str
    name: str
    construction_type: ConstructionType
    supporting_claim_ids: List[str]
    semantic_function: str
    syntactic_pattern: str
    required_roles: List[str]
    word_order: WordOrder
    language_variety: LanguageVariety
    productivity: Productivity
    status: str
    supporting_rule_ids: List[str] = field(default_factory=list)
    optional_roles: List[str] = field(default_factory=list)
    constituent_constraints: Dict[str, Any] = field(default_factory=dict)
    register: Optional[str] = None
    polarity: str = "ANY"
    exceptions: List[str] = field(default_factory=list)
    example_ids: List[str] = field(default_factory=list)
    notes: Optional[str] = None
