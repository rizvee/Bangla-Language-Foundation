"""
Adversarial Mutation and Cross-Layer Invariant Tests — BLF.

Adversarially tests that illegal combinations, uncalibrated confidence,
fake attestation claims, blinded review leaks, active secret tracking,
and candidate-level human review invariants are strictly caught and verified.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.generation.realizer import ConstrainedRealizer, RealizationError
from blf.linguistics.complex_predicates import ComplexPredicateEngine
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine, ConjugationError
from blf.linguistics.pragmatics import PragmaticsEngine, HonorificTier
from blf.quality.iaa import compute_cohens_kappa, compute_raw_agreement, evaluate_dual_iaa
from blf.validation.validators import load_schema, validate_dict_against_schema
from scripts.create_private_review_session import create_reviewer_blinded_pack, load_canonical_items, load_practice_items
from scripts.decode_review_submissions import decode_submission


class TestAdversarialInvariants(unittest.TestCase):
    def setUp(self):
        self.realizer = ConstrainedRealizer()
        self.cpred_engine = ComplexPredicateEngine()
        self.prag_engine = PragmaticsEngine()
        self.verbal_engine = VerbalConjugatorEngine()

    def test_adversarial_classifier_pattern_calibration(self):
        """
        Assures that classifier morphotactics reflect external evidence and epistemic calibration:
        1. Arbitrary unknown nominal form != CANONICAL_STANDARD (fails closed).
        2. Absence from blacklist != canonical status.
        3. N+টা+গুলো retains attested status (ATTESTED_OFFICIAL_EDUCATIONAL_USAGE) but not automatic productive standard.
        4. N+গুলো+টা remains independent and REGISTER_UNRESOLVED.
        """
        from blf.linguistics.morphology.nominal_declension import assess_nominal_morphotactics, MorphotacticStatus

        # Invariant 1: Arbitrary unknown nominal form != CANONICAL_STANDARD (fails closed)
        att_unknown = assess_nominal_morphotactics("অপরিচিত_শব্দ_XYZ")
        self.assertEqual(att_unknown["status"], MorphotacticStatus.UNKNOWN)
        self.assertFalse(att_unknown["auto_generation_safe"])

        # Invariant 2: Absence from blacklist != canonical status
        att_non_blacklisted = assess_nominal_morphotactics("কখগঘ")
        self.assertNotEqual(att_non_blacklisted["status"], MorphotacticStatus.CANONICAL_STANDARD)
        self.assertEqual(att_non_blacklisted["status"], MorphotacticStatus.UNKNOWN)
        self.assertFalse(att_non_blacklisted["auto_generation_safe"])

        # Invariant 3: N+টা+গুলো retains attested educational status but not automatic productive standard
        try:
            self.realizer.check_morphotactic_invariants("Activity A-এর ছবিটাগুলো দেখতে বলুন")
            self.realizer.check_morphotactic_invariants("বইটাগুলো নিয়ে এসো")
        except RealizationError:
            self.fail("check_morphotactic_invariants incorrectly rejected attested N+টা+গুলো pattern")

        att_chobi = assess_nominal_morphotactics("ছবিটাগুলো")
        self.assertEqual(att_chobi["status"], MorphotacticStatus.ATTESTED_OFFICIAL_EDUCATIONAL_USAGE)
        self.assertFalse(att_chobi["is_universally_illegal"])
        self.assertFalse(att_chobi["auto_generation_safe"])
        self.assertEqual(att_chobi["review_priority"], "CRITICAL")

        # Invariant 4: Evidence for N+টা+গুলো does NOT automatically validate N+গুলো+টা
        att_gulo_ta = assess_nominal_morphotactics("বইগুলোটা")
        self.assertEqual(att_gulo_ta["status"], MorphotacticStatus.REGISTER_UNRESOLVED)
        self.assertFalse(att_gulo_ta["auto_generation_safe"])
        self.assertNotEqual(att_gulo_ta["status"], att_chobi["status"])

        # Canonical standard vs unresolved vs unsupported distinction
        att_standard = assess_nominal_morphotactics("বইগুলো")
        self.assertEqual(att_standard["status"], MorphotacticStatus.CANONICAL_STANDARD)
        self.assertTrue(att_standard["auto_generation_safe"])

        att_spoken = assess_nominal_morphotactics("ছেলেটাদেরকে")
        self.assertEqual(att_spoken["status"], MorphotacticStatus.REGISTER_UNRESOLVED)
        self.assertFalse(att_spoken["auto_generation_safe"])

        att_chhele = assess_nominal_morphotactics("ছেলেগুলাকে")
        self.assertEqual(att_chhele["status"], MorphotacticStatus.ATTESTED_CONVERSATIONAL)
        self.assertFalse(att_chhele["is_universally_illegal"])

        # Genuine unsupported inverted patterns (গুলোটি, গুলোরটি) are still caught
        with self.assertRaises(RealizationError):
            self.realizer.check_morphotactic_invariants("কলমগুলোরটি দিন")

    def test_adversarial_vector_event_structure_calibration(self):
        """
        Assures that vector verb selection reflects event-structure compatibility:
        5. Stative + ফেলা returns CONTEXT_DEPENDENT/NEEDS_REVIEW rather than 'universally ungrammatical'.
        6. Context-dependent vector combinations are NOT automatically emitted as canonical standard.
        7. Established cognitive achievement + ফেলা is VERIFIED_COMBINATION.
        8. Item 023 candidate B remains human-review dependent.
        12. Unknown pole lemma + manually supplied known semantic type does not become VERIFIED_STANDARD.
        """
        from blf.linguistics.complex_predicates import VectorCompatibilityStatus

        # Stative + ফেলা is CONTEXT_DEPENDENT, not universally ungrammatical
        stative_stay = self.cpred_engine.assess_vector_compatibility("থাক", "ফেলা", "STATIVE_POSTURE")
        self.assertEqual(stative_stay["status"], VectorCompatibilityStatus.CONTEXT_DEPENDENT)
        self.assertEqual(stative_stay["evidence_state"], "NEEDS_HUMAN_REVIEW")
        self.assertIn("telicity_coercion", stative_stay["coercion_factors"])

        stative_be = self.cpred_engine.assess_vector_compatibility("হ", "ফেলা", "STATIVE_BEING")
        self.assertEqual(stative_be["status"], VectorCompatibilityStatus.CONTEXT_DEPENDENT)

        # Context-dependent combinations blocked from automatic standard generation
        valid_default, err = self.cpred_engine.validate_vector_combination("থাক", "ফেলা", "STATIVE_POSTURE")
        self.assertFalse(valid_default)
        self.assertIn("Context-dependent", err)

        with self.assertRaises(RealizationError):
            self.realizer.realize_vector_predicate_sentence("সে", "ঢাকায়", "থাক", "ফেলা", "STATIVE_POSTURE")

        # But permitted with explicit context-dependent opt-in
        valid_optin, _ = self.cpred_engine.validate_vector_combination(
            "থাক", "ফেলা", "STATIVE_POSTURE", allow_context_dependent=True
        )
        self.assertTrue(valid_optin)

        # Established cognitive achievement + ফেলা is VERIFIED_COMBINATION
        valid_cog, _ = self.cpred_engine.validate_vector_combination("জান", "ফেলা", "COGNITIVE_ACHIEVEMENT")
        self.assertTrue(valid_cog, "Cognitive achievement with 'phela' incorrectly rejected")
        cog_assess = self.cpred_engine.assess_vector_compatibility("জান", "ফেলা", "COGNITIVE_ACHIEVEMENT")
        self.assertEqual(cog_assess["status"], VectorCompatibilityStatus.ALLOWED)
        self.assertEqual(cog_assess["evidence_state"], "VERIFIED_COMBINATION")
        self.assertTrue(cog_assess["auto_generation_safe"])

        # Invariant 12: Unknown pole lemma + manually supplied known semantic type does not automatically become VERIFIED_STANDARD
        unk_pole_assess = self.cpred_engine.assess_vector_compatibility("অপরিচিত_ধাতু_XYZ", "ফেলা", "COGNITIVE_ACHIEVEMENT")
        self.assertNotEqual(unk_pole_assess["evidence_state"], "VERIFIED_STANDARD")
        self.assertNotEqual(unk_pole_assess["evidence_state"], "VERIFIED_COMBINATION")
        self.assertFalse(unk_pole_assess["auto_generation_safe"])

        # Item 023 Candidate B ('থেকে ফেলল') is context-dependent / needs review
        item_023_b_compat = self.cpred_engine.assess_vector_compatibility("থাক", "ফেলা", "STATIVE_POSTURE")
        self.assertEqual(item_023_b_compat["evidence_state"], "NEEDS_HUMAN_REVIEW")

    def test_adversarial_wh_construction_and_orthography_split(self):
        """
        Assures Wh-construction epistemic fail-closed behavior:
        9. Arbitrary Wh input returns UNKNOWN (fails closed).
        10. তোমার কী চাই? is not automatically equated with তুমি কী চাও?.
        11. Known standard Wh construction remains supported.
        """
        # Invariant 11: Standard Wh construction remains supported
        res_a = self.prag_engine.analyze_wh_construction("তুমি কী চাও?")
        self.assertEqual(res_a["construction_type"], "NOMINATIVE_AGENTIVE_TRANSITIVE_WH")
        self.assertEqual(res_a["construction_status"], "SUPPORTED_STANDARD")
        self.assertEqual(res_a["orthography_status"], "CANONICAL_STANDARD_WH")
        self.assertTrue(res_a["is_grammatical"])

        # Polar or noncanonical Wh: তুমি কি চাও?
        res_b = self.prag_engine.analyze_wh_construction("তুমি কি চাও?")
        self.assertEqual(res_b["construction_type"], "NOMINATIVE_AGENTIVE_TRANSITIVE_WH")
        self.assertEqual(res_b["construction_status"], "POLAR_OR_ORTHOGRAPHIC_AMBIGUITY")
        self.assertEqual(res_b["orthography_status"], "NONCANONICAL_OR_POLAR_AMBIGUOUS")

        # Invariant 10: তোমার কী চাই? is distinct and not automatically equated with তুমি কী চাও?
        res_c = self.prag_engine.analyze_wh_construction("তোমার কী চাই?")
        self.assertEqual(res_c["construction_type"], "GENITIVE_EXPERIENCER_MODAL_WH")
        self.assertEqual(res_c["construction_status"], "NEEDS_HUMAN_REVIEW")
        self.assertEqual(res_c["orthography_status"], "CANONICAL_STANDARD_WH")
        self.assertTrue(res_c["is_grammatical"])
        self.assertNotEqual(res_c["equivalence_to_standard_wh"], res_a["equivalence_to_standard_wh"])

        # Invariant 9: Arbitrary Wh input returns UNKNOWN, not grammatical=True
        res_arb = self.prag_engine.analyze_wh_construction("কিছু একটা বাক্য কি হবে?")
        self.assertEqual(res_arb["construction_status"], "UNKNOWN")
        self.assertIsNone(res_arb["is_grammatical"])

    def test_adversarial_polyfunctional_particle_je_calibration(self):
        """
        Assures that polyfunctional 'যে' adheres to calibrated epistemic statuses:
        6. Unverified 'যে' taxonomy does not receive VERIFIED status.
        7. Multiple plausible 'যে' senses => ambiguous unless context independently resolves.
        8. Position alone cannot guarantee 'যে' meaning.
        """
        from blf.linguistics.pragmatics import PRAGMATIC_PARTICLE_REGISTRY

        # Invariant 6: Unverified 'যে' taxonomy does not receive VERIFIED status
        je_spec = PRAGMATIC_PARTICLE_REGISTRY["যে"]
        for s in je_spec.senses:
            if s.sense_id in ["SENSE-JE-EMOTIVE-MIRATIVE", "SENSE-JE-CLAUSE-FINAL-EVALUATIVE", "SENSE-JE-EMPHATIC-STANCE"]:
                self.assertNotEqual(s.review_status, "VERIFIED")
                self.assertEqual(s.review_status, "NEEDS_HUMAN_REVIEW")
                self.assertEqual(s.confidence, "MEDIUM")
            elif s.sense_id == "SENSE-JE-COMPLEMENTIZER":
                self.assertEqual(s.review_status, "VERIFIED")
                self.assertEqual(s.confidence, "HIGH")

        # Unknown context returns AMBIGUOUS, not a deterministic guess
        ambig_res = self.prag_engine.analyze_particle_je("তিনি যে মানুষ")
        self.assertTrue(ambig_res["is_ambiguous"])
        self.assertEqual(ambig_res["primary_sense"], "AMBIGUOUS")
        self.assertGreater(len(ambig_res["candidate_senses"]), 1)

        # Invariant 7 & 8: Item 040 candidates A and B preserve ambiguity and alternative stance interpretations
        # A: আরে, সে যে এসে গেছে! (topic-adjacent: mirative + emphatic stance plausible)
        res_040_a = self.prag_engine.analyze_particle_je("আরে, সে যে এসে গেছে!")
        self.assertTrue(res_040_a["is_ambiguous"])
        self.assertEqual(res_040_a["primary_sense"], "AMBIGUOUS")
        self.assertEqual(res_040_a["most_likely_sense"], "SENSE-JE-EMOTIVE-MIRATIVE")
        self.assertIn("SENSE-JE-EMPHATIC-STANCE", res_040_a["candidate_senses"])
        self.assertTrue(res_040_a["mirativity"])

        # B: আরে, সে এসে গেছে যে! (clause-final: evaluative + emphatic stance plausible)
        res_040_b = self.prag_engine.analyze_particle_je("আরে, সে এসে গেছে যে!")
        self.assertTrue(res_040_b["is_ambiguous"])
        self.assertEqual(res_040_b["primary_sense"], "AMBIGUOUS")
        self.assertEqual(res_040_b["most_likely_sense"], "SENSE-JE-CLAUSE-FINAL-EVALUATIVE")
        self.assertIn("SENSE-JE-EMPHATIC-STANCE", res_040_b["candidate_senses"])

        # C: আরে, সে কি এসে গেছে! (polar question strategy)
        dis_c = self.prag_engine.disambiguate_ki("আরে, সে কি এসে গেছে!")
        self.assertTrue(any(d["syntactic_function"] == "POLAR_INTERROGATIVE_PARTICLE" for d in dis_c["disambiguations"]))

    def test_adversarial_source_claim_binding_integrity(self):
        """
        Invariant 5: External source identity and claim-level evidence bindings.
        Validates exact artifact metadata, PDF locators, YPSA attribution, and unverified publication year handling.
        """
        sources_path = ROOT_DIR / "sources" / "registry" / "sources.json"
        with open(sources_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        sources_by_id = {s["source_id"]: s for s in data["sources"]}

        # 1. NCTB artifact identity and exact URL
        nctb = sources_by_id["NCTB-TG-BANGLA"]
        self.assertEqual(nctb["verification_status"], "PROVISIONAL")
        self.assertEqual(
            nctb["url"],
            "https://dpe.portal.gov.bd/sites/default/files/files/dpe.portal.gov.bd/page/925359f0_2493_43bf_9890_afa439266cd6/TG%20-%20Class%204%20English.pdf",
        )
        self.assertEqual(nctb["title"], "Teacher's Guide: English for Today (Class 4)")
        self.assertIn("Class 4 English", nctb["edition"])
        self.assertEqual(nctb["source_tier"], "TIER_C")
        self.assertIsNone(nctb["identifier"])

        # 2. Exact 'ছবিটাগুলো' occurrence bound to narrow claim
        nctb_claims = {c["claim_id"]: c for c in nctb["verification"]["claims"]}
        self.assertIn("CLM-NCTB-CHOBITAGULO-OCCURRENCE", nctb_claims)
        self.assertIn("ছবিটাগুলো", nctb_claims["CLM-NCTB-CHOBITAGULO-OCCURRENCE"]["value"])
        self.assertIn("broader_bdsb_distribution", nctb["verification"]["unresolved_fields"])
        self.assertIn("broader_bdsb_productivity", nctb["verification"]["unresolved_fields"])

        # 3. Accessible Dictionary creator attribution includes YPSA
        a2i = sources_by_id["ACCESSIBLE-DICT-A2I"]
        self.assertEqual(a2i["verification_status"], "PROVISIONAL")
        self.assertIn("YPSA", a2i["author_or_org"])
        self.assertIn("YPSA", a2i["publisher"])
        self.assertEqual(a2i["source_tier"], "TIER_D")
        self.assertIsNone(a2i["identifier"])

        # 4. Publication year is not silently treated as verified
        self.assertNotIn("year", nctb["verification"]["verified_fields"])
        self.assertIn("year", nctb["verification"]["unresolved_fields"])
        self.assertNotIn("year", a2i["verification"]["verified_fields"])
        self.assertIn("year", a2i["verification"]["unresolved_fields"])

        # 5. 'যে ৩' exact headword evidence bound to polyfunctionality claim
        a2i_claims = {c["claim_id"]: c for c in a2i["verification"]["claims"]}
        self.assertIn("CLM-ACCESSIBLE-DICT-JE-POLYFUNCTIONAL", a2i_claims)
        self.assertEqual(a2i_claims["CLM-ACCESSIBLE-DICT-JE-POLYFUNCTIONAL"]["value"], "PARTICLE_JE_IS_POLYFUNCTIONAL")
        a2i_ev_locators = [e["locator"] for e in a2i["verification"]["primary_evidence"]]
        self.assertTrue(any("যে ৩" in loc for loc in a2i_ev_locators))
        self.assertIn("blf_exact_four_sense_taxonomy", a2i["verification"]["unresolved_fields"])

    def test_adversarial_vector_provenance_and_evidence_bindings(self):
        """
        Assures that vector combinations enforce strict evidence bindings:
        - Every VERIFIED_VECTOR_COMBINATION has at least one traceable evidence and claim ID.
        - Unbound combinations cannot claim VERIFIED_COMBINATION.
        - Dead vectors not in VECTOR_INVENTORY return UNKNOWN.
        """
        from blf.linguistics.complex_predicates import (
            VectorCompatibilityStatus,
            VERIFIED_VECTOR_REGISTRY,
            VERIFIED_VECTOR_COMBINATIONS,
            VECTOR_INVENTORY,
        )

        # 1. Every entry in VERIFIED_VECTOR_REGISTRY has traceable evidence/claim bindings
        self.assertGreater(len(VERIFIED_VECTOR_REGISTRY), 0)
        for (pole, vec), ev in VERIFIED_VECTOR_REGISTRY.items():
            self.assertIn(vec, VECTOR_INVENTORY, f"Vector '{vec}' in registry not present in VECTOR_INVENTORY")
            self.assertGreater(len(ev.evidence_ids), 0, f"Pair ({pole}, {vec}) missing evidence_ids")
            self.assertGreater(len(ev.claim_ids), 0, f"Pair ({pole}, {vec}) missing claim_ids")
            self.assertGreater(len(ev.source_ids), 0, f"Pair ({pole}, {vec}) missing source_ids")
            self.assertEqual(ev.status, "VERIFIED_COMBINATION")

        # 2. Unbound vector pair (e.g. লিখ + ফেলা) is TYPE_LICENSED, NOT VERIFIED_COMBINATION
        likh_assess = self.cpred_engine.assess_vector_compatibility("লিখ", "ফেলা", "TRANSITIVE_DYNAMIC")
        self.assertEqual(likh_assess["status"], VectorCompatibilityStatus.ALLOWED)
        self.assertEqual(likh_assess["evidence_state"], "TYPE_LICENSED")
        self.assertFalse(likh_assess["auto_generation_safe"])
        self.assertEqual(likh_assess["evidence_ids"], [])

        # 3. Dead vector (যাওয়া) not in VECTOR_INVENTORY returns UNKNOWN
        thak_jawa = self.cpred_engine.assess_vector_compatibility("থাক", "যাওয়া", "DURATIVE_ACTION")
        self.assertEqual(thak_jawa["status"], VectorCompatibilityStatus.UNKNOWN)
        self.assertFalse(thak_jawa["auto_generation_safe"])
        self.assertEqual(thak_jawa["evidence_state"], "UNKNOWN")

    def test_adversarial_pilot_40_item_count_freeze(self):
        """
        Invariant 14: All 40 pilot items remain strictly unchanged in count and frozen for human pilot.
        """
        queue_path = ROOT_DIR / "data" / "review_queue" / "human_review_pilot_40.json"
        with open(queue_path, "r", encoding="utf-8") as f:
            queue = json.load(f)
        items = queue.get("items", [])
        self.assertEqual(len(items), 40, f"Expected exactly 40 pilot items, found {len(items)}")
        pilot_ids = [it["pilot_id"] for it in items]
        self.assertEqual(len(set(pilot_ids)), 40, "Duplicate pilot IDs detected")

    def test_adversarial_unmodeled_participle_rejected(self):
        """Assures that arbitrary unmodeled verbs raise ConjugationError rather than emitting corrupted fallbacks."""
        with self.assertRaises(ConjugationError):
            self.verbal_engine.get_conjunctive_participle("অজানা_ক্রিয়াপদ_XYZ")

    def test_adversarial_honorific_clash_prevented(self):
        """Assures that honorific tier transformations strictly preserve agreement."""
        apni_pres = self.prag_engine.transform_addressee_register("কর", "PRES_SIMP", HonorificTier.HONORIFIC)
        self.assertIn("করেন", apni_pres)
        self.assertNotIn("করিস", apni_pres)
        self.assertNotIn("করো", apni_pres)

        tui_pres = self.prag_engine.transform_addressee_register("কর", "PRES_SIMP", HonorificTier.INTIMATE)
        self.assertIn("করিস", tui_pres)
        self.assertNotIn("করেন", tui_pres)

    def test_adversarial_private_sessions_gitignored(self):
        """Assures that .blf-private/ is explicitly included in .gitignore to prevent committing active secrets."""
        gitignore_path = ROOT_DIR / ".gitignore"
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(".blf-private/", content, ".blf-private/ must be in .gitignore")

    def test_adversarial_candidate_level_submission_schema(self):
        """Assures that raw reviewer submissions validate candidate-level judgments and require no secret seeds."""
        schema_path = ROOT_DIR / "schemas" / "v0_1" / "human_review_decision.schema.json"
        schema = load_schema(schema_path)

        valid_submission = {
            "submission_id": "REV-SUB-0001",
            "session_id": "SESS-PILOT-0001",
            "reviewer_pseudonym": "REV-LINGUIST-01",
            "reviewer_qualification": "NATIVE_LINGUIST",
            "native_bangladeshi_speaker": True,
            "native_variety": "BDSB_STANDARD",
            "opaque_item_id": "BLIND-R1-A7K4",
            "candidate_judgments": {
                "A": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},
                "B": {"acceptability": "MARKED_BUT_VALID", "certainty": "SURE"},
            },
            "preferred_candidates": ["A"],
            "correction": None,
            "comments": "Candidate A is unmarked canonical standard.",
            "timestamp": "2026-08-28T12:00:00Z",
        }
        valid, errs = validate_dict_against_schema(valid_submission, schema)
        self.assertTrue(valid, f"Failed to validate candidate-level submission: {errs}")

        # Multiple preferred candidates is valid
        multi_pref = dict(valid_submission)
        multi_pref["preferred_candidates"] = ["A", "B"]
        valid_multi, _ = validate_dict_against_schema(multi_pref, schema)
        self.assertTrue(valid_multi)

        # NONE preferred candidate is valid
        none_pref = dict(valid_submission)
        none_pref["preferred_candidates"] = ["NONE"]
        valid_none, _ = validate_dict_against_schema(none_pref, schema)
        self.assertTrue(valid_none)

    def test_adversarial_private_session_generation_opaque_ids(self):
        """Assures that private session creator produces opaque IDs, intermixed orders, and no research leaks."""
        canonical_items = load_canonical_items()
        practice_items = load_practice_items()
        self.assertEqual(len(canonical_items), 40)
        self.assertEqual(len(practice_items), 3)

        pack_a, map_a = create_reviewer_blinded_pack(
            canonical_items, practice_items, "SESS-TEST", "REV-A", "R1", 101
        )
        pack_b, map_b = create_reviewer_blinded_pack(
            canonical_items, practice_items, "SESS-TEST", "REV-B", "R2", 202
        )

        # Opaque display ID format
        for it in pack_a:
            self.assertTrue(it["display_id"].startswith("BLIND-R1-"))
            self.assertNotIn("PILOT-ITEM-", it["display_id"])
            self.assertNotIn("category", it)  # Research category withheld from reviewer
            self.assertNotIn("rule_id", it)

        # Item order differs between seeds
        order_a = [map_a[it["display_id"]]["canonical_item_id"] for it in pack_a]
        order_b = [map_b[it["display_id"]]["canonical_item_id"] for it in pack_b]
        self.assertNotEqual(order_a, order_b, "Item orders must be independently shuffled across reviewers")

    def test_adversarial_decoding_and_dual_iaa(self):
        """Assures that raw submissions decode accurately and evaluate on dual IAA metrics."""
        mapping_data = {
            "session_id": "SESS-TEST",
            "item_mappings": {
                "REV-A": {
                    "BLIND-R1-0001": {
                        "canonical_item_id": "PILOT-ITEM-001",
                        "category": "VERB_MORPHOLOGY",
                        "displayed_to_canonical": {"A": "CAND_B", "B": "CAND_A", "C": "CAND_C"},
                    }
                },
                "REV-B": {
                    "BLIND-R2-0001": {
                        "canonical_item_id": "PILOT-ITEM-001",
                        "category": "VERB_MORPHOLOGY",
                        "displayed_to_canonical": {"A": "CAND_A", "B": "CAND_B", "C": "CAND_C"},
                    }
                }
            }
        }

        sub_a = {
            "submission_id": "REV-SUB-A1",
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-A",
            "opaque_item_id": "BLIND-R1-0001",
            "candidate_judgments": {
                "A": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},  # displayed A is CAND_B
                "B": {"acceptability": "UNGRAMMATICAL", "certainty": "VERY_SURE"},     # displayed B is CAND_A
                "C": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},  # displayed C is CAND_C
            },
            "preferred_candidates": ["A"],
            "timestamp": "2026-08-28T12:00:00Z",
        }

        sub_b = {
            "submission_id": "REV-SUB-B1",
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-B",
            "opaque_item_id": "BLIND-R2-0001",
            "candidate_judgments": {
                "A": {"acceptability": "UNGRAMMATICAL", "certainty": "VERY_SURE"},     # displayed A is CAND_A
                "B": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},  # displayed B is CAND_B
                "C": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},  # displayed C is CAND_C
            },
            "preferred_candidates": ["B"],  # displayed B is CAND_B
            "timestamp": "2026-08-28T12:00:00Z",
        }

        dec_a = decode_submission(mapping_data, sub_a, allow_partial=True)
        dec_b = decode_submission(mapping_data, sub_b, allow_partial=True)

        # Both decoded records should agree that CAND_B is NATURAL_STANDARD and CAND_A is UNGRAMMATICAL
        self.assertEqual(dec_a[0]["canonical_candidate_judgments"]["CAND_B"]["acceptability"], "NATURAL_STANDARD")
        self.assertEqual(dec_b[0]["canonical_candidate_judgments"]["CAND_B"]["acceptability"], "NATURAL_STANDARD")
        self.assertEqual(dec_a[0]["canonical_preferred_candidates"], ["CAND_B"])
        self.assertEqual(dec_b[0]["canonical_preferred_candidates"], ["CAND_B"])

        # Dual IAA evaluation
        res = evaluate_dual_iaa(dec_a, dec_b, "REV-A", "REV-B")
        self.assertEqual(res["candidate_acceptability"]["raw_agreement"], 1.0)
        self.assertEqual(res["preferred_candidates"]["exact_matches"], 1)


if __name__ == "__main__":
    unittest.main()
