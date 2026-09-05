"""
BLF Multi-Layer Annotation Data Specifications.

Defines schemas for:
  1. Tokenization & Morphosyntax (UPOS, FEATS, Lemma)
  2. Syntactic Dependencies (Universal Dependencies)
  3. Semantic Frames & Role Bindings
  4. Pragmatic & Discourse Acts
  5. Dialect & Linguistic Variety Flags
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TokenAnnotation:
    token_id: int
    surface: str
    start_char: int
    end_char: int
    upos: str
    lemma: str
    feats: Dict[str, str] = field(default_factory=dict)
    xpos: Optional[str] = None


@dataclass
class SyntaxAnnotation:
    token_id: int
    head_token_id: int
    deprel: str
    deps: Optional[str] = None


@dataclass
class SemanticAnnotation:
    frame_id: str
    predicate_token_id: int
    role_bindings: Dict[str, List[int]] = field(default_factory=dict)  # role_name -> [token_ids]
    notes: Optional[str] = None


@dataclass
class PragmaticAnnotation:
    dialogue_act: str
    register: str
    politeness: str
    illocutionary_force: Optional[str] = None
    information_status: Optional[str] = None


@dataclass
class DialectAnnotation:
    variety: str
    confidence: float
    dialect_features: List[str] = field(default_factory=list)


@dataclass
class LayeredAnnotationBundle:
    record_id: str
    raw_text: str
    normalized_text: str
    tokens: List[TokenAnnotation] = field(default_factory=list)
    syntax: List[SyntaxAnnotation] = field(default_factory=list)
    semantics: Optional[SemanticAnnotation] = None
    pragmatics: Optional[PragmaticAnnotation] = None
    dialect: Optional[DialectAnnotation] = None
    annotator_id: Optional[str] = None
    provenance_hash: Optional[str] = None
