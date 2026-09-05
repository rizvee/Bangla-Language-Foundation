"""
Unit tests for BLF-Bench Diagnostic Probes, Contamination Checker, and Benchmark Runner.
"""

import unittest

from blf.benchmarks.contamination import ContaminationChecker, ContaminationStatus
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
        self.assertEqual(rep.incidents[0].incident_type, "RAW_EXACT_MATCH")

    def test_family_leakage_detected(self) -> None:
        train = [{"item_id": "tr_1", "sentence_family_id": "SF-100", "text": "আমি ভাত খাই।"}]
        test = [{"item_id": "te_1", "sentence_family_id": "SF-100", "text": "আমি কি ভাত খাই ?"}]
        rep = self.checker.audit(test, train)
        self.assertFalse(rep.is_clean)
        self.assertEqual(rep.incidents[0].incident_type, "FAMILY_LEAKAGE")

    def test_template_leakage_detected(self) -> None:
        train = [{"item_id": "tr_1", "semantic_template_id": "TMPL-01", "text": "আমি ভাত খাই।"}]
        test = [{"item_id": "te_1", "semantic_template_id": "TMPL-01", "text": "তুমি ফল খাও।"}]
        rep = self.checker.audit(test, train)
        self.assertFalse(rep.is_clean)
        self.assertEqual(rep.incidents[0].incident_type, "TEMPLATE_LEAKAGE")

    def test_empty_comparison_is_not_evaluable(self) -> None:
        test = [{"item_id": "te_1", "text": "কিছু পরীক্ষা বাক্য।"}]
        rep = self.checker.audit(test, [])
        self.assertEqual(rep.status, ContaminationStatus.NOT_EVALUABLE)
        self.assertIsNone(rep.is_clean)

    def test_clean_split(self) -> None:
        train = [{"item_id": "tr_1", "sentence_family_id": "SF-100", "text": "আমি ভাত খাই।"}]
        test = [{"item_id": "te_1", "sentence_family_id": "SF-200", "text": "তিনি বই পড়েন।"}]
        rep = self.checker.audit(test, train)
        self.assertTrue(rep.is_clean)
        self.assertEqual(rep.contaminated_items_count, 0)
        self.assertTrue(rep.clean_on_available_checks_only)
        self.assertFalse(rep.all_required_checks_passed)

    def test_extended_leakage_dimensions(self) -> None:
        # 1. Source Semantic Unit Leakage
        train_u = [{"item_id": "tr_u", "source_semantic_unit_id": "SU-01", "text": "বাঘটি বনে থাকে।"}]
        test_u = [{"item_id": "te_u", "source_semantic_unit_id": "SU-01", "text": "একটি ভিন্ন বাক্য।"}]
        rep_u = self.checker.audit(test_u, train_u)
        self.assertFalse(rep_u.is_clean)
        self.assertEqual(rep_u.incidents[0].incident_type, "SOURCE_UNIT_LEAKAGE")

        # 2. Near Duplicate Cluster Leakage
        train_c = [{"item_id": "tr_c", "near_duplicate_cluster_id": "NDC-99", "text": "তিনি অফিসে যান।"}]
        test_c = [{"item_id": "te_c", "near_duplicate_cluster_id": "NDC-99", "text": "সে অফিসে যায়।"}]
        rep_c = self.checker.audit(test_c, train_c)
        self.assertFalse(rep_c.is_clean)
        self.assertEqual(rep_c.incidents[0].incident_type, "NEAR_DUPLICATE_CLUSTER_LEAKAGE")

        # 3. Conversation Leakage
        train_cv = [{"item_id": "tr_cv", "conversation_id": "CONV-42", "text": "হ্যালো, কেমন আছো?"}]
        test_cv = [{"item_id": "te_cv", "conversation_id": "CONV-42", "text": "আমি ভালো আছি।"}]
        rep_cv = self.checker.audit(test_cv, train_cv)
        self.assertFalse(rep_cv.is_clean)
        self.assertEqual(rep_cv.incidents[0].incident_type, "CONVERSATION_LEAKAGE")


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
