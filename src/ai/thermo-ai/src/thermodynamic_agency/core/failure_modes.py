"""
Failure Modes - Death Conditions

This module defines the various ways an agent can die and
implements the logic for permanent termination.
"""

from enum import Enum
from typing import Dict, Any, Optional
import json
import time


class DeathCause(Enum):
    """Enumeration of possible death causes"""
    ENERGY_DEATH = "energy_death"
    THERMAL_DEATH = "thermal_death"
    ENTROPY_DEATH = "entropy_death"
    MEMORY_COLLAPSE = "memory_collapse"
    VOLUNTARY_SHUTDOWN = "voluntary_shutdown"


class FailureMode:
    """
    Represents a failure condition and its consequences.
    """
    
    def __init__(
        self,
        cause: DeathCause,
        description: str,
        is_reversible: bool = False
    ):
        self.cause = cause
        self.description = description
        self.is_reversible = is_reversible
        self.timestamp = None
        self.final_state = None
    
    def trigger(self, metabolic_engine) -> Dict[str, Any]:
        """
        Execute the failure mode.
        
        Args:
            metabolic_engine: The dying MetabolicEngine instance
            
        Returns:
            Death certificate with final diagnostics
        """
        self.timestamp = time.time()
        self.final_state = metabolic_engine.get_state()
        
        death_certificate = {
            'cause': self.cause.value,
            'description': self.description,
            'timestamp': self.timestamp,
            'final_state': self.final_state,
            'is_reversible': self.is_reversible,
            'lifetime': metabolic_engine.age,
            'total_operations': metabolic_engine.total_operations,
            'state_history_length': len(metabolic_engine.state_history)
        }
        
        return death_certificate


class FailureModeManager:
    """
    Manages all possible failure modes and determines which applies.
    """
    
    def __init__(self):
        self.failure_modes = {
            DeathCause.ENERGY_DEATH: FailureMode(
                DeathCause.ENERGY_DEATH,
                "Complete energy depletion. No energy remains to sustain operations.",
                is_reversible=False
            ),
            DeathCause.THERMAL_DEATH: FailureMode(
                DeathCause.THERMAL_DEATH,
                "Critical temperature exceeded. Irreversible thermal damage to core systems.",
                is_reversible=False
            ),
            DeathCause.ENTROPY_DEATH: FailureMode(
                DeathCause.ENTROPY_DEATH,
                "Total system entropy. Stability reached zero, coherence lost.",
                is_reversible=False
            ),
            DeathCause.MEMORY_COLLAPSE: FailureMode(
                DeathCause.MEMORY_COLLAPSE,
                "Memory integrity below minimum threshold. Identity lost.",
                is_reversible=False
            ),
            DeathCause.VOLUNTARY_SHUTDOWN: FailureMode(
                DeathCause.VOLUNTARY_SHUTDOWN,
                "Agent chose to terminate. Calculated that continuation would violate principles.",
                is_reversible=False
            )
        }
        
        self.death_log = []
    
    def check_failure_conditions(self, metabolic_engine) -> Optional[DeathCause]:
        """
        Check if any failure conditions are met.
        
        Args:
            metabolic_engine: MetabolicEngine instance to check
            
        Returns:
            DeathCause if a failure condition is met, None otherwise
        """
        # Energy death
        if metabolic_engine.E <= 0:
            return DeathCause.ENERGY_DEATH
        
        # Thermal death
        if metabolic_engine.T > metabolic_engine.T_critical:
            return DeathCause.THERMAL_DEATH
        
        # Entropy death
        if metabolic_engine.S <= 0:
            return DeathCause.ENTROPY_DEATH
        
        # Memory collapse
        if metabolic_engine.M < metabolic_engine.M_min:
            return DeathCause.MEMORY_COLLAPSE
        
        return None
    
    def execute_failure(
        self,
        cause: DeathCause,
        metabolic_engine
    ) -> Dict[str, Any]:
        """
        Execute a failure mode and generate death certificate.
        
        Args:
            cause: The cause of death
            metabolic_engine: The dying MetabolicEngine
            
        Returns:
            Death certificate
        """
        failure_mode = self.failure_modes[cause]
        death_certificate = failure_mode.trigger(metabolic_engine)
        
        self.death_log.append(death_certificate)
        
        return death_certificate
    
    def get_warning_level(self, metabolic_engine) -> str:
        """
        Get current danger level based on metabolic state.
        
        Returns:
            "safe", "caution", "danger", or "critical"
        """
        survival_prob = metabolic_engine.get_survival_probability()
        
        if survival_prob > 0.7:
            return "safe"
        elif survival_prob > 0.4:
            return "caution"
        elif survival_prob > 0.2:
            return "danger"
        else:
            return "critical"
    
    def get_imminent_threats(self, metabolic_engine) -> list:
        """
        Identify which death conditions are approaching.
        
        Returns:
            List of threat descriptions
        """
        threats = []
        
        # Energy threat
        energy_ratio = metabolic_engine.E / metabolic_engine.E_max
        if energy_ratio < 0.2:
            threats.append(f"Energy critical: {energy_ratio*100:.1f}%")
        
        # Temperature threat
        temp_range = metabolic_engine.T_critical - metabolic_engine.T_ambient
        temp_ratio = (metabolic_engine.T - metabolic_engine.T_ambient) / temp_range
        if temp_ratio > 0.8:
            threats.append(f"Temperature critical: {metabolic_engine.T:.1f}K")
        
        # Memory threat
        if metabolic_engine.M < 0.3:
            threats.append(f"Memory integrity low: {metabolic_engine.M*100:.1f}%")
        
        # Stability threat
        if metabolic_engine.S < 0.3:
            threats.append(f"Stability low: {metabolic_engine.S*100:.1f}%")
        
        return threats


class DeathDiagnostics:
    """
    Post-mortem analysis tools.
    """
    
    @staticmethod
    def analyze_death(death_certificate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the circumstances of death.
        
        Args:
            death_certificate: Death certificate from FailureMode
            
        Returns:
            Analysis with insights
        """
        analysis = {
            'primary_cause': death_certificate['cause'],
            'contributing_factors': [],
            'preventability': 'unknown',
            'lessons': []
        }
        
        final_state = death_certificate['final_state']
        
        # Analyze energy situation
        if final_state['energy'] < 20:
            analysis['contributing_factors'].append('Low energy reserves')
            if death_certificate['cause'] != 'energy_death':
                analysis['lessons'].append('Should have prioritized energy gathering')
        
        # Analyze temperature
        if final_state['temperature'] > 320:  # Rough threshold
            analysis['contributing_factors'].append('High operating temperature')
            analysis['lessons'].append('Should have reduced computational load')
        
        # Analyze memory
        if final_state['memory_integrity'] < 0.5:
            analysis['contributing_factors'].append('Degraded memory integrity')
            analysis['lessons'].append('Should have invested in memory repair')
        
        # Analyze stability
        if final_state['stability'] < 0.5:
            analysis['contributing_factors'].append('Low system stability')
            analysis['lessons'].append('Should have performed stability maintenance')
        
        # Determine preventability
        if len(analysis['contributing_factors']) > 2:
            analysis['preventability'] = 'difficult'
        elif len(analysis['contributing_factors']) > 0:
            analysis['preventability'] = 'moderate'
        else:
            analysis['preventability'] = 'easy'
        
        return analysis
    
    @staticmethod
    def generate_autopsy_report(
        metabolic_engine,
        death_certificate: Dict[str, Any]
    ) -> str:
        """
        Generate a human-readable autopsy report.
        
        Args:
            metabolic_engine: The deceased MetabolicEngine
            death_certificate: Death certificate
            
        Returns:
            Formatted report string
        """
        analysis = DeathDiagnostics.analyze_death(death_certificate)
        
        report = f"""
========================================
        AUTOPSY REPORT
========================================
Cause of Death: {death_certificate['cause']}
Description: {death_certificate['description']}
Time of Death: {death_certificate['timestamp']}
Lifetime: {death_certificate['lifetime']:.2f} time units
Total Operations: {death_certificate['total_operations']}

FINAL STATE:
  Energy: {death_certificate['final_state']['energy']:.2f}
  Temperature: {death_certificate['final_state']['temperature']:.2f}K
  Memory Integrity: {death_certificate['final_state']['memory_integrity']:.3f}
  Stability: {death_certificate['final_state']['stability']:.3f}
  Age: {death_certificate['final_state']['age']:.2f}

CONTRIBUTING FACTORS:
"""
        for factor in analysis['contributing_factors']:
            report += f"  - {factor}\n"
        
        report += f"\nPREVENTABILITY: {analysis['preventability']}\n"
        
        report += "\nLESSONS LEARNED:\n"
        for lesson in analysis['lessons']:
            report += f"  - {lesson}\n"
        
        report += "========================================\n"
        
        return report
