"""
PSIE — Layer 3 Bridge: System Dynamics Stub
=============================================
Stub module for the system-dynamics temporal model (Layer 3).

This module provides the interface that will eventually integrate
stock-and-flow feedback loops (Forrester, 1961; Sterman, 2000) with
the cascade engine. For the MVP, it generates placeholder conditional
probability tables (CPTs) from graph topology, which will later be
replaced by ODE-derived temporal dynamics.

Phase 2 Research Stream 2 will implement:
  - SIR-style node state transitions (Active → Stressed → Degraded → Failed)
  - Feedback loop detection and amplification modelling
  - Time-delay propagation
  - Integration with scipy.integrate for ODE solving
"""

from __future__ import annotations

import numpy as np
from typing import Optional

from .graph_schema import ProgrammeGraph


def generate_topology_cpts(
    pg: ProgrammeGraph,
    base_rate: float = 0.1,
) -> dict[str, dict]:
    """
    Generate naive conditional probability tables from graph topology.

    For each node, computes P(node_stressed | parent_states) using a
    noisy-OR model based on edge propagation rates:

      P(v stressed) = 1 - Π_{u ∈ parents(v)} (1 - p(u,v) × P(u stressed))

    This is a placeholder. Phase 2 will replace this with ODE-derived
    temporal CPTs that account for feedback loops and time delays.

    Args:
        pg: The programme graph.
        base_rate: Background probability of stress without any parent influence.

    Returns:
        Dictionary mapping node_id → {parents, cpt_noisy_or_params, base_rate}
    """
    G = pg.G
    cpts = {}

    for nid in G.nodes():
        parents = []
        for pred, _, data in G.in_edges(nid, data=True):
            parents.append({
                "parent_id": pred,
                "propagation_rate": data.get("propagation_rate", 0.5),
                "edge_type": data.get("edge_type", "unknown"),
            })

        cpts[nid] = {
            "node_id": nid,
            "label": G.nodes[nid].get("label", nid),
            "parents": parents,
            "base_rate": base_rate,
            "n_parents": len(parents),
            "avg_propagation": (
                np.mean([p["propagation_rate"] for p in parents])
                if parents else 0.0
            ),
        }

    return cpts


def detect_feedback_loops(pg: ProgrammeGraph) -> list[list[str]]:
    """
    Detect feedback loops (cycles) in the programme graph.

    Feedback loops are critical for system dynamics modelling because
    they create amplification or dampening effects that linear cascade
    models cannot capture.

    Returns:
        List of cycles, where each cycle is a list of node IDs.
    """
    try:
        cycles = list(pg.G.nodes())  # placeholder
        simple_cycles = []
        for cycle in _find_simple_cycles(pg.G, max_length=6):
            simple_cycles.append(cycle)
        return simple_cycles
    except Exception:
        return []


def _find_simple_cycles(G, max_length: int = 6) -> list[list[str]]:
    """Find simple cycles up to max_length using NetworkX."""
    import networkx as nx
    cycles = []
    for cycle in nx.simple_cycles(G):
        if len(cycle) <= max_length:
            cycles.append(cycle)
    return cycles


# ── Future Phase 2 Interface ────────────────────────────────────────

class SystemDynamicsModel:
    """
    Placeholder for the Phase 2 system dynamics integration.

    Will implement:
      - Stock-and-flow state representation
      - ODE-based temporal evolution
      - Feedback loop amplification factors
      - Time-delay propagation modelling
    """

    def __init__(self, pg: ProgrammeGraph):
        self.pg = pg
        self._feedback_loops = detect_feedback_loops(pg)

    @property
    def feedback_loop_count(self) -> int:
        return len(self._feedback_loops)

    @property
    def feedback_loops(self) -> list[list[str]]:
        return self._feedback_loops

    def evolve(self, initial_state: dict, dt: float = 0.1, steps: int = 100) -> dict:
        """
        Placeholder: evolve the system forward in time.
        Phase 2 will implement scipy.integrate.solve_ivp here.
        """
        raise NotImplementedError(
            "System dynamics temporal evolution is Phase 2 (Stream 2: Cascade Dynamics). "
            "Use CascadeEngine.simulate() for static cascade analysis."
        )
