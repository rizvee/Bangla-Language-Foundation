"""
BLF Corpus Ingestion Module.

Provides provenance-preserving source adapters and standardized data structures
for external open corpora (e.g. CoNLL-U format).
"""

from blf.ingestion.source_record import (
    IngestedDocument,
    IngestedSentence,
    IngestedToken,
    SourceArtifact,
)
from blf.ingestion.conllu import CoNLLUIngestionAdapter, CoNLLUParseError

__all__ = [
    "SourceArtifact",
    "IngestedDocument",
    "IngestedSentence",
    "IngestedToken",
    "CoNLLUIngestionAdapter",
    "CoNLLUParseError",
]
