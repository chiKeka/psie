#!/usr/bin/env python3
"""
PSIE — Programme Structural Intelligence Engine
=================================================
Demo runner: loads the Oman Vision 2040 case, runs S³ analysis,
simulates disruption cascades, and generates visualisations.

Usage:
    python main.py                  # Full demo with plots
    python main.py --no-plots       # Console output only
    python main.py --save-plots     # Save figures to outputs/
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Ensure the package is importable when run from the repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from psie.graph_schema import ProgrammeGraph
from psie.propagation import CascadeEngine, Disruption, DisruptionType
from psie.s3_metrics import S3Analyser
from psie.sd_bridge import generate_topology_cpts, detect_feedback_loops


# ── Paths ────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "oman_vision_2040.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def load_disruption_scenarios(json_path: str) -> list[Disruption]:
    """Load disruption scenarios from the JSON data file."""
    with open(json_path) as f:
        data = json.load(f)
    scenarios = []
    for s in data.get("disruption_scenarios", []):
        scenarios.append(Disruption(
            id=s["id"],
            label=s["label"],
            disruption_type=DisruptionType(s["disruption_type"]),
            injection_node=s["injection_node"],
            magnitude=s["magnitude"],
            description=s.get("description", ""),
        ))
    return scenarios


def print_section(title: str, char: str = "=") -> None:
    width = 70
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")


def main():
    parser = argparse.ArgumentParser(description="PSIE Demo Runner")
    parser.add_argument("--no-plots", action="store_true", help="Skip matplotlib plots")
    parser.add_argument("--save-plots", action="store_true", help="Save plots to outputs/")
    args = parser.parse_args()

    # ── Load programme graph ─────────────────────────────────────
    print_section("PROGRAMME STRUCTURAL INTELLIGENCE ENGINE")
    print(f"  Loading: {DATA_PATH}")
    pg = ProgrammeGraph.from_json(DATA_PATH)
    print()
    print(pg.summary())

    # ── S³ Analysis ──────────────────────────────────────────────
    analyser = S3Analyser(pg)

    # Scoping
    print_section("S³ LENS 1 — SCOPING (Vulnerability Analysis)")
    scoping = analyser.scoping()
    print("\nTop 10 by Composite Vulnerability Score:")
    for nid, score in scoping["vulnerability_ranking"][:10]:
        d = pg.G.nodes[nid]
        print(f"  {d['label']:40s}  {score:.4f}  [{d['family']}]")
    print(f"\nFragility Concentration (Gini): {scoping['fragility_concentration_gini']:.4f}")
    print(f"Minimum Viable System: {len(scoping['minimum_viable_system'])} nodes")

    # Scaffolding
    print_section("S³ LENS 2 — SCAFFOLDING (Information Flow)")
    scaffolding = analyser.scaffolding()
    print("\nInformation Bottlenecks:")
    for nid, score in scaffolding["information_bottlenecks"]:
        d = pg.G.nodes[nid]
        print(f"  {d['label']:40s}  betweenness={score:.4f}")
    if scaffolding["scaffolding_gaps"]:
        print("\nScaffolding Gaps (high criticality, low support):")
        for gap in scaffolding["scaffolding_gaps"][:5]:
            print(f"  {gap['label']:40s}  crit={gap['criticality']:.1f}  "
                  f"support={gap['support_edges']}  severity={gap['gap_severity']:.4f}")
    print(f"\nAvg Path Length: {scaffolding['flow_efficiency_avg_path_length']:.4f}")

    # Sensing
    print_section("S³ LENS 3 — SENSING (Gap Detection)")
    sensing = analyser.sensing()
    print("\nOrphan Nodes (potential blind spots):")
    for orphan in sensing["orphan_nodes"]:
        print(f"  {orphan['label']:40s}  degree={orphan['degree']}  [{orphan['family']}]")
    print(f"\nAttention Concentration: {sensing['attention_concentration']}")
    if sensing["attention_bias_warning"]:
        print("  ⚠  ATTENTION BIAS WARNING: leadership focus is concentrated in one family")

    # ── Disruption Simulations ───────────────────────────────────
    print_section("DISRUPTION SIMULATIONS (Attack Mode)")
    disruptions = load_disruption_scenarios(DATA_PATH)
    engine = CascadeEngine(pg)

    cascade_results = []
    for disruption in disruptions:
        result = engine.simulate(disruption)
        cascade_results.append(result)
        print(f"\n{result.summary()}")
        if result.cascade_path:
            print("  Cascade path:")
            for step in result.cascade_path[:8]:
                print(f"    t={step['step']}: {step['label']:30s}  "
                      f"impact={step['impact']:.4f}  [{step['family']}]")

    # ── System Dynamics Stub ─────────────────────────────────────
    print_section("SYSTEM DYNAMICS (Layer 3 — Stub)")
    cpts = generate_topology_cpts(pg)
    loops = detect_feedback_loops(pg)
    print(f"  Topology-derived CPTs generated for {len(cpts)} nodes")
    print(f"  Feedback loops detected: {len(loops)}")
    if loops:
        for i, loop in enumerate(loops[:5]):
            labels = [pg.G.nodes[n].get("label", n) for n in loop]
            print(f"    Loop {i+1}: {' → '.join(labels)}")

    # ── Visualisations ───────────────────────────────────────────
    if not args.no_plots:
        print_section("GENERATING VISUALISATIONS")
        from psie.visualization import (
            plot_programme_graph,
            plot_vulnerability_ranking,
            plot_cascade_timeline,
        )

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        show = not args.save_plots

        # Programme graph
        save_graph = os.path.join(OUTPUT_DIR, "oman_2040_graph.png") if args.save_plots else None
        plot_programme_graph(pg, title="PSIE — Oman Vision 2040", save_path=save_graph, show=show)

        # Vulnerability ranking
        save_vuln = os.path.join(OUTPUT_DIR, "vulnerability_ranking.png") if args.save_plots else None
        plot_vulnerability_ranking(scoping["vulnerability_ranking"], pg, save_path=save_vuln, show=show)

        # Cascade timeline for the widest cascade (Oil Price Crash)
        widest = max(cascade_results, key=lambda r: r.total_nodes_affected)
        save_cascade = os.path.join(OUTPUT_DIR, "cascade_timeline.png") if args.save_plots else None
        plot_cascade_timeline(widest, save_path=save_cascade, show=show)

        if args.save_plots:
            print(f"  Figures saved to {OUTPUT_DIR}/")

    print_section("DONE", "─")
    print("  PSIE v0.1.0 — Programme Structural Intelligence Engine")
    print("  Bruno Chikeka | Saïd Business School, University of Oxford")
    print()


if __name__ == "__main__":
    main()
