"""
Regression tests for claim-level source integrity, semantic verification, and artifact licensing.
"""

import json
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT_DIR / "sources" / "registry" / "sources.json"
AUDIT_LOG_PATH = ROOT_DIR / "sources" / "registry" / "source-audit.jsonl"

from scripts.audit_sources import (
    audit_single_source,
    compute_author_overlap,
    compute_token_jaccard,
    validate_claim_and_locator_integrity,
    validate_semantic_and_authorship_match,
)


class TestSourceAudit(unittest.TestCase):

    def setUp(self):
        self.assertTrue(SOURCES_PATH.is_file(), "sources.json must exist")
        with open(SOURCES_PATH, "r", encoding="utf-8") as f:
            self.registry = json.load(f)

    def test_all_registry_sources_pass_integrity_audit(self):
        """All sources currently in sources.json must pass claim-level, semantic, and artifact licensing checks."""
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
        errs = validate_claim_and_locator_integrity(mock_source)
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
        errs = validate_claim_and_locator_integrity(mock_source)
        self.assertTrue(
            any("Generic homepage" in e for e in errs),
            f"Expected generic homepage rejection, got: {errs}"
        )

    def test_synthetic_locator_rejected(self):
        """Synthetic or non-resolvable locator strings must be rejected."""
        mock_source = {
            "source_id": "TEST-BA-002",
            "title": "Test Book Title",
            "author_or_org": "Test Author",
            "source_tier": "TIER_A",
            "language": "bn",
            "year": 2016,
            "verification_status": "VERIFIED",
            "citation": "Test Citation (2016).",
            "verification": {
                "status": "VERIFIED",
                "verified_at": "2026-08-28",
                "primary_evidence": [
                    {
                        "evidence_id": "EV-SYNTH-LOC",
                        "canonical_url": "https://banglaacademy.gov.bd",
                        "publisher_or_host": "Bangla Academy",
                        "evidence_type": "Rulebook",
                        "locator": "Official Gazette / Publication Catalogue Code 1845"
                    }
                ],
                "claims": [
                    {"claim_id": "C1", "field": "title", "value": "Test", "evidence_id": "EV-SYNTH-LOC", "status": "VERIFIED"},
                    {"claim_id": "C2", "field": "year", "value": 2016, "evidence_id": "EV-SYNTH-LOC", "status": "VERIFIED"}
                ]
            }
        }
        errs = validate_claim_and_locator_integrity(mock_source)
        self.assertTrue(
            any("synthetic locator rejected" in e for e in errs),
            f"Expected synthetic locator rejection, got: {errs}"
        )

    def test_banglabert_identifier_and_license_matching(self):
        """
        Tests semantic identifier resolution and license matching for BanglaBERT:
        - ACL:2022.naacl-main.185 (Offensive Span Detection) must FAIL.
        - ACL:2022.findings-naacl.98 (BanglaBERT) with CC-BY-NC-4.0 must FAIL license check.
        - ACL:2022.findings-naacl.98 (BanglaBERT) with CC-BY-NC-SA-4.0 must PASS.
        """
        # 1. False identifier NAACL 2022 main 185
        bad_banglabert_id = {
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
        errs_bad_id = validate_semantic_and_authorship_match(bad_banglabert_id)
        self.assertTrue(any("Semantic Identifier Mismatch" in e for e in errs_bad_id))

        # 2. Canonical identifier but non-ShareAlike license
        bad_license = {
            "source_id": "BANGLA2B-TEST",
            "title": "BanglaBERT: Language Model Pretraining and Benchmarks for Low-Resource Language Understanding Evaluation in Bangla",
            "author_or_org": "Abhik Bhattacharjee, Tahmid Hasan, Wasi Ahmad, Kazi Samin Mubasshir, Md Saiful Islam, Anindya Iqbal, M. Sohel Rahman, Rifat Shahriyar",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2022,
            "verification_status": "VERIFIED",
            "paper_id": "ACL:2022.findings-naacl.98",
            "license": "CC-BY-NC-4.0",
            "citation": "BanglaBERT citation."
        }
        errs_bad_lic = validate_semantic_and_authorship_match(bad_license)
        self.assertTrue(any("License Mismatch" in e for e in errs_bad_lic))

        # 3. Canonical identifier and canonical CC-BY-NC-SA-4.0 license
        good_banglabert = {
            "source_id": "BANGLA2B-TEST",
            "title": "BanglaBERT: Language Model Pretraining and Benchmarks for Low-Resource Language Understanding Evaluation in Bangla",
            "author_or_org": "Abhik Bhattacharjee, Tahmid Hasan, Wasi Ahmad, Kazi Samin Mubasshir, Md Saiful Islam, Anindya Iqbal, M. Sohel Rahman, Rifat Shahriyar",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2022,
            "verification_status": "VERIFIED",
            "paper_id": "ACL:2022.findings-naacl.98",
            "license": "CC-BY-NC-SA-4.0",
            "citation": "BanglaBERT citation."
        }
        errs_good = validate_semantic_and_authorship_match(good_banglabert)
        self.assertEqual(errs_good, [])

    def test_banglanmt_authorship_and_license_matching(self):
        """
        Tests authorship contamination detection and license matching for BanglaNMT:
        - Contaminated author list (with foreign authors) must FAIL.
        - Misattributed author list (e.g. Md Saiful Islam replacing Masum Hasan & Madhusudan Basak) must FAIL.
        - Canonical author list from ACL:2020.emnlp-main.207 with CC-BY-NC-SA-4.0 must PASS.
        - Incorrect license (CC-BY-NC-4.0) must FAIL.
        """
        # 1. Contaminated author list with foreign co-authors
        contaminated_banglanmt = {
            "source_id": "BANGLANMT-TEST",
            "title": "Not Low-Resource Anymore: Aligner Ensembling, Batch Filtering, and New Datasets for Bengali-English Machine Translation",
            "author_or_org": "Tahmid Hasan, Abhik Bhattacharjee, Kazi Mubasshir, Md Saiful Islam, Yuan-Fang Li, Yong-Bin Kang, M. Sohel Rahman, Rifat Shahriyar",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2020,
            "verification_status": "VERIFIED",
            "paper_id": "ACL:2020.emnlp-main.207",
            "license": "CC-BY-NC-SA-4.0",
            "citation": "BanglaNMT citation."
        }
        errs_contam = validate_semantic_and_authorship_match(contaminated_banglanmt)
        self.assertTrue(
            any("Authorship Contamination" in e for e in errs_contam),
            f"Expected authorship contamination rejection, got: {errs_contam}"
        )

        # 2. Misattributed author list (Md Saiful Islam instead of Masum Hasan & Madhusudan Basak)
        misattributed_banglanmt = {
            "source_id": "BANGLANMT-TEST",
            "title": "Not Low-Resource Anymore: Aligner Ensembling, Batch Filtering, and New Datasets for Bengali-English Machine Translation",
            "author_or_org": "Tahmid Hasan, Abhik Bhattacharjee, Kazi Samin, Md Saiful Islam, M. Sohel Rahman, and Rifat Shahriyar",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2020,
            "verification_status": "VERIFIED",
            "paper_id": "ACL:2020.emnlp-main.207",
            "license": "CC-BY-NC-SA-4.0",
            "citation": "BanglaNMT citation."
        }
        errs_misattr = validate_semantic_and_authorship_match(misattributed_banglanmt)
        self.assertTrue(
            any("Authorship Contamination" in e for e in errs_misattr),
            f"Expected authorship contamination rejection for Md Saiful Islam replacement, got: {errs_misattr}"
        )

        # 3. Canonical authors from ACL:2020.emnlp-main.207 with correct license
        clean_banglanmt = {
            "source_id": "BANGLANMT-TEST",
            "title": "Not Low-Resource Anymore: Aligner Ensembling, Batch Filtering, and New Datasets for Bengali-English Machine Translation",
            "author_or_org": "Tahmid Hasan, Abhik Bhattacharjee, Kazi Samin, Masum Hasan, Madhusudan Basak, M. Sohel Rahman, and Rifat Shahriyar",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2020,
            "verification_status": "VERIFIED",
            "paper_id": "ACL:2020.emnlp-main.207",
            "license": "CC-BY-NC-SA-4.0",
            "citation": "BanglaNMT citation."
        }
        errs_clean = validate_semantic_and_authorship_match(clean_banglanmt)
        self.assertEqual(errs_clean, [])

    def test_banglanmt_canonical_authors_match_acl_anthology(self):
        """Regression test: Canonical author set for ACL:2020.emnlp-main.207 must match authoritative EMNLP 2020 publication."""
        from scripts.audit_sources import CANONICAL_METADATA_SNAPSHOTS
        canonical_snap = CANONICAL_METADATA_SNAPSHOTS.get("ACL:2020.emnlp-main.207")
        self.assertIsNotNone(canonical_snap)
        expected_authors = [
            "Tahmid Hasan",
            "Abhik Bhattacharjee",
            "Kazi Samin",
            "Masum Hasan",
            "Madhusudan Basak",
            "M. Sohel Rahman",
            "Rifat Shahriyar"
        ]
        self.assertEqual(canonical_snap["authors"], expected_authors)

    def test_bnsentmix_license_matching(self):
        """
        Tests license validation for BnSentMix:
        - MIT must FAIL (canonical repository is Apache-2.0).
        - Apache-2.0 must PASS.
        """
        bad_bnsentmix = {
            "source_id": "BNSENTMIX-TEST",
            "title": "BnSentMix: A Diverse Bengali-English Code-Mixed Dataset for Sentiment Analysis",
            "author_or_org": "Sadia Alam, Md Farhan Ishmam, Navid Hasin Alvee, Md Shahnewaz Siddique, Md Azam Hossain, Abu Raihan Mostofa Kamal",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2025,
            "verification_status": "VERIFIED",
            "paper_id": "ACL:2025.loreslm-1.4",
            "license": "MIT",
            "citation": "BnSentMix citation."
        }
        errs_bad = validate_semantic_and_authorship_match(bad_bnsentmix)
        self.assertTrue(any("License Mismatch" in e for e in errs_bad))

        good_bnsentmix = {
            "source_id": "BNSENTMIX-TEST",
            "title": "BnSentMix: A Diverse Bengali-English Code-Mixed Dataset for Sentiment Analysis",
            "author_or_org": "Sadia Alam, Md Farhan Ishmam, Navid Hasin Alvee, Md Shahnewaz Siddique, Md Azam Hossain, Abu Raihan Mostofa Kamal",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2025,
            "verification_status": "VERIFIED",
            "paper_id": "ACL:2025.loreslm-1.4",
            "license": "Apache-2.0",
            "citation": "BnSentMix citation."
        }
        errs_good = validate_semantic_and_authorship_match(good_bnsentmix)
        self.assertEqual(errs_good, [])

    def test_audit_log_exists_and_valid(self):
        """Verifies that source-audit.jsonl exists and contains valid JSON lines with audit entries."""
        self.assertTrue(AUDIT_LOG_PATH.is_file(), "source-audit.jsonl must exist")
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        self.assertGreaterEqual(len(lines), 11)
        for line in lines:
            entry = json.loads(line)
            self.assertIn("audit_id", entry)
            self.assertIn("source_id", entry)
            self.assertIn("issue_type", entry)
            self.assertIn("incorrect_claim", entry)
            self.assertIn("correction", entry)


if __name__ == "__main__":
    unittest.main()
