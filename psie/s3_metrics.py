"""
PSIE — S³ Analytical Lenses
=============================
Implements the three S³ lenses (Armanios et al., 2025) as structural
analyses over the programme knowledge graph.

  Scoping    → What does the programme depend on? (vulnerability analysis)
  Scaffolding → How does it hold together? (information flow / bottlenecks)
  Sensing    → Where should attention be directed? (gap detection / blind spots)

Each lens produces a dictionary of metrics that can be rendered by the
interpretation layer (Layer 6) using S³ vocabulary.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import networkx as nx
import numpy as np

from .graph_schema import ProgrammeGraph
from .config import VULNERABILITY_WEIGHTS, S3_THRESHOLDS


class S3Analyser:
    """
    Applies the three S³ analytical lenses to a ProgrammeGraph.
    """

    def __init__(self, graph: ProgrammeGraph):
        self.pg = graph
        self.G = graph.G

    # ═══════════════════════════════════════════════════════════════════
    # LENS 1 — SCOPING: Vulnerability Analysis
    # ═══════════════════════════════════════════════════════════════════

    def scoping(self) -> dict:
        """
        Identify where the programme is most vulnerable to disruption.

        Returns:
          degree_centrality, in/out degree, composite vulnerability ranking,
          minimum viable system node set, fragility concentration (Gini).
        """
        G = self.G
        w = VULNERABILITY_WEIGHTS

        degree = nx.degree_centrality(G)
        in_deg = nx.in_degree_centrality(G)
        out_deg = nx.out_degree_centrality(G)

        # Composite vulnerability score per node
        ranking = []
        for nid in G.nodes():
            d = G.nodes[nid]
            score = (
                w["degree_centrality"] * degree.get(nid, 0)
                + w["vulnerability_attr"] * d.get("vulnerability", 0.5)
                + w["capacity_inverse"] * (1.0 - d.get("absorptive_capacity", 0.5))
                + w["criticality"] * d.get("criticality", 0.5)
            )
            ranking.append((nid, round(score, 4)))
        ranking.sort(key=lambda x: x[1], reverse=True)

        # Minimum Viable System: nodes with above-median centrality
        median_deg = float(np.median(list(degree.values()))) if degree else 0.0
        mvs = {n for n, d in degree.items() if d >= median_deg}

        # Fragility concentration (Gini coefficient of degree distribution)
        vals = sorted(degree.values())
        n = len(vals)
        if n > 0 and sum(vals) > 0:
            gini = (
                2.0 * sum((i + 1) * v for i, v in enumerate(vals))
                / (n * sum(vals))
            ) - (n + 1) / n
        else:
            gini = 0.0

        return {
            "degree_centrality": _round_dict(degree),
            "in_degree_centrality": _round_dict(in_deg),
            "out_degree_centrality": _round_dict(out_deg),
            "vulnerability_ranking": ranking,
            "minimum_viable_system": mvs,
            "fragility_concentration_gini": round(gini, 4),
        }

    # ═══════════════════════════════════════════════════════════════════
    # LENS 2 — SCAFFOLDING: Information Flow Analysis
    # ═══════════════════════════════════════════════════════════════════

    def scaffolding(self) -> dict:
        """
        Assess the programme's information-flow structure.

        Returns:
          betweenness centrality, information bottlenecks,
          scaffolding gaps (high criticality + low support), avg path length.
        """
        G = self.G
        t = S3_THRESHOLDS

        betweenness = nx.betweenness_centrality(G, weight="weight")

        # Bottlenecks: top percentile by betweenness
        sorted_b = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
        top_n = max(1, int(len(sorted_b) * t["bottleneck_percentile"]))
        bottlenecks = [(nid, round(s, 4)) for nid, s in sorted_b[:top_n]]

        # Scaffolding gaps: high criticality but few incoming support edges
        gaps = []
        for nid in G.nodes():
            d = G.nodes[nid]
            crit = d.get("criticality", 0.5)
            support_in = sum(
                1 for _, _, ed in G.in_edges(nid, data=True)
                if ed.get("category") == "support"
            )
            if crit > t["scaffolding_gap_criticality"] and support_in < t["scaffolding_gap_max_support"]:
                gaps.append({
                    "node_id": nid,
                    "label": d.get("label", nid),
                    "criticality": crit,
                    "support_edges": support_in,
                    "gap_severity": round(crit / (support_in + 1), 4),
                })
        gaps.sort(key=lambda x: x["gap_severity"], reverse=True)

        # Average shortest path (use undirected for reachability)
        Gu = G.to_undirected()
        if nx.is_connected(Gu):
            avg_path = nx.average_shortest_path_length(Gu)
        else:
            largest = max(nx.connected_components(Gu), key=len)
            avg_path = nx.average_shortest_path_length(Gu.subgraph(largest))

        return {
            "betweenness_centrality": _round_dict(betweenness),
            "information_bottlenecks": bottlenecks,
            "scaffolding_gaps": gaps,
            "flow_efficiency_avg_path_length": round(avg_path, 4),
        }

    # ═══════════════════════════════════════════════════════════════════
    # LENS 3 — SENSING: Gap Detection & Blind Spots
    # ═══════════════════════════════════════════════════════════════════

    def sensing(self) -> dict:
        """
        Detect what is missing from the programme's structural picture.

        Returns:
          eigenvector centrality, orphan nodes (potential blind spots),
          clustering coefficients, attention concentration & bias warning.
        """
        G = self.G
        t = S3_THRESHOLDS

        # Eigenvector centrality — where executive attention concentrates
        try:
            eigenvec = nx.eigenvector_centrality(G, max_iter=1000, weight="weight")
        except nx.PowerIterationFailedConvergence:
            eigenvec = nx.degree_centrality(G)

        # Orphan nodes: bottom percentile by degree
        degree = dict(G.degree())
        sorted_deg = sorted(degree.items(), key=lambda x: x[1])
        bottom_n = max(1, int(len(sorted_deg) * t["orphan_percentile"]))
        orphans = [
            {
                "node_id": nid,
                "label": G.nodes[nid].get("label", nid),
                "degree": deg,
                "family": G.nodes[nid].get("family", ""),
            }
            for nid, deg in sorted_deg[:bottom_n]
        ]

        # Clustering coefficients (undirected)
        clustering = nx.clustering(G.to_undirected())

        # Attention bias: are the top eigenvector-centrality nodes concentrated
        # in one family?
        sorted_eigen = sorted(eigenvec.items(), key=lambda x: x[1], reverse=True)
        top_attn = sorted_eigen[: max(1, len(sorted_eigen) // 4)]
        attn_families: dict[str, int] = defaultdict(int)
        for nid, _ in top_attn:
            fam = G.nodes[nid].get("family", "unknown")
            attn_families[fam] += 1

        max_share = max(attn_families.values(), default=0) / max(len(top_attn), 1)
        bias_warning = max_share > t["attention_bias_threshold"]

        return {
            "eigenvector_centrality": _round_dict(eigenvec),
            "orphan_nodes": orphans,
            "clustering_coefficients": _round_dict(clustering),
            "attention_concentration": dict(attn_families),
            "attention_bias_warning": bias_warning,
        }

    # ═══════════════════════════════════════════════════════════════════
    # FULL ANALYSIS
    # ═══════════════════════════════════════════════════════════════════

    def full_analysis(self) -> dict:
        """Run all three S³ lenses and return consolidated results."""
        return {
            "programme": self.pg.name,
            "nodes": self.pg.node_count,
            "edges": self.pg.edge_count,
            "scoping": self.scoping(),
            "scaffolding": self.scaffolding(),
            "sensing": self.sensing(),
        }


# ── Helpers ──────────────────────────────────────────────────────────

def _round_dict(d: dict, decimals: int = 4) -> dict:
    return {k: round(v, decimals) for k, v in d.items()}
