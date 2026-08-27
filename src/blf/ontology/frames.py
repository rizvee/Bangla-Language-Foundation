"""
BLF Semantic Frames Domain Models.

Provides strongly typed dataclasses and structures for FrameNet-style semantic
frames, thematic role sets, selectional constraints, and predicate mappings.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SemanticRole(str, Enum):
    AGENT = "AGENT"
    EXPERIENCER = "EXPERIENCER"
    PATIENT = "PATIENT"
    THEME = "THEME"
    RECIPIENT = "RECIPIENT"
    BENEFICIARY = "BENEFICIARY"
    SOURCE = "SOURCE"
    GOAL = "GOAL"
    LOCATION = "LOCATION"
    TIME = "TIME"
    MANNER = "MANNER"
    INSTRUMENT = "INSTRUMENT"
    CAUSE = "CAUSE"
    STIMULUS = "STIMULUS"
    CONTENT = "CONTENT"
    ATTRIBUTE = "ATTRIBUTE"
    POSSESSOR = "POSSESSOR"


class FrameType(str, Enum):
    CORE_COMMUNICATION = "CORE_COMMUNICATION"
    EVERYDAY_EVENT = "EVERYDAY_EVENT"
    STATIVE_RELATIONAL = "STATIVE_RELATIONAL"
    COGNITIVE_EXPERIENCE = "COGNITIVE_EXPERIENCE"
    PHYSICAL_ACTION = "PHYSICAL_ACTION"
    SOCIAL_INTERACTION = "SOCIAL_INTERACTION"


class FrameRelationType(str, Enum):
    INHERITS = "INHERITS"
    SUBFRAME_OF = "SUBFRAME_OF"
    CAUSES = "CAUSES"
    PRECEDES = "PRECEDES"
    OPPOSES = "OPPOSES"
    RELATED_TO = "RELATED_TO"


@dataclass
class SemanticFrame:
    frame_id: str
    frame_name: str
    frame_definition: str
    frame_type: FrameType
    core_roles: List[SemanticRole]
    compatible_constructions: List[str]
    compatible_predicates: List[str]
    status: str
    optional_roles: List[SemanticRole] = field(default_factory=list)
    selectional_constraints: Dict[str, Any] = field(default_factory=dict)
    frame_relations: List[Dict[str, str]] = field(default_factory=list)
    notes: Optional[str] = None
