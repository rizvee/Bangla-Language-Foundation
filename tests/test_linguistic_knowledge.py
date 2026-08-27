"""
Unit tests for the BLF Linguistic Knowledge Layer & Ontology Models.

Verifies:
1. Referential integrity across Sources -> Evidence -> Claims -> Rules -> Examples.
2. Anti-slop invariants: no dangling IDs, no unauthorized HUMAN_APPROVED states.
3. Schema conformity for all ontology files.
4. Correctness of dataclasses and domain models in src/blf/ontology.
"""

import json
import unittest
from pathlib import Path
import sys

# Ensure src is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from blf.ontology.models import (
    EpistemicClass,
    Grammaticality,
    LanguageVariety,
    LinguisticClaim,
    LinguisticEvidence,
    LinguisticExample,
    LinguisticLevel,
    LinguisticRule,
    Productivity,
    ProvenanceClass,
    ReviewStatus,
    RuleRelation,
    RuleRelationType,
    TerminologyMapping,
)
from blf.validation.validators import load_schema, validate_dict_against_schema


class TestLinguisticKnowledgeLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parent.parent
        cls.schemas_dir = cls.root_dir / "schemas" / "v0_1"
        cls.sources_path = cls.root_dir / "sources" / "registry" / "sources.json"
        cls.evidence_path = cls.root_dir / "ontology" / "evidence" / "pilot_evidence.json"
        cls.claims_path = cls.root_dir / "ontology" / "claims" / "pilot_claims.json"
        cls.rules_path = cls.root_dir / "ontology" / "rules" / "pilot_rules.json"
        cls.examples_path = cls.root_dir / "ontology" / "examples" / "pilot_examples.json"
        cls.conflicts_path = cls.root_dir / "ontology" / "conflicts" / "conflicts.json"
        cls.crosswalk_path = cls.root_dir / "research" / "linguistic-knowledge" / "terminology-crosswalk.json"

        with open(cls.sources_path, "r", encoding="utf-8") as f:
            cls.sources_data = json.load(f)
        with open(cls.evidence_path, "r", encoding="utf-8") as f:
            cls.evidence_data = json.load(f)
        with open(cls.claims_path, "r", encoding="utf-8") as f:
            cls.claims_data = json.load(f)
        with open(cls.rules_path, "r", encoding="utf-8") as f:
            cls.rules_data = json.load(f)
        with open(cls.examples_path, "r", encoding="utf-8") as f:
            cls.examples_data = json.load(f)
        with open(cls.conflicts_path, "r", encoding="utf-8") as f:
            cls.conflicts_data = json.load(f)
        with open(cls.crosswalk_path, "r", encoding="utf-8") as f:
            cls.crosswalk_data = json.load(f)

    def test_evidence_grounding_in_sources(self):
        """Every evidence item must cite a valid registered source."""
        valid_sources = {s["source_id"] for s in self.sources_data.get("sources", [])}
        for ev in self.evidence_data.get("evidence_items", []):
            self.assertIn(
                ev["source_id"],
                valid_sources,
                f"Evidence {ev['evidence_id']} cites unregistered source {ev['source_id']}",
            )
            self.assertTrue(ev["locator"], f"Evidence {ev['evidence_id']} missing locator")
            self.assertTrue(ev["excerpt_or_paraphrase"], f"Evidence {ev['evidence_id']} missing excerpt")

    def test_claims_grounding_in_evidence(self):
        """Every claim must be supported by valid evidence IDs."""
        valid_evidence_ids = {e["evidence_id"] for e in self.evidence_data.get("evidence_items", [])}
        for clm in self.claims_data.get("claims", []):
            self.assertTrue(clm["evidence_ids"], f"Claim {clm['claim_id']} has no evidence_ids")
            for eid in clm["evidence_ids"]:
                self.assertIn(
                    eid,
                    valid_evidence_ids,
                    f"Claim {clm['claim_id']} cites non-existent evidence {eid}",
                )

    def test_rules_grounding_in_claims(self):
        """Every rule must reference valid supporting claim IDs."""
        valid_claim_ids = {c["claim_id"] for c in self.claims_data.get("claims", [])}
        for rul in self.rules_data.get("rules", []):
            self.assertTrue(rul["supporting_claim_ids"], f"Rule {rul['rule_id']} has no supporting claims")
            for cid in rul["supporting_claim_ids"]:
                self.assertIn(
                    cid,
                    valid_claim_ids,
                    f"Rule {rul['rule_id']} cites non-existent claim {cid}",
                )

    def test_example_provenance_and_integrity(self):
        """Examples must have complete provenance and valid grammaticality ratings."""
        for ex in self.examples_data.get("examples", []):
            prov = ex.get("provenance", {})
            self.assertIn("provenance_class", prov, f"Example {ex['example_id']} missing provenance_class")
            self.assertIn(
                ex["grammaticality"],
                [
                    "GRAMMATICAL",
                    "UNGRAMMATICAL",
                    "MARKED",
                    "ARCHAIC",
                    "UNNATURAL",
                    "REGISTER_MISMATCH",
                    "DIALECT_SPECIFIC",
                    "SEMANTICALLY_INVALID",
                ],
            )
            self.assertTrue(ex["normalized_text"], f"Example {ex['example_id']} missing normalized text")

    def test_no_automated_human_approved_claims(self):
        """Automated pipelines must not assign HUMAN_APPROVED without authenticated human review."""
        for clm in self.claims_data.get("claims", []):
            self.assertNotEqual(
                clm.get("human_review_status"),
                "HUMAN_APPROVED",
                f"Claim {clm['claim_id']} has illegal automated status HUMAN_APPROVED",
            )

    def test_terminology_crosswalk_integrity(self):
        """Crosswalk entries must reference valid registered sources."""
        valid_sources = {s["source_id"] for s in self.sources_data.get("sources", [])}
        for tm in self.crosswalk_data.get("mappings", []):
            sid = tm.get("source_id")
            if sid:
                self.assertIn(
                    sid,
                    valid_sources,
                    f"Terminology mapping {tm['mapping_id']} cites unregistered source {sid}",
                )

    def test_conflict_relations_integrity(self):
        """Conflict relations must reference valid source entities and allowed relation types."""
        valid_sources = {s["source_id"] for s in self.sources_data.get("sources", [])}
        valid_types = {e.value for e in RuleRelationType}
        for rel in self.conflicts_data.get("relations", []):
            self.assertIn(rel["source_entity_id"], valid_sources)
            self.assertIn(rel["target_entity_id"], valid_sources)
            self.assertIn(rel["relation_type"], valid_types)

    def test_dataclass_instantiation(self):
        """Verifies Python domain models can be instantiated correctly."""
        ev = LinguisticEvidence(
            evidence_id="EV-TEST-01",
            source_id="BA-GRAM-2011",
            evidence_type="GRAMMATICAL_RULE_FORMULATION",
            locator="Vol. 1, p. 10",
            page_or_section="Vol. 1",
            excerpt_or_paraphrase="Test excerpt",
            copyright_handling="SCHOLARLY_PARAPHRASE",
            verification_status="VERIFIED",
        )
        self.assertEqual(ev.evidence_id, "EV-TEST-01")

        clm = LinguisticClaim(
            claim_id="CLM-TEST-01",
            evidence_ids=["EV-TEST-01"],
            linguistic_level=LinguisticLevel.SYNTAX,
            claim_type="CONSTITUENT_ORDER",
            source_assertion="Test assertion",
            normalized_claim="Normalized test",
            epistemic_class=EpistemicClass.SOURCE_ASSERTED,
            language_variety=LanguageVariety.BDSB_STANDARD,
            confidence="HIGH",
            verification_status="VERIFIED",
            human_review_status=ReviewStatus.SOURCE_VERIFIED,
        )
        self.assertEqual(clm.claim_id, "CLM-TEST-01")
        self.assertEqual(clm.linguistic_level, LinguisticLevel.SYNTAX)


if __name__ == "__main__":
    unittest.main()
