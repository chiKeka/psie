"""
PSIE — Visualisation Module
==============================
Matplotlib-based static graph visualisation + optional pyvis interactive HTML.

Provides publication-quality figures for the dissertation and interactive
exploration for analysis sessions.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
from typing import Optional

from .graph_schema import ProgrammeGraph
from .propagation import CascadeResult
from .config import FAMILY_COLOURS, EDGE_CATEGORY_COLOURS


def plot_programme_graph(
    pg: ProgrammeGraph,
    cascade: Optional[CascadeResult] = None,
    title: Optional[str] = None,
    figsize: tuple[int, int] = (16, 12),
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot the programme graph using matplotlib.

    Nodes are coloured by family and sized by degree centrality.
    If a CascadeResult is provided, affected nodes are highlighted with
    red borders and sized by impact.
    """
    G = pg.G
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.set_facecolor("#f8f9fa")
    fig.patch.set_facecolor("#ffffff")

    # Layout
    pos = nx.spring_layout(G, k=2.5, iterations=80, seed=42)

    # Degree centrality for node sizing
    degree = nx.degree_centrality(G)

    # Cascade lookup
    cascade_nodes = {}
    if cascade:
        for step in cascade.cascade_path:
            cascade_nodes[step["node_id"]] = step["impact"]

    # ── Draw edges ───────────────────────────────────────────────
    for u, v, data in G.edges(data=True):
        cat = data.get("category", "dependency")
        colour = EDGE_CATEGORY_COLOURS.get(cat, "#cccccc")
        weight = data.get("weight", 0.5)
        alpha = 0.3 + 0.4 * weight

        # Highlight cascade edges
        if u in cascade_nodes and v in cascade_nodes:
            colour = "#e74c3c"
            alpha = 0.9

        ax.annotate(
            "",
            xy=pos[v], xytext=pos[u],
            arrowprops=dict(
                arrowstyle="-|>",
                color=colour,
                alpha=alpha,
                lw=0.8 + weight * 1.5,
                connectionstyle="arc3,rad=0.1",
            ),
        )

    # ── Draw nodes ───────────────────────────────────────────────
    for nid in G.nodes():
        data = G.nodes[nid]
        family = data.get("family", "")
        colour = FAMILY_COLOURS.get(family, "#95a5a6")
        size = 300 + degree.get(nid, 0) * 2000

        edge_colour = "#333333"
        linewidth = 1.5

        if nid in cascade_nodes:
            edge_colour = "#e74c3c"
            linewidth = 3.0
            size = max(size, 200 + cascade_nodes[nid] * 3000)

        nx.draw_networkx_nodes(
            G, pos,
            nodelist=[nid],
            node_size=[size],
            node_color=[colour],
            edgecolors=[edge_colour],
            linewidths=[linewidth],
            ax=ax,
        )

    # ── Labels ───────────────────────────────────────────────────
    labels = {n: G.nodes[n].get("label", n) for n in G.nodes()}
    nx.draw_networkx_labels(
        G, pos, labels,
        font_size=7, font_weight="bold", font_color="#2c3e50",
        ax=ax,
    )

    # ── Legend ────────────────────────────────────────────────────
    legend_patches = [
        mpatches.Patch(color=c, label=f)
        for f, c in FAMILY_COLOURS.items()
        if f in pg.families()
    ]
    ax.legend(
        handles=legend_patches,
        loc="upper left",
        fontsize=8,
        framealpha=0.9,
        title="Node Families",
        title_fontsize=9,
    )

    display_title = title or f"PSIE — {pg.name}"
    ax.set_title(display_title, fontsize=14, fontweight="bold", color="#2c3e50")
    ax.axis("off")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    if show:
        plt.show()

    return fig


def plot_vulnerability_ranking(
    ranking: list[tuple[str, float]],
    pg: ProgrammeGraph,
    top_n: int = 15,
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """Horizontal bar chart of top-N vulnerability scores."""
    data = ranking[:top_n]
    node_ids = [nid for nid, _ in data]
    scores = [s for _, s in data]
    labels = [pg.G.nodes[nid].get("label", nid) for nid in node_ids]
    colours = [FAMILY_COLOURS.get(pg.G.nodes[nid].get("family", ""), "#95a5a6") for nid in node_ids]

    fig, ax = plt.subplots(figsize=(10, 0.5 * top_n + 1))
    bars = ax.barh(range(len(labels)), scores, color=colours, edgecolor="#333", linewidth=0.5)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Composite Vulnerability Score", fontsize=10)
    ax.set_title("S³ Scoping: Vulnerability Ranking", fontsize=12, fontweight="bold")
    ax.set_xlim(0, max(scores) * 1.15)

    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{score:.3f}", va="center", fontsize=8, color="#555")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_cascade_timeline(
    cascade: CascadeResult,
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """Step-by-step cascade impact timeline."""
    if not cascade.cascade_path:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No cascade propagation", ha="center", va="center", fontsize=14)
        ax.axis("off")
        return fig

    steps = sorted(set(e["step"] for e in cascade.cascade_path))
    step_impacts = {s: [] for s in steps}
    for entry in cascade.cascade_path:
        step_impacts[entry["step"]].append(entry)

    fig, ax = plt.subplots(figsize=(12, 6))
    y_pos = 0
    y_labels = []
    y_positions = []

    for step in steps:
        entries = sorted(step_impacts[step], key=lambda x: -x["impact"])
        for entry in entries:
            colour = FAMILY_COLOURS.get(entry["family"], "#95a5a6")
            ax.barh(y_pos, entry["impact"], color=colour, edgecolor="#333", linewidth=0.5, height=0.7)
            ax.text(entry["impact"] + 0.005, y_pos, f'{entry["impact"]:.3f}',
                    va="center", fontsize=8, color="#555")
            y_labels.append(f'[t={step}] {entry["label"]}')
            y_positions.append(y_pos)
            y_pos += 1

    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Impact Magnitude", fontsize=10)
    ax.set_title(f'Cascade Timeline: {cascade.disruption_label}', fontsize=12, fontweight="bold")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig
