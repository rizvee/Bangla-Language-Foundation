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


class CycleDetectedError(Exception):
    """Raised when an edge insertion would introduce a directed cycle into the DAG."""
    pass


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


@dataclass
class GraphAuditResult:
    node_counts_by_type: Dict[str, int]
    edge_counts_by_relation: Dict[str, int]
    missing_required_links: List[str]
    missing_optional_links: List[str]
    cycles_detected: bool
    cycle_paths: List[List[str]]
    orphan_nodes: List[str]
    untraceable_claims: List[str]
    untraceable_rules: List[str]
    unresolved_references: List[str] = field(default_factory=list)


class OntologyGraph:
    """Directed knowledge graph for BLF linguistic ontology with lineage tracing."""

    def __init__(self) -> None:
        self.nodes: Dict[str, GraphNode] = {}
        self.outgoing: Dict[str, List[GraphEdge]] = {}
        self.incoming: Dict[str, List[GraphEdge]] = {}
        self.unresolved_references: List[str] = []

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
        check_cycle: bool = True,
    ) -> GraphEdge:
        if source_id not in self.nodes:
            raise KeyError(f"Source node '{source_id}' does not exist in graph")
        if target_id not in self.nodes:
            raise KeyError(f"Target node '{target_id}' does not exist in graph")

        # 1. Deduplication: idempotent if identical edge already exists
        for existing in self.outgoing.get(source_id, []):
            if existing.target_id == target_id and existing.relation == relation:
                if metadata:
                    existing.metadata.update(metadata)
                return existing

        # 2. Cycle detection: adding source_id -> target_id creates cycle if path exists target_id -> source_id
        if check_cycle and self._has_path(target_id, source_id):
            raise CycleDetectedError(
                f"Cannot add edge '{source_id}' -> '{target_id}' ({relation.value}): creates a directed cycle in DAG."
            )

        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            relation=relation,
            metadata=metadata or {},
        )
        self.outgoing[source_id].append(edge)
        self.incoming[target_id].append(edge)
        return edge

    def _has_path(self, start_id: str, end_id: str) -> bool:
        """Returns True if there is a directed path from start_id to end_id."""
        if start_id == end_id:
            return True
        visited: Set[str] = set()
        queue: List[str] = [start_id]
        while queue:
            curr = queue.pop(0)
            if curr == end_id:
                return True
            if curr in visited:
                continue
            visited.add(curr)
            for edge in self.outgoing.get(curr, []):
                if edge.target_id not in visited:
                    queue.append(edge.target_id)
        return False

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

    def audit_graph(self) -> GraphAuditResult:
        """
        Performs a comprehensive audit of graph invariants:
        - node counts by type
        - edge counts by relation
        - cycles detected
        - orphan nodes (0 in, 0 out)
        - untraceable claims (missing evidence links)
        - untraceable rules (missing claim links)
        - missing required vs optional links
        - unresolved references
        """
        node_counts = {nt.value: 0 for nt in NodeType}
        for n in self.nodes.values():
            node_counts[n.node_type.value] += 1

        edge_counts = {er.value: 0 for er in EdgeRelation}
        for edges in self.outgoing.values():
            for e in edges:
                edge_counts[e.relation.value] += 1

        orphan_nodes = [
            nid for nid in self.nodes
            if len(self.outgoing.get(nid, [])) == 0 and len(self.incoming.get(nid, [])) == 0
        ]

        # Untraceable claims: claims without DERIVES_FROM edge to evidence
        untraceable_claims = []
        for nid, n in self.nodes.items():
            if n.node_type == NodeType.CLAIM:
                has_ev = any(
                    e.relation == EdgeRelation.DERIVES_FROM and self.nodes.get(e.target_id) and self.nodes[e.target_id].node_type == NodeType.EVIDENCE
                    for e in self.outgoing.get(nid, [])
                )
                if not has_ev:
                    untraceable_claims.append(nid)

        # Untraceable rules: rules without SUPPORTS edge to claims
        untraceable_rules = []
        for nid, n in self.nodes.items():
            if n.node_type == NodeType.RULE:
                has_claim = any(
                    e.relation == EdgeRelation.SUPPORTS and self.nodes.get(e.target_id) and self.nodes[e.target_id].node_type == NodeType.CLAIM
                    for e in self.outgoing.get(nid, [])
                )
                if not has_claim:
                    untraceable_rules.append(nid)

        # Check for cycles across whole graph
        cycles_detected = False
        cycle_paths: List[List[str]] = []
        visited_global: Set[str] = set()
        rec_stack: Set[str] = set()
        path_stack: List[str] = []

        def cycle_dfs(node: str) -> None:
            nonlocal cycles_detected
            visited_global.add(node)
            rec_stack.add(node)
            path_stack.append(node)

            for e in self.outgoing.get(node, []):
                nxt = e.target_id
                if nxt not in visited_global:
                    cycle_dfs(nxt)
                elif nxt in rec_stack:
                    cycles_detected = True
                    idx = path_stack.index(nxt)
                    cycle_paths.append(list(path_stack[idx:] + [nxt]))

            path_stack.pop()
            rec_stack.remove(node)

        for nid in self.nodes:
            if nid not in visited_global:
                cycle_dfs(nid)

        missing_required = []
        missing_optional = []

        # Evidence must have source
        for nid, n in self.nodes.items():
            if n.node_type == NodeType.EVIDENCE:
                has_src = any(
                    e.relation == EdgeRelation.DERIVES_FROM and self.nodes.get(e.target_id) and self.nodes[e.target_id].node_type == NodeType.SOURCE
                    for e in self.outgoing.get(nid, [])
                )
                if not has_src:
                    missing_required.append(f"Evidence '{nid}' missing source grounding")

        for c in untraceable_claims:
            missing_required.append(f"Claim '{c}' missing evidence grounding")
        for r in untraceable_rules:
            missing_required.append(f"Rule '{r}' missing claim support")

        return GraphAuditResult(
            node_counts_by_type=node_counts,
            edge_counts_by_relation=edge_counts,
            missing_required_links=missing_required,
            missing_optional_links=missing_optional,
            cycles_detected=cycles_detected,
            cycle_paths=cycle_paths,
            orphan_nodes=orphan_nodes,
            untraceable_claims=untraceable_claims,
            untraceable_rules=untraceable_rules,
            unresolved_references=list(self.unresolved_references),
        )

    @classmethod
    def build_from_repository(cls, root_dir: Path, strict: bool = False) -> "OntologyGraph":
        """Constructs an OntologyGraph instance populated with repository artifacts."""
        graph = cls()

        def _read_json(p: Path) -> Dict[str, Any]:
            if not p.is_file():
                return {}
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

        def _handle_missing_ref(source_info: str, missing_ref: str) -> None:
            msg = f"{source_info} references missing node '{missing_ref}'"
            if strict:
                raise KeyError(msg)
            graph.unresolved_references.append(msg)

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
                if sid:
                    if sid in graph.nodes:
                        graph.add_edge(eid, sid, EdgeRelation.DERIVES_FROM, {"role": "source_reference"})
                    else:
                        _handle_missing_ref(f"Evidence '{eid}'", sid)

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
                    else:
                        _handle_missing_ref(f"Claim '{cid}'", eid)

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
                    else:
                        _handle_missing_ref(f"Rule '{rid}'", cid)

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
                    else:
                        _handle_missing_ref(f"Construction '{cid}'", clm_id)

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
                    else:
                        _handle_missing_ref(f"Frame '{fid}'", const_id)

        # 7. Sentence Families
        families_file = root_dir / "data" / "validation" / "sentence_families_diagnostic.json"
        if families_file.is_file():
            sf_data = _read_json(families_file)
            for sf in sf_data.get("sentence_families", []):
                sf_id = sf["sentence_family_id"]
                graph.add_node(sf_id, NodeType.SENTENCE_FAMILY, sf)
                fid = sf.get("semantic_frame_id")
                if fid:
                    if fid in graph.nodes:
                        graph.add_edge(sf_id, fid, EdgeRelation.DERIVES_FROM, {"role": "frame_derivation"})
                    else:
                        _handle_missing_ref(f"SentenceFamily '{sf_id}'", fid)
                cid = sf.get("primary_construction_id")
                if cid:
                    if cid in graph.nodes:
                        graph.add_edge(sf_id, cid, EdgeRelation.REALIZES, {"role": "construction_realization"})
                    else:
                        _handle_missing_ref(f"SentenceFamily '{sf_id}'", cid)

        # 8. Attestations
        attest_file = root_dir / "ontology" / "attestations" / "corpus_attestations.json"
        if attest_file.is_file():
            att_data = _read_json(attest_file)
            for att in att_data.get("attestations", []):
                aid = att["attestation_id"]
                graph.add_node(aid, NodeType.ATTESTATION, att)
                sid = att.get("corpus_source_id")
                if sid:
                    if sid in graph.nodes:
                        graph.add_edge(aid, sid, EdgeRelation.DERIVES_FROM, {"role": "corpus_grounding"})
                    else:
                        _handle_missing_ref(f"Attestation '{aid}'", sid)
                eid = att.get("bound_evidence_id")
                if eid:
                    if eid in graph.nodes:
                        graph.add_edge(aid, eid, EdgeRelation.ATTESTS, {"role": "evidence_corroboration"})
                    else:
                        _handle_missing_ref(f"Attestation '{aid}'", eid)

        return graph

    # Backward-compatible alias
    load_from_repository = build_from_repository
