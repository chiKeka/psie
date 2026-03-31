# PSIE — Programme Structural Intelligence Engine

**A computational tool that makes the invisible topology of major programmes visible, analysable, and actionable.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## The Problem

Nine out of ten megaprojects overrun on budget or schedule (91.5% by Flyvbjerg's database of 16,000+ projects). The core issue is not a lack of data but a lack of **structural visibility**: programme leaders cannot see the topology of interdependencies between workstreams, resources, stakeholders, governance structures, and risks. Gantt charts show sequence. Risk registers list items. Neither reveals *structure* — the hidden web of couplings through which a delay in one workstream cascades into cost overruns in another.

## The Idea

PSIE encodes the interdependency structure of a major programme as a **typed knowledge graph**, then applies network analysis and cascade simulation to reveal structural vulnerabilities invisible to conventional programme controls.

### Six-Layer Architecture

| Layer | Component | Source | Function |
|-------|-----------|--------|----------|
| 6 | Interpretation Layer | S³ Framework | Translate outputs into programme-management language |
| 5 | Calibration Layer | Reference Class Forecasting | Anchor predictions to empirical base rates |
| 4 | Prediction Engine | Bayesian Networks | Compute probability distributions over outcomes |
| 3 | Temporal Model | System Dynamics | Model feedback loops, stocks, flows, and delays |
| **2** | **Propagation Engine** | **Network Science** | **Simulate cascading disruptions** ✅ |
| **1** | **Graph Schema** | **DSMs / Systems Engineering** | **Encode programme as typed knowledge graph** ✅ |

Layers 1–2 are implemented in this MVP. Layers 3–5 are stubs with clear interfaces for Phase 2 research streams.

### Three Decision Modes

- **Explore** — *Scenario Planning*: Map the full dependency topology; identify structural vulnerabilities.
- **Attack** — *War Gaming*: Simulate cascading failures; quantify blast radius.
- **Steer** — *Adaptive Planning*: Update the model with live data; recommend structural interventions.

## Quick Start

```bash
# Clone and install
git clone https://github.com/chiKeka/psie.git
cd psie
pip install -r requirements.txt

# Run the demo
python main.py --save-plots

# Run without plots (console only)
python main.py --no-plots
```

### Google Colab

Open `notebooks/oman_demo.ipynb` in Google Colab for an interactive walkthrough — no local setup required.

## Proof of Concept: Oman Vision 2040

The MVP includes a fully encoded case study of Oman's national vision programme (23 nodes, 35 edges) derived from the baseline system map in Armanios et al. (2025).

### Key Findings

| S³ Lens | Finding |
|---------|---------|
| **Scoping** | Non-Oil Industries and Trade are most structurally vulnerable |
| **Scaffolding** | Fiscal & Monetary Policy is the primary information bottleneck |
| **Sensing** | National Identity and Environmental Sustainability are orphan nodes (blind spots) |
| **Sensing** | Attention bias: leadership focus concentrates on Economy family nodes |
| **Attack** | Oil Price Crash produces the widest cascade; IMEC disruption is surprisingly shallow |

## Project Structure

```
psie/
├── psie/                        # Core Python package
│   ├── __init__.py
│   ├── config.py                # Constants, colours, thresholds
│   ├── graph_schema.py          # Layer 1: typed knowledge graph
│   ├── propagation.py           # Layer 2: cascade simulation
│   ├── s3_metrics.py            # S³ analytical lenses
│   ├── visualization.py         # Matplotlib graph visualisation
│   └── sd_bridge.py             # Layer 3 stub (system dynamics)
├── data/
│   └── oman_vision_2040.json    # Case study data
├── notebooks/
│   └── oman_demo.ipynb          # Google Colab notebook
├── ui/
│   └── streamlit_app.py         # Interactive Streamlit dashboard
├── outputs/                     # Generated figures
├── research_streams/            # Phase 2 placeholders
│   ├── 1_representation/
│   ├── 2_cascades/
│   ├── 3_prediction/
│   ├── 4_calibration/
│   └── 5_automation/
├── main.py                      # Demo runner
├── requirements.txt
└── README.md
```

## Intellectual Foundations

| Tradition | Engine Layer | Core Contribution |
|-----------|-------------|-------------------|
| Network Science & Cascading Failure | Propagation Engine | Models *how* disruptions travel (Buldyrev et al., 2010; Barabási, 2016) |
| System Dynamics | Temporal Model | Captures feedback loops and time delays (Forrester, 1961; Sterman, 2000) |
| Design Structure Matrices | Graph Schema | Structural representation of interdependencies (Eppinger & Browning, 2012) |
| Bayesian Networks | Prediction Engine | Probabilistic inference under uncertainty (Pearl, 2009; Fenton & Neil, 2012) |
| Reference Class Forecasting | Calibration Layer | Anchors predictions to empirical base rates (Flyvbjerg, 2006; Kahneman & Lovallo, 1993) |

The **S³ Framework** (Scoping, Scaffolding, Sensing) from Armanios et al. (2025) serves as the domain interpretation layer — translating structural analysis into programme-management insight.

## Research Programme

This MVP is the foundation for a multi-phase research programme:

- **Phase 1** (2026): MMPM Dissertation — structural diagnosis via typed graphs
- **Phase 2** (2027–2029): Five parallel research streams, each producing publications and validated engine components
- **Phase 3** (2029+): Product assembly — integrated prediction engine

## Contributing

This is a research tool seeking collaborators in network science, system dynamics, Bayesian inference, programme management, and NLP/AI. If your expertise intersects with any of the five intellectual traditions, I'd love to hear from you.

See `docs/collaboration_deck.pdf` for a one-page overview of collaboration opportunities.

## Author

**Bruno Chikeka**
MSc Major Programme Management, Saïd Business School, University of Oxford
Supervisor: Prof. Daniel Armanios

## License

MIT License. See [LICENSE](LICENSE) for details.

## Citation

If you use PSIE in your research, please cite:

```bibtex
@software{chikeka2026psie,
  author  = {Chikeka, Bruno},
  title   = {PSIE: Programme Structural Intelligence Engine},
  year    = {2026},
  url     = {https://github.com/chiKeka/psie},
}
```
