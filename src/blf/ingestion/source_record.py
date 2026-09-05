"""
BLF Corpus Ingestion Data Records.

Defines strongly-typed data structures for representing external linguistic corpora
and treebanks, tracking upstream artifact provenance and granular sentence/token annotations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SourceArtifact:
    """Represents a verified external upstream repository/file artifact."""
    artifact_id: str
    source_id: str
    upstream_repository: Optional[str] = None
    upstream_commit_sha: Optional[str] = None
    file_path: Optional[str] = None
    file_sha256: Optional[str] = None
    license_expression: str = "UNKNOWN"
    license_file_sha256: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class IngestedToken:
    """Represents an individual token in a sentence (e.g. CoNLL-U 10-column token row)."""
    id: int
    form: str
    lemma: str
    upos: str
    xpos: Optional[str] = None
    feats: Dict[str, str] = field(default_factory=dict)
    head: Optional[int] = None
    deprel: Optional[str] = None
    deps: Optional[str] = None
    misc: Dict[str, str] = field(default_factory=dict)
    is_multiword: bool = False
    multiword_range: Optional[Tuple[int, int]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "form": self.form,
            "lemma": self.lemma,
            "upos": self.upos,
            "xpos": self.xpos,
            "feats": self.feats,
            "head": self.head,
            "deprel": self.deprel,
            "deps": self.deps,
            "misc": self.misc,
            "is_multiword": self.is_multiword,
            "multiword_range": self.multiword_range,
        }


@dataclass
class IngestedSentence:
    """Represents an ingested sentence with metadata and token list."""
    sentence_id: str
    document_id: Optional[str] = None
    raw_text: str = ""
    tokens: List[IngestedToken] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    source_artifact: Optional[SourceArtifact] = None

    @property
    def token_count(self) -> int:
        return len([t for t in self.tokens if not t.is_multiword])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sentence_id": self.sentence_id,
            "document_id": self.document_id,
            "raw_text": self.raw_text,
            "token_count": self.token_count,
            "metadata": self.metadata,
            "tokens": [t.to_dict() for t in self.tokens],
        }


@dataclass
class IngestedDocument:
    """Represents an ingested document containing multiple sentences."""
    document_id: str
    artifact_id: str
    source_id: str
    sentences: List[IngestedSentence] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def sentence_count(self) -> int:
        return len(self.sentences)

    @property
    def token_count(self) -> int:
        return sum(s.token_count for s in self.sentences)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "artifact_id": self.artifact_id,
            "source_id": self.source_id,
            "sentence_count": self.sentence_count,
            "token_count": self.token_count,
            "metadata": self.metadata,
            "sentences": [s.to_dict() for s in self.sentences],
        }
