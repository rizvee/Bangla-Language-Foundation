"""
Unit tests for BLF Ontology Graph Engine.
"""

import unittest
from pathlib import Path

from blf.ontology.graph import EdgeRelation, NodeType, OntologyGraph


class TestOntologyGraph(unittest.TestCase):

    def setUp(self) -> None:
        self.root_dir = Path(__file__).resolve().parent.parent
        self.graph = OntologyGraph()

    def test_add_nodes_and_edges(self) -> None:
        n1 = self.graph.add_node("source_1", NodeType.SOURCE, {"title": "Test Source"})
        n2 = self.graph.add_node("evidence_1", NodeType.EVIDENCE, {"excerpt": "Test excerpt"})
        self.assertEqual(n1.node_id, "source_1")
        self.assertEqual(n2.node_id, "evidence_1")

        edge = self.graph.add_edge("evidence_1", "source_1", EdgeRelation.DERIVES_FROM)
        self.assertEqual(edge.relation, EdgeRelation.DERIVES_FROM)
        self.assertEqual(len(self.graph.get_outgoing("evidence_1")), 1)
        self.assertEqual(len(self.graph.get_incoming("source_1")), 1)

    def test_missing_node_raises_error(self) -> None:
        self.graph.add_node("node_a", NodeType.CLAIM)
        with self.assertRaises(KeyError):
            self.graph.add_edge("node_a", "non_existent", EdgeRelation.SUPPORTS)

    def test_integrity_validation(self) -> None:
        self.graph.add_node("c1", NodeType.CLAIM)
        self.graph.add_node("e1", NodeType.EVIDENCE)
        self.graph.add_edge("c1", "e1", EdgeRelation.DERIVES_FROM)
        valid, issues = self.graph.validate_integrity()
        self.assertTrue(valid)
        self.assertEqual(len(issues), 0)

    def test_backward_lineage_trace(self) -> None:
        self.graph.add_node("source_1", NodeType.SOURCE)
        self.graph.add_node("evidence_1", NodeType.EVIDENCE)
        self.graph.add_node("claim_1", NodeType.CLAIM)
        self.graph.add_node("rule_1", NodeType.RULE)

        self.graph.add_edge("evidence_1", "source_1", EdgeRelation.DERIVES_FROM)
        self.graph.add_edge("claim_1", "evidence_1", EdgeRelation.DERIVES_FROM)
        self.graph.add_edge("rule_1", "claim_1", EdgeRelation.SUPPORTS)

        paths = self.graph.trace_backward_lineage("rule_1")
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0], ["rule_1", "claim_1", "evidence_1", "source_1"])

    def test_build_from_repository(self) -> None:
        repo_graph = OntologyGraph.build_from_repository(self.root_dir)
        valid, issues = repo_graph.validate_integrity()
        self.assertTrue(valid, f"Repository graph validation issues: {issues}")
        self.assertGreater(len(repo_graph.nodes), 50)
        # Check backward lineage from diagnostic sentence family
        paths = repo_graph.trace_backward_lineage("SF-00001-BOOK-READ")
        self.assertGreater(len(paths), 0)
        self.assertEqual(paths[0][0], "SF-00001-BOOK-READ")


if __name__ == "__main__":
    unittest.main()
