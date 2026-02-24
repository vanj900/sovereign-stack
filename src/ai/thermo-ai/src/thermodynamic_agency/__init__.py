"""
Thermodynamic Agency - Bio-Digital Organisms

A framework for building AI agents with genuine metabolic constraints,
ethical reasoning, and emergent agency through thermodynamic limitation.
"""

from .bio_digital_organism import BioDigitalOrganism
from .core import MetabolicEngine, EntropySimulator
from .cognition import GoalManager, EthicalEngine, IdentityPersistence
from .inference import PredictiveModel, ActiveInferenceLoop
from .environment import ResourceWorld, TaskGenerator, LifeLog

__version__ = "0.1.0"

__all__ = [
    'BioDigitalOrganism',
    'MetabolicEngine',
    'EntropySimulator',
    'GoalManager',
    'EthicalEngine',
    'IdentityPersistence',
    'PredictiveModel',
    'ActiveInferenceLoop',
    'ResourceWorld',
    'TaskGenerator',
    'LifeLog'
]