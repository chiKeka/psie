"""
PSIE — Layer 1: Graph Schema
==============================
Typed knowledge graph representation for major programmes.

Defines the formal ontology: node types, edge types, and the
ProgrammeGraph container built on NetworkX.

Theoretical basis:
  - Design Structure Matrices (Eppinger & Browning, 2012)
  - Network Science (Barabási, 2016)
  - S³ Framework vocabulary (Armanios et al., 2025)

Mathematical representation:
  G = (V, E, τ_V, τ_E, w)
  where V = nodes, E = directed edges, τ = type functions, w = weight function
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Iterator
import json
import networkx as nx


# ═══════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════

class NodeType(Enum):
    """Types of nodes in the programme graph."""
    # Components
    PROJECT            = "project"
    WORKSTREAM         = "workstream"
    CAPABILITY         = "capability"
    # Actors
    ORGANISATION       = "organisation"
    COMMUNITY          = "community"
    INDIVIDUAL         = "individual"
    # Governance
    POLICY             = "policy"
    MECHANISM          = "mechanism"
    METRIC             = "metric"
    # Resources
    FINANCIAL          = "financial"
    PHYSICAL           = "physical"
    INFORMATIONAL      = "informational"
    # Environment
    EXTERNAL_CONDITION = "external_condition"
    EXOGENOUS_EVENT    = "exogenous_event"


class NodeCategory(Enum):
    """High-level node categories."""
    COMPONENT   = "component"
    ACTOR       = "actor"
    GOVERNANCE  = "governance"
    RESOURCE    = "resource"
    ENVIRONMENT = "environment"


NODE_TYPE_TO_CATEGORY = {
    NodeType.PROJECT:            NodeCategory.COMPONENT,
    NodeType.WORKSTREAM:         NodeCategory.COMPONENT,
    NodeType.CAPABILITY:         NodeCategory.COMPONENT,
    NodeType.ORGANISATION:       NodeCategory.ACTOR,
    NodeType.COMMUNITY:          NodeCategory.ACTOR,
    NodeType.INDIVIDUAL:         NodeCategory.ACTOR,
    NodeType.POLICY:             NodeCategory.GOVERNANCE,
    NodeType.MECHANISM:          NodeCategory.GOVERNANCE,
    NodeType.METRIC:             NodeCategory.GOVERNANCE,
    NodeType.FINANCIAL:          NodeCategory.RESOURCE,
    NodeType.PHYSICAL:           NodeCategory.RESOURCE,
    NodeType.INFORMATIONAL:      NodeCategory.RESOURCE,
    NodeType.EXTERNAL_CONDITION: NodeCategory.ENVIRONMENT,
    NodeType.EXOGENOUS_EVENT:    NodeCategory.ENVIRONMENT,
}


class EdgeType(Enum):
    """Types of edges (dependency relationships) in the programme graph."""
    # Dependency
    CAUSAL_LINK        = "causal_link"
    RESOURCE_FLOW      = "resource_flow"
    INFORMATION_FLOW   = "information_flow"
    TEMPORAL_SEQUENCE  = "temporal_sequence"
    # Governance
    AUTHORITY_OVER     = "authority_over"
    OVERSIGHT_OF       = "oversight_of"
    ACCOUNTABLE_TO     = "accountable_to"
    # Support
    SCAFFOLDS          = "scaffolds"
    FUNDS_OPERATES     = "funds_operates"
    SKILL_MATCH        = "skill_match"
    # Vulnerability
    EXPOSED_TO         = "exposed_to"
    PROPAGATES_RISK_TO = "propagates_risk_to"
    AMPLIFIES          = "amplifies"
    # Social
    INFLUENCES_POLICY  = "influences_policy"
    REPRESENTS_INTEREST_OF = "represents_interest_of"
    EXCLUDED_FROM      = "excluded_from"


class EdgeCategory(Enum):
    """High-level edge categories."""
    DEPENDENCY    = "dependency"
    GOVERNANCE    = "governance"
    SUPPORT       = "support"
    VULNERABILITY = "vulnerability"
    SOCIAL        = "social"


EDGE_TYPE_TO_CATEGORY = {
    EdgeType.CAUSAL_LINK:           EdgeCategory.DEPENDENCY,
    EdgeType.RESOURCE_FLOW:         EdgeCategory.DEPENDENCY,
    EdgeType.INFORMATION_FLOW:      EdgeCategory.DEPENDENCY,
    EdgeType.TEMPORAL_SEQUENCE:     EdgeCategory.DEPENDENCY,
    EdgeType.AUTHORITY_OVER:        EdgeCategory.GOVERNANCE,
    EdgeType.OVERSIGHT_OF:          EdgeCategory.GOVERNANCE,
    EdgeType.ACCOUNTABLE_TO:        EdgeCategory.GOVERNANCE,
    EdgeType.SCAFFOLDS:             EdgeCategory.SUPPORT,
    EdgeType.FUNDS_OPERATES:        EdgeCategory.SUPPORT,
    EdgeType.SKILL_MATCH:           EdgeCategory.SUPPORT,
    EdgeType.EXPOSED_TO:            EdgeCategory.VULNERABILITY,
    EdgeType.PROPAGATES_RISK_TO:    EdgeCategory.VULNERABILITY,
    EdgeType.AMPLIFIES:             EdgeCategory.VULNERABILITY,
    EdgeType.INFLUENCES_POLICY:     EdgeCategory.SOCIAL,
    EdgeType.REPRESENTS_INTEREST_OF: EdgeCategory.SOCIAL,
    EdgeType.EXCLUDED_FROM:         EdgeCategory.SOCIAL,
}


class RuleType(Enum):
    """The five simple rule types from S³ scoping (Armanios et al., 2025)."""
    HOW_TO   = "how_to"
    BOUNDARY = "boundary"
    PRIORITY = "priority"
    TIMING   = "timing"
    EXIT     = "exit"


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class ProgrammeNode:
    """
    A node in the programme knowledge graph.

    Attributes correspond to the formal specification:
      v ∈ V, with attributes (criticality, vulnerability, absorptive_capacity) ∈ [0,1]³
    """
    id: str
    label: str
    node_type: NodeType
    family: str = ""
    description: str = ""
    criticality: float = 0.5
    vulnerability: float = 0.5
    absorptive_capacity: float = 0.5
    source: str = ""
    confidence: float = 1.0

    @property
    def category(self) -> NodeCategory:
        return NODE_TYPE_TO_CATEGORY[self.node_type]

    def to_dict(self) -> dict:
        """Serialise to dictionary for NetworkX node attributes."""
        return {
            "label": self.label,
            "node_type": self.node_type.value,
            "category": self.category.value,
            "family": self.family,
            "description": self.description,
            "criticality": self.criticality,
            "vulnerability": self.vulnerability,
            "absorptive_capacity": self.absorptive_capacity,
            "source": self.source,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, node_id: str, d: dict) -> ProgrammeNode:
        """Reconstruct from dictionary (e.g. JSON data file)."""
        return cls(
            id=node_id,
            label=d["label"],
            node_type=NodeType(d["node_type"]),
            family=d.get("family", ""),
            description=d.get("description", ""),
            criticality=d.get("criticality", 0.5),
            vulnerability=d.get("vulnerability", 0.5),
            absorptive_capacity=d.get("absorptive_capacity", 0.5),
            source=d.get("source", ""),
            confidence=d.get("confidence", 1.0),
        )


@dataclass
class ProgrammeEdge:
    """
    A directed edge in the programme knowledge graph.

    Represents a typed dependency: e = (u, v, τ_E, w, p)
    where p = propagation_rate ∈ [0,1].
    """
    id: str
    source: str
    target: str
    edge_type: EdgeType
    weight: float = 0.5
    propagation_rate: float = 0.5
    rule_type: Optional[RuleType] = None
    bidirectional: bool = False
    evidence: str = ""
    confidence: float = 1.0

    @property
    def category(self) -> EdgeCategory:
        return EDGE_TYPE_TO_CATEGORY[self.edge_type]

    def to_dict(self) -> dict:
        """Serialise to dictionary for NetworkX edge attributes."""
        return {
            "edge_id": self.id,
            "edge_type": self.edge_type.value,
            "category": self.category.value,
            "weight": self.weight,
            "propagation_rate": self.propagation_rate,
            "rule_type": self.rule_type.value if self.rule_type else None,
            "bidirectional": self.bidirectional,
            "evidence": self.evidence,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, edge_id: str, d: dict) -> ProgrammeEdge:
        """Reconstruct from dictionary."""
        rt = d.get("rule_type")
        return cls(
            id=edge_id,
            source=d["source"],
            target=d["target"],
            edge_type=EdgeType(d["edge_type"]),
            weight=d.get("weight", 0.5),
            propagation_rate=d.get("propagation_rate", 0.5),
            rule_type=RuleType(rt) if rt else None,
            bidirectional=d.get("bidirectional", False),
            evidence=d.get("evidence", ""),
            confidence=d.get("confidence", 1.0),
        )


# ═══════════════════════════════════════════════════════════════════════
# PROGRAMME GRAPH
# ═══════════════════════════════════════════════════════════════════════

class ProgrammeGraph:
    """
    The core knowledge graph for a major programme.

    Wraps a NetworkX DiGraph with typed node/edge semantics and provides
    serialisation to/from JSON for portable case-study data.
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.G: nx.DiGraph = nx.DiGraph()
        self._nodes: dict[str, ProgrammeNode] = {}
        self._edges: dict[str, ProgrammeEdge] = {}

    # ── Construction ─────────────────────────────────────────────────

    def add_node(self, node: ProgrammeNode) -> None:
        """Add a typed node to the graph."""
        self._nodes[node.id] = node
        self.G.add_node(node.id, **node.to_dict())

    def add_edge(self, edge: ProgrammeEdge) -> None:
        """Add a typed directed edge. Creates reverse edge if bidirectional."""
        self._edges[edge.id] = edge
        self.G.add_edge(edge.source, edge.target, **edge.to_dict())
        if edge.bidirectional:
            rev = edge.to_dict()
            rev["edge_id"] = f"{edge.id}_rev"
            self.G.add_edge(edge.target, edge.source, **rev)

    def get_node(self, node_id: str) -> Optional[ProgrammeNode]:
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[ProgrammeEdge]:
        return self._edges.get(edge_id)

    # ── Properties ───────────────────────────────────────────────────

    @property
    def node_count(self) -> int:
        return self.G.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self.G.number_of_edges()

    @property
    def density(self) -> float:
        return nx.density(self.G)

    def nodes(self) -> Iterator[ProgrammeNode]:
        return iter(self._nodes.values())

    def edges(self) -> Iterator[ProgrammeEdge]:
        return iter(self._edges.values())

    def families(self) -> set[str]:
        """Return all unique family labels in the graph."""
        return {n.family for n in self._nodes.values() if n.family}

    # ── Serialisation ────────────────────────────────────────────────

    def to_json(self, path: str) -> None:
        """Export graph to a portable JSON file."""
        data = {
            "name": self.name,
            "description": self.description,
            "nodes": {nid: n.to_dict() for nid, n in self._nodes.items()},
            "edges": {eid: {**e.to_dict(), "source": e.source, "target": e.target}
                      for eid, e in self._edges.items()},
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def from_json(cls, path: str) -> ProgrammeGraph:
        """Load a programme graph from a JSON file."""
        with open(path) as f:
            data = json.load(f)
        pg = cls(name=data["name"], description=data.get("description", ""))
        for nid, ndata in data["nodes"].items():
            pg.add_node(ProgrammeNode.from_dict(nid, ndata))
        for eid, edata in data["edges"].items():
            pg.add_edge(ProgrammeEdge.from_dict(eid, edata))
        return pg

    # ── Summary ──────────────────────────────────────────────────────

    def summary(self) -> str:
        """Human-readable structural summary."""
        from collections import Counter
        cat_counts = Counter(
            self.G.nodes[n].get("category", "?") for n in self.G.nodes()
        )
        edge_cats = Counter(
            d.get("category", "?") for _, _, d in self.G.edges(data=True)
        )
        lines = [
            f"Programme: {self.name}",
            f"Nodes: {self.node_count}  |  Edges: {self.edge_count}  |  Density: {self.density:.4f}",
            "",
            "Node breakdown:  " + ", ".join(f"{c} ({n})" for c, n in cat_counts.most_common()),
            "Edge breakdown:  " + ", ".join(f"{c} ({n})" for c, n in edge_cats.most_common()),
            "",
            f"Weakly connected: {nx.is_weakly_connected(self.G)}",
            f"Components: {nx.number_weakly_connected_components(self.G)}",
        ]
        return "\n".join(lines)
