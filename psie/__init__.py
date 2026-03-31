"""
Programme Structural Intelligence Engine (PSIE)
================================================
A computational tool that encodes the interdependency structure of major
programmes as typed knowledge graphs, then applies network analysis and
cascade simulation to reveal structural vulnerabilities invisible to
conventional programme controls.

Based on five intellectual traditions:
  1. Network Science & Cascading Failure
  2. System Dynamics
  3. Design Structure Matrices
  4. Bayesian Networks
  5. Reference Class Forecasting

With the S³ Framework (Armanios et al., 2025) as the domain interpretation layer.

Author: Bruno Chikeka
Institution: Saïd Business School, University of Oxford
"""

__version__ = "0.1.0"
__author__ = "Bruno Chikeka"

from .graph_schema import (
    NodeType, EdgeType, NodeCategory, EdgeCategory,
    ProgrammeNode, ProgrammeEdge, ProgrammeGraph,
)
from .propagation import CascadeEngine, Disruption, DisruptionType
from .s3_metrics import S3Analyser

__all__ = [
    "NodeType", "EdgeType", "NodeCategory", "EdgeCategory",
    "ProgrammeNode", "ProgrammeEdge", "ProgrammeGraph",
    "CascadeEngine", "Disruption", "DisruptionType",
    "S3Analyser",
]
