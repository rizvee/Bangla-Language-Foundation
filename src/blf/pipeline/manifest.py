"""
BLF Corpus Engineering Pipeline Manifest & Provenance Tracking.

Generates reproducible audit manifests for data processing stages:
raw -> normalized -> cleaned -> deduplicated.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PipelineRecord:
    record_id: str
    raw_text: str
    raw_sha256: str
    normalized_text: str
    normalized_sha256: str
    cleaning_metrics: Dict[str, Any]
    dedup_decision: Dict[str, Any]
    transformations_applied: List[Dict[str, Any]] = field(default_factory=list)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class PipelineManifest:
    manifest_id: str
    pipeline_version: str
    total_input_records: int = 0
    total_unique_records: int = 0
    total_duplicates_removed: int = 0
    records: List[PipelineRecord] = field(default_factory=list)
    tier_breakdown: Dict[str, int] = field(default_factory=dict)

    def add_record(self, record: PipelineRecord) -> None:
        self.records.append(record)
        self.total_input_records += 1
        tier = record.dedup_decision.get("tier", "UNKNOWN")
        is_dup = record.dedup_decision.get("is_duplicate", False)

        self.tier_breakdown[tier] = self.tier_breakdown.get(tier, 0) + 1
        if is_dup:
            self.total_duplicates_removed += 1
        else:
            self.total_unique_records += 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def save_json(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
