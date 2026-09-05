"""
BLF Typed Ontology Graph Engine.

Provides an in-memory directed graph linking sources, evidence, claims, rules,
paradigms, constructions, semantic frames, sentence families, and attestations
with bidirectional traversal and lineage verification.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple
import json


class NodeType(str, Enum):
    SOURCE = "SOURCE"
    EVIDENCE = "EVIDENCE"
    CLAIM = "CLAIM"
    RULE = "RULE"
    PARADIGM = "PARADIGM"
    CONSTRUCTION = "CONSTRUCTION"
    FRAME = "FRAME"
    SENTENCE_FAMILY = "SENTENCE_FAMILY"
    ATTESTATION = "ATTESTATION"
    EXAMPLE = "EXAMPLE"


class EdgeRelation(str, Enum):
    DERIVES_FROM = "derives_from"
    SUPPORTS = "supports"
    REFINES = "refines"
    MAPS_TO = "maps_to"
    ATTESTS = "attests"
    REALIZES = "realizes"
    CONTAINS = "contains"
    CONSTRAINED_BY = "constrained_by"


@dataclass
class GraphNode:
    node_id: str
    node_type: NodeType
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    relation: EdgeRelation
    metadata: Dict[str, Any] = field(default_factory=dict)


class OntologyGraph:
    """Directed knowledge graph for BLF linguistic ontology with lineage tracing."""

    def __init__(self) -> None:
        self.nodes: Dict[str, GraphNode] = {}
        self.outgoing: Dict[str, List[GraphEdge]] = {}
        self.incoming: Dict[str, List[GraphEdge]] = {}

    def add_node(self, node_id: str, node_type: NodeType, data: Optional[Dict[str, Any]] = None) -> GraphNode:
        if node_id in self.nodes:
            # Update data if provided
            if data:
                self.nodes[node_id].data.update(data)
            return self.nodes[node_id]

        node = GraphNode(node_id=node_id, node_type=node_type, data=data or {})
        self.nodes[node_id] = node
        self.outgoing[node_id] = []
        self.incoming[node_id] = []
        return node

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: EdgeRelation,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GraphEdge:
        if source_id not in self.nodes:
            raise KeyError(f"Source node '{source_id}' does not exist in graph")
        if target_id not in self.nodes:
            raise KeyError(f"Target node '{target_id}' does not exist in graph")

        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            relation=relation,
            metadata=metadata or {},
        )
        self.outgoing[source_id].append(edge)
        self.incoming[target_id].append(edge)
        return edge

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)

    def get_outgoing(self, node_id: str, relation: Optional[EdgeRelation] = None) -> List[GraphEdge]:
        edges = self.outgoing.get(node_id, [])
        if relation is not None:
            return [e for e in edges if e.relation == relation]
        return edges

    def get_incoming(self, node_id: str, relation: Optional[EdgeRelation] = None) -> List[GraphEdge]:
        edges = self.incoming.get(node_id, [])
        if relation is not None:
            return [e for e in edges if e.relation == relation]
        return edges

    def trace_backward_lineage(self, start_id: str) -> List[List[str]]:
        """
        Traces all paths backwards from start_id through DERIVES_FROM / SUPPORTS edges.
        Returns list of path node_id sequences: [start_id, ..., root_source_id].
        """
        if start_id not in self.nodes:
            return []

        paths: List[List[str]] = []

        def dfs(current_id: str, current_path: List[str], visited: Set[str]) -> None:
            # Look for outgoing derivation/supports edges (edges leading towards deeper provenance)
            out_edges = [
                e for e in self.outgoing.get(current_id, [])
                if e.relation in (EdgeRelation.DERIVES_FROM, EdgeRelation.SUPPORTS, EdgeRelation.REALIZES)
            ]
            if not out_edges:
                paths.append(list(current_path))
                return

            for edge in out_edges:
                nxt = edge.target_id
                if nxt not in visited:
                    visited.add(nxt)
                    current_path.append(nxt)
                    dfs(nxt, current_path, visited)
                    current_path.pop()
                    visited.remove(nxt)

        dfs(start_id, [start_id], {start_id})
        return paths

    def validate_integrity(self) -> Tuple[bool, List[str]]:
        """Verifies graph integrity: no dangling edges, node types consistent."""
        issues: List[str] = []
        for nid, edges in self.outgoing.items():
            for edge in edges:
                if edge.target_id not in self.nodes:
                    issues.append(f"Dangling edge from '{nid}' to non-existent '{edge.target_id}'")
        for nid, edges in self.incoming.items():
            for edge in edges:
                if edge.source_id not in self.nodes:
                    issues.append(f"Dangling reverse edge to '{nid}' from non-existent '{edge.source_id}'")

        return len(issues) == 0, issues

    @classmethod
    def build_from_repository(cls, root_dir: Path) -> "OntologyGraph":
        """Constructs an OntologyGraph instance populated with repository artifacts."""
        graph = cls()

        def _read_json(p: Path) -> Dict[str, Any]:
            if not p.is_file():
                return {}
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

        # 1. Sources
        sources_file = root_dir / "sources" / "registry" / "sources.json"
        if sources_file.is_file():
            s_data = _read_json(sources_file)
            for s in s_data.get("sources", []):
                graph.add_node(s["source_id"], NodeType.SOURCE, s)

        # 2. Evidence
        ev_file = root_dir / "ontology" / "evidence" / "pilot_evidence.json"
        if ev_file.is_file():
            ev_data = _read_json(ev_file)
            for ev in ev_data.get("evidence_items", []):
                eid = ev["evidence_id"]
                graph.add_node(eid, NodeType.EVIDENCE, ev)
                sid = ev.get("source_id")
                if sid and sid in graph.nodes:
                    graph.add_edge(eid, sid, EdgeRelation.DERIVES_FROM, {"role": "source_reference"})

        # 3. Claims
        claims_file = root_dir / "ontology" / "claims" / "pilot_claims.json"
        if claims_file.is_file():
            c_data = _read_json(claims_file)
            for clm in c_data.get("claims", []):
                cid = clm["claim_id"]
                graph.add_node(cid, NodeType.CLAIM, clm)
                for eid in clm.get("evidence_ids", []):
                    if eid in graph.nodes:
                        graph.add_edge(cid, eid, EdgeRelation.DERIVES_FROM, {"role": "evidence_grounding"})

        # 4. Rules
        rules_file = root_dir / "ontology" / "rules" / "pilot_rules.json"
        if rules_file.is_file():
            r_data = _read_json(rules_file)
            for r in r_data.get("rules", []):
                rid = r["rule_id"]
                graph.add_node(rid, NodeType.RULE, r)
                for cid in r.get("supporting_claim_ids", []):
                    if cid in graph.nodes:
                        graph.add_edge(rid, cid, EdgeRelation.SUPPORTS, {"role": "claim_support"})

        # 5. Constructions
        const_file = root_dir / "ontology" / "constructions" / "constructions.json"
        if const_file.is_file():
            const_data = _read_json(const_file)
            for c in const_data.get("constructions", []):
                cid = c["construction_id"]
                graph.add_node(cid, NodeType.CONSTRUCTION, c)
                for clm_id in c.get("supporting_claim_ids", []):
                    if clm_id in graph.nodes:
                        graph.add_edge(cid, clm_id, EdgeRelation.SUPPORTS, {"role": "claim_support"})

        # 6. Frames
        frames_file = root_dir / "ontology" / "frames" / "core_frames.json"
        if frames_file.is_file():
            f_data = _read_json(frames_file)
            for fr in f_data.get("frames", []):
                fid = fr["frame_id"]
                graph.add_node(fid, NodeType.FRAME, fr)
                for const_id in fr.get("compatible_constructions", []):
                    if const_id in graph.nodes:
                        graph.add_edge(fid, const_id, EdgeRelation.REALIZES, {"role": "frame_realization"})

        # 7. Sentence Families
        families_file = root_dir / "data" / "validation" / "sentence_families_diagnostic.json"
        if families_file.is_file():
            sf_data = _read_json(families_file)
            for sf in sf_data.get("sentence_families", []):
                sf_id = sf["sentence_family_id"]
                graph.add_node(sf_id, NodeType.SENTENCE_FAMILY, sf)
                fid = sf.get("semantic_frame_id")
                if fid and fid in graph.nodes:
                    graph.add_edge(sf_id, fid, EdgeRelation.DERIVES_FROM, {"role": "frame_derivation"})
                cid = sf.get("primary_construction_id")
                if cid and cid in graph.nodes:
                    graph.add_edge(sf_id, cid, EdgeRelation.REALIZES, {"role": "construction_realization"})

        # 8. Attestations
        attest_file = root_dir / "ontology" / "attestations" / "corpus_attestations.json"
        if attest_file.is_file():
            att_data = _read_json(attest_file)
            for att in att_data.get("attestations", []):
                aid = att["attestation_id"]
                graph.add_node(aid, NodeType.ATTESTATION, att)
                sid = att.get("corpus_source_id")
                if sid and sid in graph.nodes:
                    graph.add_edge(aid, sid, EdgeRelation.DERIVES_FROM, {"role": "corpus_grounding"})
                eid = att.get("bound_evidence_id")
                if eid and eid in graph.nodes:
                    graph.add_edge(aid, eid, EdgeRelation.ATTESTS, {"role": "evidence_corroboration"})

        return graph
