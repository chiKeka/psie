"""
PSIE — Streamlit Interactive Dashboard
========================================
Interactive exploration of programme structure, S³ analysis,
and disruption simulation.

Usage:
    streamlit run ui/streamlit_app.py
"""

from __future__ import annotations

import os
import sys
import json
import streamlit as st
import matplotlib.pyplot as plt

# Ensure package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from psie.graph_schema import ProgrammeGraph
from psie.propagation import CascadeEngine, Disruption, DisruptionType
from psie.s3_metrics import S3Analyser
from psie.visualization import plot_programme_graph, plot_vulnerability_ranking, plot_cascade_timeline
from psie.config import FAMILY_COLOURS

# ── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="PSIE — Programme Structural Intelligence Engine",
    page_icon="🔬",
    layout="wide",
)

# ── Load Data ────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "oman_vision_2040.json")


@st.cache_resource
def load_graph():
    return ProgrammeGraph.from_json(DATA_PATH)


@st.cache_resource
def load_scenarios():
    with open(DATA_PATH) as f:
        data = json.load(f)
    return data.get("disruption_scenarios", [])


pg = load_graph()
analyser = S3Analyser(pg)
scenarios = load_scenarios()

# ── Header ───────────────────────────────────────────────────────────
st.title("🔬 Programme Structural Intelligence Engine")
st.caption(f"**{pg.name}** — {pg.node_count} nodes, {pg.edge_count} edges")

# ── Tabs ─────────────────────────────────────────────────────────────
tab_overview, tab_scoping, tab_scaffolding, tab_sensing, tab_attack = st.tabs([
    "📊 Overview", "🎯 Scoping", "🏗️ Scaffolding", "👁️ Sensing", "⚔️ Attack"
])

# ── Overview Tab ─────────────────────────────────────────────────────
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nodes", pg.node_count)
    col2.metric("Edges", pg.edge_count)
    col3.metric("Density", f"{pg.density:.4f}")
    col4.metric("Families", len(pg.families()))

    st.subheader("Programme Graph")
    fig = plot_programme_graph(pg, title=f"PSIE — {pg.name}", show=False)
    st.pyplot(fig)
    plt.close(fig)

# ── Scoping Tab ──────────────────────────────────────────────────────
with tab_scoping:
    st.subheader("S³ Scoping — Vulnerability Analysis")
    st.markdown("*What does the programme depend on?*")

    scoping = analyser.scoping()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Fragility (Gini)", f"{scoping['fragility_concentration_gini']:.4f}")
    with col2:
        st.metric("Min Viable System", f"{len(scoping['minimum_viable_system'])} nodes")

    st.subheader("Vulnerability Ranking")
    fig = plot_vulnerability_ranking(scoping["vulnerability_ranking"], pg, show=False)
    st.pyplot(fig)
    plt.close(fig)

# ── Scaffolding Tab ──────────────────────────────────────────────────
with tab_scaffolding:
    st.subheader("S³ Scaffolding — Information Flow")
    st.markdown("*How does the programme hold together?*")

    scaffolding = analyser.scaffolding()

    st.metric("Avg Path Length", f"{scaffolding['flow_efficiency_avg_path_length']:.2f}")

    st.subheader("Information Bottlenecks")
    for nid, score in scaffolding["information_bottlenecks"]:
        d = pg.G.nodes[nid]
        st.write(f"- **{d['label']}** — betweenness: {score:.4f}")

    if scaffolding["scaffolding_gaps"]:
        st.subheader("Scaffolding Gaps")
        for gap in scaffolding["scaffolding_gaps"][:5]:
            st.write(f"- **{gap['label']}** — criticality: {gap['criticality']:.1f}, "
                     f"support edges: {gap['support_edges']}, severity: {gap['gap_severity']:.4f}")

# ── Sensing Tab ──────────────────────────────────────────────────────
with tab_sensing:
    st.subheader("S³ Sensing — Gap Detection")
    st.markdown("*Where should attention be directed?*")

    sensing = analyser.sensing()

    if sensing["attention_bias_warning"]:
        st.warning("⚠️ **Attention Bias Warning**: Leadership focus is concentrated in one family.")

    st.subheader("Attention Concentration")
    st.json(sensing["attention_concentration"])

    st.subheader("Orphan Nodes (Potential Blind Spots)")
    for orphan in sensing["orphan_nodes"]:
        st.write(f"- **{orphan['label']}** — degree: {orphan['degree']} [{orphan['family']}]")

# ── Attack Tab ───────────────────────────────────────────────────────
with tab_attack:
    st.subheader("Disruption Simulation — Attack Mode")
    st.markdown("*If this disruption hits, what breaks?*")

    scenario_names = [s["label"] for s in scenarios]
    selected = st.selectbox("Select disruption scenario", scenario_names)
    scenario_data = scenarios[scenario_names.index(selected)]

    magnitude = st.slider("Disruption magnitude", 0.1, 1.0, scenario_data["magnitude"], 0.05)

    disruption = Disruption(
        id=scenario_data["id"],
        label=scenario_data["label"],
        disruption_type=DisruptionType(scenario_data["disruption_type"]),
        injection_node=scenario_data["injection_node"],
        magnitude=magnitude,
        description=scenario_data.get("description", ""),
    )

    engine = CascadeEngine(pg)
    result = engine.simulate(disruption)

    col1, col2, col3 = st.columns(3)
    col1.metric("Nodes Affected", result.total_nodes_affected)
    col2.metric("Cascade Depth", f"{result.cascade_depth} steps")
    col3.metric("Families Hit", len(result.impact_by_family))

    st.subheader("Cascade Timeline")
    fig = plot_cascade_timeline(result, show=False)
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Impact by Family")
    st.json(result.impact_by_family)

    st.subheader("Programme Graph with Cascade")
    fig = plot_programme_graph(pg, cascade=result, title=f"Cascade: {selected}", show=False)
    st.pyplot(fig)
    plt.close(fig)
