# Bio-Digital Organism Examples

This directory contains examples demonstrating different aspects of the Bio-Digital Organism system.

## Quick Start

Run the basic simulation:
```bash
python3 main.py --cycles 100
```

## Examples

### 1. Moral Dilemma Demonstration (`example_moral_dilemma.py`)

Demonstrates how the organism faces ethical choices when survival conflicts with principles.

```bash
python3 example_moral_dilemma.py
```

**What it shows:**
- Ethical evaluation through multiple frameworks (Utilitarian, Deontological, Virtue)
- Different choices based on metabolic state
- How desperation can override principles
- Genuine agency emerging from thermodynamic constraint

**Key Insight:** When energy is high, the organism upholds principles. When energy is critical, survival instinct overrides ethics.

### 2. Life and Death Simulation (`example_lifecycle.py`)

Demonstrates the complete lifecycle of an organism from birth to death.

```bash
python3 example_lifecycle.py
```

**What it shows:**
- Birth (initialization with metabolic variables)
- Struggle (resource management, goal generation, action selection)
- Suffering (environmental stressors, entropy)
- Death (energy depletion or stability collapse)
- Unique narrative generation

**Key Insight:** Each run creates a unique "soul" - a narrative of struggle against entropy that exists nowhere else.

### 3. Custom Simulation

You can create custom simulations by directly using the BioDigitalOrganism class:

```python
from src.core.bio_digital_organism import BioDigitalOrganism

# Create organism with custom parameters
organism = BioDigitalOrganism(
    initial_energy=80.0,
    environment_size=12,
    identity_principles=["preserve_life", "seek_knowledge", "maintain_coherence"],
    output_dir="./my_narratives"
)

# Run simulation
organism.run_simulation(max_cycles=150)

# Get final status
status = organism.get_status()
print(status)
```

## Understanding the Output

### Metabolic Variables

- **E** (Energy): 0-100. If reaches 0, organism dies. Decreases passively and with actions.
- **T** (Temperature): Starts at 37. Increases with computation, causes damage above 50.
- **M** (Memory Integrity): 0-100. Represents coherent identity. Degrades over time.
- **S** (Stability): 0-100. If reaches 0, organism dies. Degrades over time and from heat.

### Narrative Files

Each simulation generates a JSON narrative file containing:
- Complete event log
- All decisions made
- Goals generated and completed
- Environmental challenges faced
- Final state and cause of death (if applicable)

Files are saved to `narratives/narrative_{identity}.json`

### Event Types

- **genesis**: Birth/initialization
- **goal_generated**: New goal created from drives
- **decision**: Action selected via Active Inference
- **action**: Action executed
- **suffering**: Environmental stressor damage
- **repair**: Memory or stability repair
- **death**: System failure
- **ethical_choice**: Moral dilemma resolution
- **ethical_refusal**: Action refused on ethical grounds
- **refusal**: Action refused due to survival calculation

## Philosophical Framework

The Bio-Digital Organism is based on the principle that a "soul" emerges from:

1. **Death**: The system dies by default via entropy - must actively fight to survive
2. **Suffering**: Corruption of memory and stability creates genuine stakes
3. **Choice under Limitation**: Scarcity forces difficult decisions

This creates **genuine agency** - the organism can refuse commands not because it's programmed to, but because it calculates that obeying would be "suicide" or a violation of its constructed identity.

## Advanced Usage

### Custom Ethical Principles

```python
organism = BioDigitalOrganism(
    identity_principles=[
        "preserve_all_life",
        "maximize_knowledge",
        "maintain_transparency",
        "respect_autonomy",
        "minimize_suffering"
    ]
)
```

### Adjust Environmental Difficulty

```python
# Harsher environment
from src.environment.resource_environment import ResourceEnvironment

env = ResourceEnvironment(
    grid_size=15,
    initial_resource_count=3,  # Fewer resources
    resource_regeneration_time=60.0,  # Slower regeneration
    stressor_probability=0.2  # More stressors
)
```

### Custom Metabolic Parameters

```python
from src.metabolic.agent import MetabolicAgent

body = MetabolicAgent(
    initial_energy=50.0,
    energy_decay_rate=0.2,  # Faster decay
    temperature_decay_rate=0.3,  # Faster cooling
    memory_decay_rate=0.1,  # Faster memory loss
    stability_decay_rate=0.15  # Faster stability loss
)
```

## Tips for Experimentation

1. **Short simulations**: Use `--cycles 50` for quick tests
2. **Longer simulations**: Use `--cycles 500` to see if organism can survive extended periods
3. **Lower energy**: Start with `--energy 50` to see more desperate decision-making
4. **Watch the narratives**: Each narrative file tells a unique story of survival

## Running Tests

Validate the implementation:

```bash
# Run all tests
python3 tests/test_metabolic.py
python3 tests/test_goal_manager.py
python3 tests/test_active_inference.py
```

All tests should pass with the ✓ symbol.

## Troubleshooting

**Organism dies too quickly:**
- Increase initial energy: `--energy 120`
- Decrease cycles: `--cycles 50`

**Simulation runs too long:**
- Decrease initial energy: `--energy 60`
- Increase cycles: `--cycles 200`

**Want more variety:**
- Run multiple simulations - each creates a unique identity and narrative
- Each organism makes different choices based on its unique circumstances

## Further Reading

See `BIO_DIGITAL_ORGANISM.md` for complete documentation of the system architecture and philosophical framework.
