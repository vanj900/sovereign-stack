"""Failure-mode exception hierarchy for the thermodynamic agent."""


class MetabolicFailure(Exception):
    """Base class for all thermodynamic failure conditions."""

    def __init__(self, message: str = "", state: dict | None = None):
        super().__init__(message)
        self.state = state or {}


class EnergyDeathException(MetabolicFailure):
    """Raised when energy E drops to or below zero."""


class ThermalDeathException(MetabolicFailure):
    """Raised when temperature T exceeds T_critical."""


class EntropyDeathException(MetabolicFailure):
    """Raised when stability S drops to or below zero."""


class MemoryCollapseException(MetabolicFailure):
    """Raised when memory integrity M drops below M_min."""
