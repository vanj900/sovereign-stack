"""Core thermodynamic substrate — metabolic engine, entropy dynamics, failure modes."""

from .failure_modes import (
    MetabolicFailure,
    EnergyDeathException,
    ThermalDeathException,
    EntropyDeathException,
    MemoryCollapseException,
)
from .entropy_dynamics import EntropyDynamics, DEFAULTS
from .metabolic_engine import MetabolicEngine

__all__ = [
    "MetabolicFailure",
    "EnergyDeathException",
    "ThermalDeathException",
    "EntropyDeathException",
    "MemoryCollapseException",
    "EntropyDynamics",
    "DEFAULTS",
    "MetabolicEngine",
]
