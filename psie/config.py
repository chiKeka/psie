"""
PSIE — Configuration & Constants
==================================
Centralised configuration for the Programme Structural Intelligence Engine.
"""

# ── Family colour palette (matches CMR paper colour coding) ──────────
FAMILY_COLOURS = {
    "Economy":            "#4A90D9",   # Blue
    "Society":            "#F5C542",   # Yellow
    "Environment":        "#9B59B6",   # Purple
    "Support Mechanisms": "#E74C3C",   # Red
    "Governance":         "#6B8E23",   # Olive green
    "External":           "#95A5A6",   # Grey for exogenous events
}

# ── Node shape mapping by category ───────────────────────────────────
CATEGORY_SHAPES = {
    "component":   "dot",
    "actor":       "diamond",
    "governance":  "triangle",
    "resource":    "square",
    "environment": "star",
}

# ── Edge colour mapping by category ──────────────────────────────────
EDGE_CATEGORY_COLOURS = {
    "dependency":    "#333333",
    "governance":    "#6B8E23",
    "support":       "#2ECC71",
    "vulnerability": "#E74C3C",
    "social":        "#F39C12",
}

# ── Cascade simulation defaults ──────────────────────────────────────
CASCADE_DEFAULTS = {
    "absorption_threshold": 0.05,   # Impact below this is fully absorbed
    "max_steps":            10,     # Maximum cascade propagation steps
    "off_path_penalty":     0.3,    # Multiplier for non-primary edge paths
}

# ── Vulnerability score weights (for scoping analysis) ───────────────
VULNERABILITY_WEIGHTS = {
    "degree_centrality": 0.4,
    "vulnerability_attr": 0.3,
    "capacity_inverse":  0.2,
    "criticality":       0.1,
}

# ── S³ Lens thresholds ──────────────────────────────────────────────
S3_THRESHOLDS = {
    "scaffolding_gap_criticality": 0.6,   # Min criticality to flag gap
    "scaffolding_gap_max_support": 2,     # Max support edges before gap
    "orphan_percentile":          0.2,    # Bottom 20% by degree
    "bottleneck_percentile":      0.2,    # Top 20% by betweenness
    "attention_bias_threshold":   0.6,    # Family share above this = bias
}
