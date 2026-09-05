"""
BLF-Bench Diagnostic Runner and Report Generator.

Orchestrates diagnostic probe execution, scores predictions against linguistic gold standards,
and produces comprehensive metric contracts without fabricating empirical model results.
"""

from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from blf.benchmarks.contamination import ContaminationChecker, ContaminationReport
from blf.benchmarks.probes import (
    BaseProbe,
    ComplexPredicateProbe,
    DOMProbe,
    HonorificAgreementProbe,
    MorphotacticsProbe,
    PolarityProbe,
    ProbeResult,
    ProbeType,
)


@dataclass
class PhenomenonScore:
    phenomenon: str
    total_evaluated: int
    correct_count: int
    accuracy: float
    error_types: Dict[str, int] = field(default_factory=dict)


@dataclass
class BenchmarkReport:
    benchmark_name: str = "BLF-Bench-Diagnostic"
    version: str = "0.1.0-scaffold"
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_probes_run: int = 0
    overall_accuracy: float = 0.0
    phenomenon_scores: Dict[str, PhenomenonScore] = field(default_factory=dict)
    probe_results: List[ProbeResult] = field(default_factory=list)
    contamination_audit: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert enums to string values
        d["probe_results"] = [
            {
                "probe_id": r.probe_id,
                "probe_type": r.probe_type.value,
                "target_sentence": r.target_sentence,
                "is_correct": r.is_correct,
                "expected_output": r.expected_output,
                "predicted_output": r.predicted_output,
                "error_type": r.error_type,
            }
            for r in self.probe_results
        ]
        return d


class BLFBenchRunner:
    """Executes diagnostic linguistic probes across registered instances."""

    def __init__(self) -> None:
        self.probes: Dict[ProbeType, BaseProbe] = {
            ProbeType.DOM: DOMProbe(),
            ProbeType.COMPLEX_PREDICATE: ComplexPredicateProbe(),
            ProbeType.POLARITY: PolarityProbe(),
            ProbeType.HONORIFIC_AGREEMENT: HonorificAgreementProbe(),
            ProbeType.MORPHOTACTICS: MorphotacticsProbe(),
        }
        self.contamination_checker = ContaminationChecker()

    def run_benchmark(
        self,
        probe_instances: List[Dict[str, Any]],
        training_reference_set: Optional[List[Dict[str, Any]]] = None,
    ) -> BenchmarkReport:
        if not probe_instances:
            return BenchmarkReport()

        results: List[ProbeResult] = []
        by_phenomenon: Dict[str, List[ProbeResult]] = defaultdict(list)

        for inst in probe_instances:
            pt_str = inst.get("probe_type")
            try:
                pt = ProbeType(pt_str)
            except (ValueError, TypeError):
                continue

            probe_engine = self.probes.get(pt)
            if probe_engine:
                res = probe_engine.evaluate(inst)
                results.append(res)
                by_phenomenon[pt.value].append(res)

        total = len(results)
        total_correct = sum(1 for r in results if r.is_correct)
        overall_acc = (total_correct / total) if total > 0 else 0.0

        phenom_scores: Dict[str, PhenomenonScore] = {}
        for p_name, p_results in by_phenomenon.items():
            p_total = len(p_results)
            p_correct = sum(1 for r in p_results if r.is_correct)
            p_acc = (p_correct / p_total) if p_total > 0 else 0.0

            err_counts: Dict[str, int] = defaultdict(int)
            for r in p_results:
                if not r.is_correct and r.error_type:
                    err_counts[r.error_type] += 1

            phenom_scores[p_name] = PhenomenonScore(
                phenomenon=p_name,
                total_evaluated=p_total,
                correct_count=p_correct,
                accuracy=p_acc,
                error_types=dict(err_counts),
            )

        contam_dict = None
        if training_reference_set:
            contam_rep = self.contamination_checker.audit(probe_instances, training_reference_set)
            contam_dict = asdict(contam_rep)

        return BenchmarkReport(
            total_probes_run=total,
            overall_accuracy=overall_acc,
            phenomenon_scores=phenom_scores,
            probe_results=results,
            contamination_audit=contam_dict,
        )
