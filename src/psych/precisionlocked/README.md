# PrecisionLocked

**A Computational Framework for Trauma and Therapeutic Change via Active Inference**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This repository implements a mechanistic framework for understanding psychological trauma and therapeutic recovery through the **Free Energy Principle (FEP)** and **Active Inference**. 

### Core Thesis

**Trauma is not merely a psychological event but a specific computational configuration**: the assignment of pathologically high precision (Π → ∞) to high-level priors within the generative hierarchy.

**Therapeutic intervention is "Bayesian Annealing"**: a controlled process of lowering prior precision to facilitate error-driven belief updating within a biologically limited reconsolidation window.

## Key Concepts

### 1. Trauma as Pathological Precision

In the Active Inference framework, **precision** (Π) acts as the "gain" on prediction errors. When prior precision becomes pathologically elevated:

```
Π_prior → ∞  ⟹  μ̇ → 0  (Belief updating stops)
```

This creates a **deep attractor basin** in the free-energy landscape—a rigid belief configuration immune to sensory disconfirmation.

### 2. The Energetic Paradox

Trauma presents a computational paradox:
- **Low local entropy**: Rigid, certain beliefs (Π → ∞)
- **High metabolic cost**: Physical exhaustion

**Mechanism**: The mismatch between the rigid prior ("Danger") and the safe environment generates continuous, high-amplitude prediction errors. Since the prior cannot update, the system must engage in **active suppression** of these errors—a metabolically expensive process that constitutes **allostatic load**.

### 3. Therapy as Bayesian Annealing

Therapeutic intervention implements a precision modulation schedule:

```
Π_prior ↓  (Reduce prior certainty)
Π_sensory ↑  (Increase sensory evidence weight)
```

This shifts the system from a **"prior-driven"** regime (trauma) to a **"sensory-driven"** regime (healthy), allowing the internal model to update toward veridical representations.

### 4. The Reconsolidation Window

Belief updating is constrained by a **memory reconsolidation window** (~3-6 hours):
1. Memory must be retrieved (activated)
2. A prediction error violation must occur (safety in presence of threat cues)
3. Updating must occur within the time window
4. A **safety scaffold** must be maintained (otherwise risk of retraumatization)

## Installation

```bash
# Clone the repository
git clone https://github.com/vanj900/precisionlocked.git
cd precisionlocked

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

## Quick Start

### Simulate Trauma Dynamics

```python
from precisionlocked.trauma_model import TraumaSimulator
from precisionlocked.visualization import plot_trauma_dynamics

# Initialize simulator
simulator = TraumaSimulator(
    n_features=1,
    trauma_precision=100.0,  # Π_prior → ∞
    safe_environment_mean=1.0  # Safe context
)

# Run simulation
results = simulator.run_simulation(n_timesteps=100)

# Visualize
plot_trauma_dynamics(results, save_path="trauma_dynamics.png")
```

### Simulate Therapeutic Intervention

```python
from precisionlocked.therapy_model import TherapeuticIntervention
from precisionlocked.visualization import plot_therapeutic_intervention

# Initialize intervention
intervention = TherapeuticIntervention(
    n_features=1,
    trauma_precision=100.0,  # Initial state
    safe_sensory_mean=1.0
)

# Run therapeutic session with Bayesian Annealing
history = intervention.run_session(
    duration=100,
    schedule_type="exponential",
    safety_scaffold=True
)

# Assess outcome
outcome = intervention.assess_outcome()
print(f"Convergence to safety: {outcome['convergence_to_safety']:.3f}")

# Visualize
plot_therapeutic_intervention(history, save_path="therapy.png")
```

## Examples

Run the included demonstration scripts:

```bash
# Trauma dynamics simulation
python examples/trauma_simulation.py

# Therapeutic intervention simulation
python examples/therapy_simulation.py
```

## Framework Components

### Core Modules

1. **`free_energy.py`**: Free Energy Principle implementation
   - Variational free energy calculation
   - Precision weighting mechanisms
   - Active inference agent

2. **`trauma_model.py`**: Trauma as computational pathology
   - Pathological attractor basin
   - Allostatic load calculator
   - Trauma dynamics simulator

3. **`therapy_model.py`**: Therapeutic intervention
   - Bayesian annealing scheduler
   - Neuromodulatory control
   - Reconsolidation window constraints
   - Complete therapeutic intervention model

4. **`visualization.py`**: Analysis and plotting utilities
   - Trauma dynamics plots
   - Therapeutic intervention visualization
   - Precision landscape diagrams

## Theoretical Foundation

This implementation is based on the following theoretical framework:

### Mathematical Formulation

**Variational Free Energy:**
```
F = E_q[log q(μ) - log p(y, μ)]
  = (Sensory Surprise) + (Complexity)
```

**Belief Update (Gradient Descent):**
```
μ̇ = -∂F/∂μ = Π_sensory · ε - Π_prior · μ

where ε = y - μ  (prediction error)
```

**Trauma Condition:**
```
Π_prior → ∞  ⟹  μ̇ → 0
```

**Allostatic Load:**
```
L(t) = L_base + Π_prior · ||ε(t)|| · κ

where κ is the metabolic cost factor
```

### Neuromodulatory Mapping

- **Noradrenaline (NE)**: Signals unexpected uncertainty (phasic activation for destabilizing priors)
- **Acetylcholine (ACh)**: Increases sensory prediction error gain (Π_sensory)
- **Dopamine (DA)**: Encodes precision of action policies
- **Oxytocin**: Reduces precision of social threat priors

## Experimental Results

**See [RESULTS.md](RESULTS.md) for comprehensive experimental validation.**

Four systematic experiments have been conducted to validate the framework:
1. **Baseline Trauma Dynamics**: Demonstrates linear scaling of allostatic load with prior precision
2. **Annealing Schedule Comparison**: Sigmoid schedule achieves 78% convergence to safety
3. **Parameter Sensitivity Analysis**: Higher trauma severity requires longer intervention duration
4. **Safety Scaffold Requirement**: Safety context is computationally necessary for successful therapy

**Key Findings:**
- ✅ All major theoretical predictions validated
- ✅ Trauma precision linearly predicts metabolic cost
- ✅ Bayesian Annealing successfully enables attractor escape
- ✅ Safety scaffold is critical (100% vs 0% success rate)

## Falsifiable Predictions

1. **Neural Coupling**: Successful therapy correlates with decreased effective connectivity (precision) between amygdala and mPFC during trauma script recall

2. **Pupillometry**: Locus coeruleus activity (via pupil dilation) shifts from tonic (rigid) to phasic (reactive) patterns during therapeutic annealing

3. **Metabolic Markers**: Allostatic load markers (cortisol, inflammatory cytokines) decrease as prior precision is reduced

## Citation

If you use this framework in your research, please cite:

```
@software{precisionlocked2026,
  title = {PrecisionLocked: A Computational Framework for Trauma and Therapeutic Change},
  author = {},
  year = {2026},
  url = {https://github.com/vanj900/precisionlocked}
}
```

## Related Work

This framework builds on:
- **Free Energy Principle** (Friston, 2010)
- **Active Inference** (Friston et al., 2017)
- **Precision-weighted prediction errors** (Feldman & Friston, 2010)
- **Memory reconsolidation** (Nader & Hardt, 2009)
- **Allostatic load** (McEwen, 1998)

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## License

MIT License - see `LICENSE` file for details.

## Acknowledgments

This computational framework provides a mechanistic bridge between:
- Information theory (Free Energy Principle)
- Neurobiology (neuromodulation, reconsolidation)
- Clinical phenomenology (trauma, therapy)

The goal is to move beyond metaphor toward precise, testable hypotheses about the computational nature of psychological suffering and healing.
