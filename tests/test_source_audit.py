"""
Regression tests for claim-level source integrity and semantic verification.
"""

import json
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT_DIR / "sources" / "registry" / "sources.json"
AUDIT_LOG_PATH = ROOT_DIR / "sources" / "registry" / "source-audit.jsonl"

from scripts.audit_sources import (
    audit_single_source,
    compute_token_jaccard,
    validate_claim_level_evidence,
    validate_semantic_identifier_match,
)


class TestSourceAudit(unittest.TestCase):

    def setUp(self):
        self.assertTrue(SOURCES_PATH.is_file(), "sources.json must exist")
        with open(SOURCES_PATH, "r", encoding="utf-8") as f:
            self.registry = json.load(f)

    def test_all_registry_sources_pass_integrity_audit(self):
        """All sources currently in sources.json must pass claim-level and semantic checks."""
        sources = self.registry.get("sources", [])
        self.assertGreater(len(sources), 0)

        for src in sources:
            sid = src.get("source_id", "UNKNOWN")
            status = src.get("verification_status")
            errs = audit_single_source(src)
            self.assertEqual(
                errs, [],
                f"Source '{sid}' (status={status}) failed audit: {errs}"
            )

    def test_verified_source_requires_claim_evidence_block(self):
        """VERIFIED status must contain explicit claim-level verification bindings."""
        mock_source = {
            "source_id": "TEST-SRC-001",
            "title": "Test Source Title",
            "author_or_org": "Test Author",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2024,
            "verification_status": "VERIFIED",
            "citation": "Test Citation (2024)."
        }
        errs = validate_claim_level_evidence(mock_source)
        self.assertIn("Status is 'VERIFIED' but record lacks a 'verification' block.", errs)

    def test_generic_homepage_cannot_verify_book_metadata(self):
        """Generic organization homepage without locator cannot verify book publication fields."""
        mock_source = {
            "source_id": "TEST-BA-001",
            "title": "Test Book Title",
            "author_or_org": "Test Author",
            "source_tier": "TIER_A",
            "language": "bn",
            "year": 2012,
            "verification_status": "VERIFIED",
            "citation": "Test Citation (2012).",
            "verification": {
                "status": "VERIFIED",
                "verified_at": "2026-08-28",
                "primary_evidence": [
                    {
                        "evidence_id": "EV-GENERIC-HP",
                        "canonical_url": "https://banglaacademy.gov.bd",
                        "publisher_or_host": "Bangla Academy",
                        "evidence_type": "Organization Homepage"
                    }
                ],
                "claims": [
                    {"claim_id": "C1", "field": "title", "value": "Test", "evidence_id": "EV-GENERIC-HP", "status": "VERIFIED"},
                    {"claim_id": "C2", "field": "year", "value": 2012, "evidence_id": "EV-GENERIC-HP", "status": "VERIFIED"}
                ]
            }
        }
        errs = validate_claim_level_evidence(mock_source)
        self.assertTrue(
            any("Generic homepage" in e for e in errs),
            f"Expected generic homepage rejection, got: {errs}"
        )

    def test_banglabert_identifier_matching(self):
        """
        Tests semantic identifier resolution for BanglaBERT:
        - ACL:2022.naacl-main.185 (Offensive Span Detection) must FAIL.
        - ACL:2022.findings-naacl.98 (BanglaBERT) must PASS.
        - arXiv:2101.00204 (BanglaBERT preprint) must PASS.
        """
        # 1. False identifier NAACL 2022 main 185
        bad_banglabert = {
            "source_id": "BANGLA2B-TEST",
            "title": "BanglaBERT: Language Model Pretraining and Benchmarks for Low-Resource Language Understanding Evaluation in Bangla",
            "author_or_org": "Tahmid Hasan et al.",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2022,
            "verification_status": "VERIFIED",
            "paper_id": "ACL:2022.naacl-main.185",
            "citation": "BanglaBERT citation."
        }
        errs_bad = validate_semantic_identifier_match(bad_banglabert)
        self.assertTrue(
            any("Semantic Identifier Mismatch" in e for e in errs_bad),
            f"Expected mismatch rejection for ACL:2022.naacl-main.185, got: {errs_bad}"
        )

        # 2. Canonical identifier Findings of NAACL 2022 98
        good_banglabert = {
            "source_id": "BANGLA2B-TEST",
            "title": "BanglaBERT: Language Model Pretraining and Benchmarks for Low-Resource Language Understanding Evaluation in Bangla",
            "author_or_org": "Abhik Bhattacharjee et al.",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2022,
            "verification_status": "VERIFIED",
            "paper_id": "ACL:2022.findings-naacl.98",
            "citation": "BanglaBERT citation."
        }
        errs_good = validate_semantic_identifier_match(good_banglabert)
        self.assertEqual(errs_good, [], f"Expected clean pass for ACL:2022.findings-naacl.98, got: {errs_good}")

    def test_known_misidentifications_detected(self):
        """Tests that historical misidentified citations are detected and rejected."""
        # 1. Speech arXiv mismatch
        bad_speech = {
            "source_id": "BENGLAI-TEST",
            "title": "Bengali Common Voice Speech Dataset for Automatic Speech Recognition",
            "paper_id": "arXiv:2206.14051",
            "verification_status": "VERIFIED"
        }
        errs1 = validate_semantic_identifier_match(bad_speech)
        self.assertTrue(any("Semantic Identifier Mismatch" in e for e in errs1))

        # 2. Transliteration ACL mismatch
        bad_translit = {
            "source_id": "BANGLISH-TEST",
            "title": "BanglaTLit: A Benchmark Dataset for Back-Transliteration of Romanized Bangla",
            "paper_id": "ACL:2021.wnut-1.14",
            "verification_status": "VERIFIED"
        }
        errs2 = validate_semantic_identifier_match(bad_translit)
        self.assertTrue(any("Semantic Identifier Mismatch" in e for e in errs2))

    def test_audit_log_exists_and_valid(self):
        """Verifies that source-audit.jsonl exists and contains valid JSON lines with audit entries."""
        self.assertTrue(AUDIT_LOG_PATH.is_file(), "source-audit.jsonl must exist")
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        self.assertGreaterEqual(len(lines), 8)
        for line in lines:
            entry = json.loads(line)
            self.assertIn("audit_id", entry)
            self.assertIn("source_id", entry)
            self.assertIn("issue_type", entry)
            self.assertIn("incorrect_claim", entry)
            self.assertIn("correction", entry)


if __name__ == "__main__":
    unittest.main()
