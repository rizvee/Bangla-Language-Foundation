"""
Unit tests for BLF-Bench Diagnostic Probes, Contamination Checker, and Benchmark Runner.
"""

import unittest

from blf.benchmarks.contamination import ContaminationChecker
from blf.benchmarks.probes import (
    ComplexPredicateProbe,
    DOMProbe,
    HonorificAgreementProbe,
    MorphotacticsProbe,
    PolarityProbe,
    ProbeType,
)
from blf.benchmarks.runner import BLFBenchRunner


class TestBenchmarkProbes(unittest.TestCase):

    def test_dom_probe_evaluation(self) -> None:
        probe = DOMProbe()
        inst = {
            "probe_id": "dom_01",
            "lemma": "ছেলেটি",
            "animacy": "HUMAN",
            "definiteness": "DEFINITE",
            "predicted_form": "ছেলেটিকে",
        }
        res = probe.evaluate(inst)
        self.assertTrue(res.is_correct)
        self.assertEqual(res.expected_output, "ছেলেটিকে")

    def test_complex_predicate_probe_evaluation(self) -> None:
        probe = ComplexPredicateProbe()
        inst = {
            "probe_id": "cp_01",
            "pole_verb": "ফেলে",
            "vector_verb": "দেওয়া",
            "pole_semantic_type": "RELEASE_ACTION",
            "predicted_status": "VERIFIED_COMBINATION",
        }
        res = probe.evaluate(inst)
        self.assertTrue(res.is_correct)

    def test_honorific_agreement_probe_evaluation(self) -> None:
        probe = HonorificAgreementProbe()
        # Apni / Tini requires 'poden'
        inst = {
            "probe_id": "hon_01",
            "verb_root": "পড়",
            "tense_key": "PRES_SIMP",
            "person_slot": "3_HON",
            "predicted_verb": "পড়েন",
        }
        res = probe.evaluate(inst)
        self.assertTrue(res.is_correct)

    def test_morphotactics_probe_inverted_stacking(self) -> None:
        probe = MorphotacticsProbe()
        inst = {
            "probe_id": "morph_01",
            "form": "বইগুলোটি",
            "predicted_status": "UNGRAMMATICAL",
        }
        res = probe.evaluate(inst)
        self.assertTrue(res.is_correct)
        self.assertEqual(res.expected_output, "UNGRAMMATICAL")


class TestContaminationChecker(unittest.TestCase):

    def setUp(self) -> None:
        self.checker = ContaminationChecker(ngram_size=4)

    def test_exact_match_detected(self) -> None:
        train = [{"item_id": "tr_1", "text": "তিনি প্রতিদিন সকালে হাঁটেন।"}]
        test = [{"item_id": "te_1", "text": "তিনি প্রতিদিন সকালে হাঁটেন।"}]
        rep = self.checker.audit(test, train)
        self.assertFalse(rep.is_clean)
        self.assertEqual(rep.contaminated_items_count, 1)
        self.assertEqual(rep.incidents[0].incident_type, "EXACT_MATCH")

    def test_family_leakage_detected(self) -> None:
        train = [{"item_id": "tr_1", "sentence_family_id": "SF-100", "text": "আমি ভাত খাই।"}]
        test = [{"item_id": "te_1", "sentence_family_id": "SF-100", "text": "আমি কি ভাত খাই ?"}]
        rep = self.checker.audit(test, train)
        self.assertFalse(rep.is_clean)
        self.assertEqual(rep.incidents[0].incident_type, "FAMILY_LEAKAGE")

    def test_clean_split(self) -> None:
        train = [{"item_id": "tr_1", "sentence_family_id": "SF-100", "text": "আমি ভাত খাই।"}]
        test = [{"item_id": "te_1", "sentence_family_id": "SF-200", "text": "তিনি বই পড়েন।"}]
        rep = self.checker.audit(test, train)
        self.assertTrue(rep.is_clean)
        self.assertEqual(rep.contaminated_items_count, 0)


class TestBenchmarkRunner(unittest.TestCase):

    def test_runner_execution(self) -> None:
        runner = BLFBenchRunner()
        instances = [
            {
                "probe_id": "p1",
                "probe_type": ProbeType.DOM.value,
                "lemma": "ছেলেটি",
                "animacy": "HUMAN",
                "definiteness": "DEFINITE",
                "predicted_form": "ছেলেটিকে",
            },
            {
                "probe_id": "p2",
                "probe_type": ProbeType.MORPHOTACTICS.value,
                "form": "বইগুলোটি",
                "predicted_status": "UNGRAMMATICAL",
            },
        ]
        report = runner.run_benchmark(instances)
        self.assertEqual(report.total_probes_run, 2)
        self.assertEqual(report.overall_accuracy, 1.0)
        self.assertIn(ProbeType.DOM.value, report.phenomenon_scores)


if __name__ == "__main__":
    unittest.main()
