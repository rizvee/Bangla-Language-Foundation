"""
BLF Corpus Engineering and Data Processing Pipeline.

Provides reversible normalization, conservative cleaning, 4-tier deduplication,
and deterministic provenance tracking.
"""

from blf.pipeline.cleaning import ConservativeTextCleaner
from blf.pipeline.deduplication import DeduplicationTier, MultiTierDeduplicator
from blf.pipeline.manifest import PipelineManifest, PipelineRecord
from blf.pipeline.normalization import ReversibleNormalizer, TransformationStep

__all__ = [
    "ConservativeTextCleaner",
    "DeduplicationTier",
    "MultiTierDeduplicator",
    "PipelineManifest",
    "PipelineRecord",
    "ReversibleNormalizer",
    "TransformationStep",
]
