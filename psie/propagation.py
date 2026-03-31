"""
PSIE — Layer 2: Propagation Engine
====================================
Cascade simulation through the typed dependency graph.

Implements the propagation equation from the idea document:

  Impact(v, t+1) = Σ_{u ∈ N⁻(v)} w(u,v) · Impact(u,t) · (1 − α(v))

where:
  N⁻(v)  = in-neighbours of v
  w(u,v) = edge propagation rate
  α(v)   = absorptive capacity of v

Theoretical basis:
  - Buldyrev et al. (2010) — cascading failure in interdependent networks
  - Barabási (2016) — Network Science
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from collections import defaultdict
from typing import Optional

from .graph_schema import ProgrammeGraph, EdgeType
from .config import CASCADE_DEFAULTS


# ═══════════════════════════════════════════════════════════════════════
# DISRUPTION TYPES
# ═══════════════════════════════════════════════════════════════════════

class DisruptionType(Enum):
    """Classification of disruption events."""
    DELAY                = "delay"
    COST_OVERRUN         = "cost_overrun"
    POLITICAL_RISK       = "political_risk"
    INFORMATION_GAP      = "information_gap"
    STAKEHOLDER_CONFLICT = "stakeholder_conflict"
    RESOURCE_SHORTAGE    = "resource_shortage"
    EXTERNAL_SHOCK       = "external_shock"


# Which edge types each disruption type primarily propagates through
DISRUPTION_PRIMARY_PATHS: dict[DisruptionType, list[EdgeType]] = {
    DisruptionType.DELAY: [
        EdgeType.TEMPORAL_SEQUENCE, EdgeType.CAUSAL_LINK,
    ],
    DisruptionType.COST_OVERRUN: [
        EdgeType.RESOURCE_FLOW, EdgeType.FUNDS_OPERATES,
    ],
    DisruptionType.POLITICAL_RISK: [
        EdgeType.INFLUENCES_POLICY, EdgeType.AUTHORITY_OVER,
    ],
    DisruptionType.INFORMATION_GAP: [
        EdgeType.INFORMATION_FLOW, EdgeType.SCAFFOLDS,
    ],
    DisruptionType.STAKEHOLDER_CONFLICT: [
        EdgeType.REPRESENTS_INTEREST_OF, EdgeType.EXCLUDED_FROM,
    ],
    DisruptionType.RESOURCE_SHORTAGE: [
        EdgeType.RESOURCE_FLOW, EdgeType.SKILL_MATCH,
    ],
    DisruptionType.EXTERNAL_SHOCK: [
        EdgeType.EXPOSED_TO, EdgeType.PROPAGATES_RISK_TO,
    ],
}


@dataclass
class Disruption:
    """A disruption event to be injected into the programme graph."""
    id: str
    label: str
    disruption_type: DisruptionType
    injection_node: str
    magnitude: float = 0.5
    description: str = ""

    @property
    def primary_paths(self) -> list[EdgeType]:
        return DISRUPTION_PRIMARY_PATHS[self.disruption_type]


# ═══════════════════════════════════════════════════════════════════════
# CASCADE ENGINE
# ═══════════════════════════════════════════════════════════════════════

class CascadeEngine:
    """
    Simulates cascading disruptions through a ProgrammeGraph.

    Uses breadth-first propagation with typed edge filtering,
    absorptive capacity damping, and configurable thresholds.
    """

    def __init__(
        self,
        graph: ProgrammeGraph,
        absorption_threshold: float = CASCADE_DEFAULTS["absorption_threshold"],
        max_steps: int = CASCADE_DEFAULTS["max_steps"],
        off_path_penalty: float = CASCADE_DEFAULTS["off_path_penalty"],
    ):
        self.pg = graph
        self.threshold = absorption_threshold
        self.max_steps = max_steps
        self.off_path_penalty = off_path_penalty

    def simulate(self, disruption: Disruption) -> CascadeResult:
        """
        Simulate a disruption propagating through the programme graph.

        Returns a CascadeResult containing the full cascade path,
        impact-by-family breakdown, and summary statistics.
        """
        G = self.pg.G
        primary_types = {et.value for et in disruption.primary_paths}

        node_impact: dict[str, float] = {}
        cascade_path: list[dict] = []
        frontier = [(disruption.injection_node, disruption.magnitude, 0)]
        visited: set[str] = set()
        steps_remaining = self.max_steps

        while frontier and steps_remaining > 0:
            next_frontier = []
            for node_id, incoming_impact, step in frontier:
                if node_id in visited:
                    continue
                visited.add(node_id)

                # Apply absorptive capacity: Impact × (1 − α)
                node_data = G.nodes.get(node_id, {})
                alpha = node_data.get("absorptive_capacity", 0.5)
                absorbed_impact = incoming_impact * (1.0 - alpha)

                if absorbed_impact < self.threshold:
                    continue  # Fully absorbed

                node_impact[node_id] = absorbed_impact
                cascade_path.append({
                    "node_id": node_id,
                    "label": node_data.get("label", node_id),
                    "step": step,
                    "impact": round(absorbed_impact, 4),
                    "family": node_data.get("family", ""),
                })

                # Propagate to out-neighbours
                for _, target, edge_data in G.out_edges(node_id, data=True):
                    if target in visited:
                        continue
                    edge_type = edge_data.get("edge_type", "")
                    rate = edge_data.get("propagation_rate", 0.5)

                    # Apply penalty for non-primary paths
                    if edge_type not in primary_types:
                        rate *= self.off_path_penalty

                    outgoing = absorbed_impact * rate
                    if outgoing > self.threshold:
                        next_frontier.append((target, outgoing, step + 1))

            frontier = next_frontier
            steps_remaining -= 1

        # Aggregate by family
        impact_by_family: dict[str, float] = defaultdict(float)
        for entry in cascade_path:
            impact_by_family[entry["family"]] += entry["impact"]

        return CascadeResult(
            disruption_label=disruption.label,
            injection_node=disruption.injection_node,
            cascade_path=cascade_path,
            total_nodes_affected=len(cascade_path),
            cascade_depth=max((e["step"] for e in cascade_path), default=0),
            impact_by_family={k: round(v, 4) for k, v in impact_by_family.items()},
            node_impact=node_impact,
        )


@dataclass
class CascadeResult:
    """Container for cascade simulation results."""
    disruption_label: str
    injection_node: str
    cascade_path: list[dict]
    total_nodes_affected: int
    cascade_depth: int
    impact_by_family: dict[str, float]
    node_impact: dict[str, float]

    def summary(self) -> str:
        lines = [
            f"Disruption: {self.disruption_label}",
            f"  Injection:       {self.injection_node}",
            f"  Nodes affected:  {self.total_nodes_affected}",
            f"  Cascade depth:   {self.cascade_depth} steps",
            f"  Impact by family:",
        ]
        for fam, imp in sorted(self.impact_by_family.items(), key=lambda x: -x[1]):
            lines.append(f"    {fam:25s} {imp:.4f}")
        return "\n".join(lines)
