"""
PrecisionLocked: A Computational Framework for Trauma and Therapeutic Change

This package implements a mechanistic framework for understanding psychological 
trauma and therapeutic recovery through the Free Energy Principle (FEP) and 
Active Inference.

Key Concepts:
- Trauma as pathologically high precision (Π → ∞) assignment to priors
- Therapeutic intervention as "Bayesian Annealing"
- Allostatic load as metabolic cost of error suppression
"""

__version__ = "0.1.0"

from .free_energy import VariationalFreeEnergy, PrecisionWeighting
from .trauma_model import TraumaAttractor, AllostaticLoad
from .therapy_model import BayesianAnnealing, ReconsolidationWindow

__all__ = [
    "VariationalFreeEnergy",
    "PrecisionWeighting",
    "TraumaAttractor",
    "AllostaticLoad",
    "BayesianAnnealing",
    "ReconsolidationWindow",
]
