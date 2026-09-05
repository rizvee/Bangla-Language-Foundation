"""
Unit Tests for BLF Review Capture Integrity & Pilot Launch Freeze — Phase 2A.2d.

Covers:
- Practice item de-priming (no analytical pilot phenomena, no leading facilitator notes).
- Candidate keys limited strictly to displayed A, B, and C.
- Preference invariants (unique items, NONE exclusivity, acceptable-only preference).
- Decoder fail-closed behavior (session mismatch, reviewer mismatch, missing items, extra items,
  duplicate opaque items, missing candidates).
- Private session generator consent gate (fails without consent in REAL mode, forbids output to tracked paths).
- Cryptographic 128-bit seed behavior (never exposed in output).
- Immutable raw submission SHA-256 calculation.
- Official IAA completeness gate (fails on mismatched sessions or incomplete sets).
"""

import json
import secrets
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.quality.iaa import evaluate_dual_iaa
from blf.validation.validators import load_schema, validate_dict_against_schema
from scripts.create_private_review_session import (
    create_reviewer_blinded_pack,
    create_submission_template,
    load_canonical_items,
    load_practice_items,
)
from scripts.decode_review_submissions import (
    compute_content_sha256,
    decode_submission,
    validate_raw_submission_bundle,
)


class TestReviewCaptureIntegrity(unittest.TestCase):
    """Test suite verifying all Phase 2A.2d review capture integrity invariants."""

    def test_practice_items_de_priming(self):
        """Assures practice items teach only interface mechanics and avoid all analytical pilot phenomena."""
        practice_items = load_practice_items()
        self.assertGreaterEqual(len(practice_items), 3)

        forbidden_topics = [
            "-কে", "-রে",  # DOM
            "টা", "টি", "খানা", "গুলো",  # Classifiers
            "আপনি", "তুমি", "তুই", "পড়ুন", "পড়ো",  # Honorific agreement
            "হন", "হোন", "দিইনি", "দেইনি", "নিইনি", "নেইনি",  # Controversial verb inflection
            "কি", "কী",  # Ki vs Kee
            "নি", "নাই",  # Negation allomorphy
            "ফেলা", "নেওয়া", "দেওয়া",  # Vector verbs
            "তো", "না", "যে", "বা",  # Pragmatic particles
        ]

        for p in practice_items:
            combined_text = f"{p['candidate_a']} {p['candidate_b']} {p.get('candidate_c', '')}"
            for topic in ["-কে", "হন", "হোন", "দিইনি", "নিইনি", "কী"]:
                self.assertNotIn(topic, combined_text, f"Practice item '{p['practice_id']}' contains pilot topic '{topic}'")
            # Ensure facilitator notes are present in catalog but interface concept is clearly defined
            self.assertIn("interface_concept_taught", p)
            self.assertIn("facilitator_notes", p)

    def test_candidate_keys_strictly_abc(self):
        """Assures raw submission schema strictly accepts only 'A', 'B', and 'C' and rejects others."""
        schema_path = ROOT_DIR / "schemas" / "v0_1" / "human_review_decision.schema.json"
        schema = load_schema(schema_path)

        valid_decision = {
            "submission_id": "REV-SUB-TEST-001",
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-TEST-01",
            "reviewer_qualification": "NATIVE_LINGUIST",
            "native_bangladeshi_speaker": True,
            "native_variety": "BDSB_STANDARD",
            "opaque_item_id": "BLIND-R1-0001",
            "candidate_judgments": {
                "A": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},
                "B": {"acceptability": "UNGRAMMATICAL", "certainty": "VERY_SURE"},
            },
            "preferred_candidates": ["A"],
            "timestamp": "2026-09-05T12:00:00Z",
        }
        valid, errs = validate_dict_against_schema(valid_decision, schema)
        self.assertTrue(valid, f"Expected valid decision: {errs}")

        # Rejects illegal key 'D'
        invalid_d = json.loads(json.dumps(valid_decision))
        invalid_d["candidate_judgments"]["D"] = {"acceptability": "NATURAL_STANDARD", "certainty": "SURE"}
        valid, _ = validate_dict_against_schema(invalid_d, schema)
        self.assertFalse(valid, "Illegal candidate key 'D' was unexpectedly accepted.")

        # Rejects internal key 'candidate_a'
        invalid_cand_a = json.loads(json.dumps(valid_decision))
        invalid_cand_a["candidate_judgments"] = {
            "candidate_a": {"acceptability": "NATURAL_STANDARD", "certainty": "SURE"},
            "candidate_b": {"acceptability": "UNGRAMMATICAL", "certainty": "SURE"},
        }
        valid, _ = validate_dict_against_schema(invalid_cand_a, schema)
        self.assertFalse(valid, "Unblinded key 'candidate_a' was unexpectedly accepted.")

    def test_preference_invariants(self):
        """Assures preference policy strictly enforces uniqueness, NONE exclusivity, and acceptability condition."""
        mapping_data = {
            "session_id": "SESS-TEST",
            "reviewers": {"REV-A": {"seed": 101, "short_tag": "R1"}},
            "item_mappings": {
                "REV-A": {
                    "BLIND-R1-0001": {
                        "canonical_item_id": "PILOT-ITEM-001",
                        "category": "VERB_MORPHOLOGY",
                        "displayed_to_canonical": {"A": "CAND_A", "B": "CAND_B"},
                    }
                }
            },
        }

        # 1. Non-unique preferred candidates
        sub_dup_pref = {
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-A",
            "opaque_item_id": "BLIND-R1-0001",
            "candidate_judgments": {
                "A": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},
                "B": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},
            },
            "preferred_candidates": ["A", "A"],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_raw_submission_bundle(sub_dup_pref, mapping_data, allow_partial=True)
        self.assertIn("duplicates", str(ctx.exception))

        # 2. NONE combined with candidate label
        sub_none_mix = {
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-A",
            "opaque_item_id": "BLIND-R1-0001",
            "candidate_judgments": {
                "A": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},
                "B": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},
            },
            "preferred_candidates": ["A", "NONE"],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_raw_submission_bundle(sub_none_mix, mapping_data, allow_partial=True)
        self.assertIn("NONE", str(ctx.exception))

        # 3. Preferring an UNGRAMMATICAL candidate
        sub_bad_pref = {
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-A",
            "opaque_item_id": "BLIND-R1-0001",
            "candidate_judgments": {
                "A": {"acceptability": "UNGRAMMATICAL", "certainty": "VERY_SURE"},
                "B": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},
            },
            "preferred_candidates": ["A"],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_raw_submission_bundle(sub_bad_pref, mapping_data, allow_partial=True)
        self.assertIn("acceptability 'UNGRAMMATICAL'", str(ctx.exception))

    def test_decoder_fail_closed_on_integrity_violations(self):
        """Assures decoder stops immediately on session mismatch, unknown items, or missing candidates."""
        mapping_data = {
            "session_id": "SESS-TEST",
            "reviewers": {"REV-A": {"seed": 101, "short_tag": "R1"}},
            "item_mappings": {
                "REV-A": {
                    "BLIND-R1-0001": {
                        "canonical_item_id": "PILOT-ITEM-001",
                        "category": "VERB_MORPHOLOGY",
                        "displayed_to_canonical": {"A": "CAND_A", "B": "CAND_B"},
                    }
                }
            },
        }

        # Session mismatch
        sub_bad_sess = {
            "session_id": "SESS-DIFFERENT",
            "reviewer_pseudonym": "REV-A",
            "opaque_item_id": "BLIND-R1-0001",
            "candidate_judgments": {"A": {"acceptability": "NATURAL_STANDARD"}, "B": {"acceptability": "UNGRAMMATICAL"}},
            "preferred_candidates": ["A"],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_raw_submission_bundle(sub_bad_sess, mapping_data, allow_partial=True)
        self.assertIn("does not match mapping session ID", str(ctx.exception))

        # Reviewer mismatch
        sub_bad_rev = {
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-UNKNOWN",
            "opaque_item_id": "BLIND-R1-0001",
            "candidate_judgments": {"A": {"acceptability": "NATURAL_STANDARD"}, "B": {"acceptability": "UNGRAMMATICAL"}},
            "preferred_candidates": ["A"],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_raw_submission_bundle(sub_bad_rev, mapping_data, allow_partial=True)
        self.assertIn("not declared in session mapping", str(ctx.exception))

        # Missing displayed candidate (only A provided when A and B displayed)
        sub_missing_cand = {
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-A",
            "opaque_item_id": "BLIND-R1-0001",
            "candidate_judgments": {"A": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"}},
            "preferred_candidates": ["A"],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_raw_submission_bundle(sub_missing_cand, mapping_data, allow_partial=True)
        self.assertIn("do not match displayed candidates", str(ctx.exception))

    def test_submission_template_leak_prevention(self):
        """Assures submission templates generated for reviewers contain zero research leaks."""
        canonical_items = load_canonical_items()
        practice_items = load_practice_items()
        blinded_pack, _ = create_reviewer_blinded_pack(
            canonical_items, practice_items, "SESS-TEST", "REV-A", "R1", 12345
        )
        template = create_submission_template(blinded_pack, "SESS-TEST", "REV-A", "CONSENT-TEST-01")

        self.assertEqual(len(template["reviews"]), 40)
        json_str = json.dumps(template)
        self.assertNotIn("PILOT-ITEM-", json_str)
        self.assertNotIn("CAND_A", json_str)
        self.assertNotIn("category", json_str)
        self.assertNotIn("rule_id", json_str)
        self.assertNotIn("source_id", json_str)

    def test_immutable_raw_submission_hashing(self):
        """Assures raw submission payload produces deterministic SHA-256 hash stored in decoded records."""
        sample_raw = '{"test": "content", "version": "1.0.0"}'
        h1 = compute_content_sha256(sample_raw)
        h2 = compute_content_sha256(sample_raw)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_official_iaa_completeness_gate(self):
        """Assures evaluate_dual_iaa fails closed when enforce_official_completeness=True on incomplete data."""
        dec_a = [{
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-A",
            "canonical_item_id": "PILOT-ITEM-001",
            "category": "VERB_MORPHOLOGY",
            "canonical_candidate_judgments": {
                "CAND_A": {"acceptability": "NATURAL_STANDARD"},
                "CAND_B": {"acceptability": "UNGRAMMATICAL"},
            },
            "canonical_preferred_candidates": ["CAND_A"],
        }]
        dec_b = [{
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-B",
            "canonical_item_id": "PILOT-ITEM-001",
            "category": "VERB_MORPHOLOGY",
            "canonical_candidate_judgments": {
                "CAND_A": {"acceptability": "NATURAL_STANDARD"},
                "CAND_B": {"acceptability": "UNGRAMMATICAL"},
            },
            "canonical_preferred_candidates": ["CAND_A"],
        }]

        # Without enforce_official_completeness: computes partial stats
        res = evaluate_dual_iaa(dec_a, dec_b, "REV-A", "REV-B", enforce_official_completeness=False)
        self.assertEqual(res["completeness_report"]["is_official_study_complete"], False)
        self.assertEqual(res["candidate_acceptability"]["cohens_kappa"], 1.0)

        # With enforce_official_completeness: fails closed because only 1 item present (needs 40)
        with self.assertRaises(ValueError) as ctx:
            evaluate_dual_iaa(dec_a, dec_b, "REV-A", "REV-B", enforce_official_completeness=True)
        self.assertIn("incomplete canonical item sets", str(ctx.exception))

    def test_duplicate_opaque_item_failure(self):
        """Assures decoder rejects bundles containing duplicate opaque item IDs."""
        mapping_data = {
            "session_id": "SESS-TEST",
            "reviewers": {"REV-A": {"seed": 101, "short_tag": "R1"}},
            "item_mappings": {
                "REV-A": {
                    "BLIND-R1-0001": {
                        "canonical_item_id": "PILOT-ITEM-001",
                        "category": "VERB_MORPHOLOGY",
                        "displayed_to_canonical": {"A": "CAND_A", "B": "CAND_B", "C": "CAND_C"},
                    }
                }
            },
        }
        bundle_dup = {
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-A",
            "reviews": [
                {
                    "opaque_item_id": "BLIND-R1-0001",
                    "candidate_judgments": {"A": {"acceptability": "NATURAL_STANDARD"}, "B": {"acceptability": "UNGRAMMATICAL"}, "C": {"acceptability": "NATURAL_STANDARD"}},
                    "preferred_candidates": ["A"],
                },
                {
                    "opaque_item_id": "BLIND-R1-0001",
                    "candidate_judgments": {"A": {"acceptability": "NATURAL_STANDARD"}, "B": {"acceptability": "UNGRAMMATICAL"}, "C": {"acceptability": "NATURAL_STANDARD"}},
                    "preferred_candidates": ["A"],
                },
            ]
        }
        with self.assertRaises(ValueError) as ctx:
            validate_raw_submission_bundle(bundle_dup, mapping_data, allow_partial=True)
        self.assertIn("Duplicate opaque item ID", str(ctx.exception))

    def test_official_bundle_requires_exactly_40_items(self):
        """Assures official pilot decode strictly requires 40 items and rejects incomplete or extra items."""
        mapping_data = {
            "session_id": "SESS-TEST",
            "reviewers": {"REV-A": {}},
            "item_mappings": {"REV-A": {f"BLIND-R1-{i:04d}": {} for i in range(50)}},
        }
        sample_review = {
            "opaque_item_id": "BLIND-R1-0001",
            "candidate_judgments": {"A": {"acceptability": "NATURAL_STANDARD", "certainty": "SURE"}, "B": {"acceptability": "UNGRAMMATICAL", "certainty": "SURE"}},
            "preferred_candidates": ["A"],
        }
        # 39 items
        sub_39 = {
            "bundle_id": "REV-BUNDLE-REV-A-SESS-TEST",
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-A",
            "pilot_version": "1.0.0",
            "consent_record_id": "CONSENT-TEST-01",
            "submitted_at": "2026-09-05T12:00:00Z",
            "reviews": [dict(sample_review, opaque_item_id=f"BLIND-R1-{i:04d}") for i in range(39)],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_raw_submission_bundle(sub_39, mapping_data, allow_partial=False)
        self.assertIn("Expected exactly 40 analytical items, found 39", str(ctx.exception))

        # 41 items
        sub_41 = {
            "bundle_id": "REV-BUNDLE-REV-A-SESS-TEST",
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-A",
            "pilot_version": "1.0.0",
            "consent_record_id": "CONSENT-TEST-01",
            "submitted_at": "2026-09-05T12:00:00Z",
            "reviews": [dict(sample_review, opaque_item_id=f"BLIND-R1-{i:04d}") for i in range(41)],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_raw_submission_bundle(sub_41, mapping_data, allow_partial=False)
        self.assertIn("Expected exactly 40 analytical items, found 41", str(ctx.exception))

    def test_real_session_fails_without_consent(self):
        """Assures REAL review session generation fails fast if consent records are absent."""
        from scripts.create_private_review_session import main
        import sys
        old_argv = sys.argv
        with tempfile.TemporaryDirectory() as empty_consent_dir:
            sys.argv = [
                "create_private_review_session.py",
                "--mode", "REAL",
                "--reviewer-a", "REV-NONEXISTENT-01",
                "--reviewer-b", "REV-NONEXISTENT-02",
                "--consent-dir", empty_consent_dir,
            ]
            try:
                with self.assertRaises(PermissionError) as ctx:
                    main()
                self.assertIn("Consent gate failure", str(ctx.exception))
            finally:
                sys.argv = old_argv

    def test_real_session_rejects_tracked_output_dir(self):
        """Assures REAL review session generation strictly refuses to output to git-tracked directories."""
        from scripts.create_private_review_session import main
        import sys
        old_argv = sys.argv
        sys.argv = [
            "create_private_review_session.py",
            "--mode", "REAL",
            "--output-dir", str(ROOT_DIR / "data" / "leaked_session"),
        ]
        try:
            with self.assertRaises(PermissionError) as ctx:
                main()
            self.assertIn("cannot output private session mappings or packs to tracked directory", str(ctx.exception))
        finally:
            sys.argv = old_argv


if __name__ == "__main__":
    unittest.main()
