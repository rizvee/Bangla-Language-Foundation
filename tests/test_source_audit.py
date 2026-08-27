"""
Regression tests for bibliographic verification and source integrity auditing.
"""

import json
import unittest
from pathlib import Path

from blf.linguistics.tags import VerificationStatus
from scripts.audit_sources import (
    audit_known_misidentifications,
    audit_source_structure,
    load_sources,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT_DIR / "sources" / "registry" / "sources.json"
AUDIT_LOG_PATH = ROOT_DIR / "sources" / "registry" / "source-audit.jsonl"


class TestSourceAudit(unittest.TestCase):
    def test_known_misidentifications_detected(self):
        """Tests that historical misidentified citations are detected and rejected."""
        # 1. 2021.wnut-1.14 misattributed as Banglish transliteration
        bad_translit = {
            "source_id": "TEST-BAD-TRANSLIT",
            "title": "Banglish Transliteration",
            "author_or_org": "Firoj Alam",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2021,
            "license": "CC-BY-4.0",
            "redistribution": "open_redistribution",
            "verification_status": "VERIFIED",
            "citation": "Proceedings of WNUT 2021. https://aclanthology.org/2021.wnut-1.14/",
            "notes": "Banglish transliteration"
        }
        errs = audit_known_misidentifications(bad_translit)
        self.assertTrue(len(errs) > 0, "Failed to catch ACL 2021.wnut-1.14 misattribution.")

        # 2. 2022.findings-emnlp.319 misattributed as SentiraBangla
        bad_sentiment = {
            "source_id": "TEST-BAD-SENTIMENT",
            "title": "SentiraBangla Code-Mixed Sentiment",
            "author_or_org": "Md. Arid Hasan",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2022,
            "license": "CC-BY-NC-4.0",
            "redistribution": "derived_features_only",
            "verification_status": "VERIFIED",
            "citation": "Findings of EMNLP 2022. https://aclanthology.org/2022.findings-emnlp.319/",
            "notes": "Code-mixed sentiment"
        }
        errs = audit_known_misidentifications(bad_sentiment)
        self.assertTrue(len(errs) > 0, "Failed to catch ACL 2022.findings-emnlp.319 misattribution.")

        # 3. 2206.14051 misattributed as Bengali.AI Speech
        bad_speech = {
            "source_id": "TEST-BAD-SPEECH",
            "title": "Bengali.AI Speech Corpus",
            "author_or_org": "Bengali.AI",
            "source_tier": "TIER_D",
            "language": "bn",
            "year": 2022,
            "license": "CC0-1.0",
            "redistribution": "open_redistribution",
            "verification_status": "VERIFIED",
            "citation": "arXiv:2206.14051",
            "notes": "Bengali.AI speech audio dataset"
        }
        errs = audit_known_misidentifications(bad_speech)
        self.assertTrue(len(errs) > 0, "Failed to catch arXiv:2206.14051 misattribution.")

    def test_verified_source_requires_evidence_block(self):
        """VERIFIED status must contain explicit verification evidence."""
        source_without_evidence = {
            "source_id": "TEST-VERIFIED-NO-EVIDENCE",
            "title": "Test Grammar",
            "author_or_org": "Test Author",
            "source_tier": "TIER_A",
            "language": "bn",
            "year": 2020,
            "license": "MIT",
            "redistribution": "open_redistribution",
            "verification_status": "VERIFIED",
            "citation": "Test Author (2020)."
        }
        errs = audit_source_structure(source_without_evidence)
        self.assertTrue(any("verification" in e for e in errs), "Source without verification block was incorrectly permitted as VERIFIED.")

    def test_audit_log_exists_and_valid(self):
        """Verifies that source-audit.jsonl exists and contains valid JSON lines."""
        self.assertTrue(AUDIT_LOG_PATH.is_file(), "source-audit.jsonl not found.")
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertTrue(len(lines) >= 5, "source-audit.jsonl contains insufficient audit trail entries.")
        for line in lines:
            record = json.loads(line.strip())
            self.assertIn("audit_id", record)
            self.assertIn("source_id", record)
            self.assertIn("previous_status", record)
            self.assertIn("new_status", record)
            self.assertIn("issue_type", record)
            self.assertIn("correction", record)

    def test_all_registry_sources_pass_integrity_audit(self):
        """All sources currently in sources.json must pass structural and misidentification checks."""
        data = load_sources()
        sources = data.get("sources", [])
        self.assertTrue(len(sources) > 0)
        
        for src in sources:
            sid = src.get("source_id")
            struct_errs = audit_source_structure(src)
            misid_errs = audit_known_misidentifications(src)
            all_errs = struct_errs + misid_errs
            self.assertEqual(all_errs, [], f"Source '{sid}' failed integrity audit: {all_errs}")


if __name__ == "__main__":
    unittest.main()
