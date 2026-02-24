# Results Documentation

This directory contains all experimental results, visualizations, and analysis outputs from the Thermo-AI Bio-Digital Organism validation suite.

## Directory Structure

```
results/
├── README.md                    # This file
├── trajectories/                # Energy, temperature, memory, stability trajectories
├── bifurcations/                # Divergence analysis and decision trees
├── entropy/                     # Entropy generation and heat dissipation plots
├── survival/                    # Survival curves and lifetime analysis
├── tuning/                      # Parameter tuning results and recommendations
├── emergence_reports/           # HTML reports from test runs
└── notebooks/                   # Jupyter notebooks for interactive analysis
```

## Subdirectory Details

### `trajectories/`
Contains time-series plots of metabolic state variables:
- **Individual trajectories**: E, T, M, S over time for single agents
- **Multi-agent comparisons**: Multiple agents on same plot
- **State variable grids**: 2x2 comparison of all four variables

**Key files:**
- `*_trajectory.png` - Single agent trajectory with death markers
- `multi_agent_*.png` - Comparative plots across agents
- `state_variables_grid.png` - Complete state space overview

**Interpretation:**
- Energy (E) drops indicate resource consumption
- Temperature (T) spikes show computational activity
- Memory (M) degradation indicates thermal damage
- Stability (S) decline shows entropy accumulation
- Death markers indicate failure mode locations

### `bifurcations/`
Analyzes how identical initial conditions produce divergent outcomes:
- **Trajectory divergence**: Shows behavioral splitting over time
- **Parameter bifurcations**: Critical parameter values causing regime changes
- **Decision trees**: Ethical dilemma choice patterns
- **Phase space plots**: 2D projections of state trajectories

**Key files:**
- `trajectory_divergence.png` - Divergence growth from identical start
- `parameter_bifurcation_*.png` - Outcome changes with parameters
- `phase_space_*.png` - State space topology

**Interpretation:**
- Growing divergence indicates stochastic emergence of uniqueness
- Bifurcation points show where system behavior fundamentally changes
- Phase space attractors indicate stable behavioral patterns

### `entropy/`
Thermodynamic analysis of entropy generation and dissipation:
- **Entropy dynamics**: Generation vs. export rates
- **Heat dissipation**: Temperature regulation patterns
- **Thermodynamic efficiency**: Useful work per energy spent

**Key files:**
- `*_entropy.png` - Entropy generation and cumulative plots
- `*_heat.png` - Heat generation/dissipation balance
- `*_efficiency.png` - Energy utilization efficiency

**Interpretation:**
- High entropy generation = rapid deterioration
- Effective heat dissipation = survival through cooling
- Low efficiency = wasteful energy use (indicates poor decisions)

### `survival/`
Statistical analysis of organism lifetimes:
- **Survival curves**: Kaplan-Meier style probability plots
- **Lifetime vs. scarcity**: How resource availability affects survival
- **Survival heatmaps**: Parameter combinations and survival rates
- **Death cause distributions**: Which failure modes dominate

**Key files:**
- `survival_curves.png` - Survival probability over time by configuration
- `lifetime_vs_scarcity.png` - Scatter plot with trend line
- `survival_heatmap_*.png` - Parameter space survival analysis
- `death_causes.png` - Distribution of failure modes

**Interpretation:**
- Steep survival curves = harsh conditions
- Flat curves = abundant resources
- Survival at high scarcity = emergent skill
- Diverse death causes = multiple failure modes active

### `tuning/`
Parameter optimization results:
- **Grid search results**: Complete parameter sweep data
- **Parameter space heatmaps**: Visual guide to behavioral regimes
- **Tuning reports**: Recommended parameter ranges
- **Regime identification**: Balanced, high-Φ, high-divergence configurations

**Key files:**
- `tuning_results.json` - Raw data from all parameter combinations
- `parameter_space_analysis.png` - 4-panel heatmap overview
- `tuning_report.md` - Human-readable recommendations

**Interpretation:**
- **Balanced regime**: Death is challenging but avoidable (recommended)
- **High-Φ regime**: Maximum integrated information emergence
- **High-divergence regime**: Maximum behavioral uniqueness
- **Extreme regime**: High difficulty for testing edge cases

### `emergence_reports/`
Comprehensive HTML reports from test runs:
- Test suite results (pass/fail)
- Aggregate metrics across all agents
- Individual agent performance
- Embedded visualizations
- Key findings summary

**Key files:**
- `report_YYYYMMDD_HHMMSS.html` - Timestamped test reports

**Interpretation:**
- Green status = all tests passed
- Red status = test failures (investigate logs)
- Φ > 0.3 indicates strong coherence
- Divergence > 0.2 indicates meaningful uniqueness

### `notebooks/`
Interactive Jupyter notebooks for deeper analysis:
- `emergence_analysis.ipynb` - Main analysis notebook
- Custom analyses and visualizations
- Parameter exploration widgets
- Comparative studies

## Key Metrics Reference

### Φ (Integrated Information)
- **Range**: [0, 1]
- **Meaning**: How coherently the system behaves (correlation between state variables)
- **Good values**: > 0.2 indicates emergence of integrated behavior
- **Low values**: < 0.1 suggests decoupled, incoherent dynamics

### Divergence Index
- **Range**: [0, 1]
- **Meaning**: How much agents with identical parameters diverge
- **Good values**: > 0.15 shows meaningful behavioral uniqueness
- **Low values**: < 0.05 suggests deterministic, non-emergent behavior

### Survival Efficiency
- **Range**: [0, ∞)
- **Meaning**: Lifetime achieved per unit energy consumed
- **Good values**: Higher is better, > 0.5 indicates efficient resource use
- **Low values**: < 0.2 suggests poor decision-making or harsh conditions

### Identity Coherence
- **Range**: [0, 1]
- **Meaning**: Consistency of agent's narrative identity
- **Good values**: > 0.6 indicates stable sense of self
- **Low values**: < 0.3 suggests identity fragmentation

### Thermal Stress Index
- **Range**: [0, 1]
- **Meaning**: How close to thermal death
- **Safe**: < 0.3
- **Warning**: 0.3 - 0.7
- **Critical**: > 0.7

## Recommended Parameter Ranges

Based on parameter tuning results:

### For Emergence Demonstrations
```yaml
E_max: 80-100
scarcity: 0.5-0.6
max_steps: 100-150
```
- Balanced difficulty
- Death is avoidable with skill
- Good Φ and divergence

### For Long-term Studies
```yaml
E_max: 120-150
scarcity: 0.3-0.4
max_steps: 200-500
```
- Extended survival possible
- Observe value evolution over time
- Rich behavioral patterns

### For Stress Testing
```yaml
E_max: 40-60
scarcity: 0.8-0.95
max_steps: 30-50
```
- High difficulty
- Rapid death common
- Tests failure mode robustness

## Interpreting Results

### Signs of Healthy Emergence
- ✓ Φ > 0.2 (integrated behavior)
- ✓ Divergence > 0.15 (behavioral uniqueness)
- ✓ Variable lifetimes (not all dying at same time)
- ✓ Multiple death causes (all failure modes active)
- ✓ Near-death experiences > 0 (struggle for survival)
- ✓ Ethical weight evolution (value changes through experience)

### Warning Signs
- ✗ Φ < 0.1 (incoherent dynamics)
- ✗ Divergence < 0.05 (deterministic behavior)
- ✗ All agents die at same step (too harsh or too easy)
- ✗ Single dominant death cause (other modes not functioning)
- ✗ No near-death experiences (too easy, no stakes)
- ✗ No ethical evolution (no learning from trauma)

## Running New Experiments

### Quick Test
```bash
python experiments/run_emergence_tests.py --quick
```

### Full Test Suite
```bash
python experiments/run_emergence_tests.py --num-agents 10
```

### Parameter Tuning
```bash
python experiments/parameter_tuning.py
```

### Individual Tests
```bash
pytest tests/emergence_tests.py -v
```

### Interactive Analysis
```bash
jupyter notebook results/notebooks/emergence_analysis.ipynb
```

## Reproducibility

All experiments use:
- Fixed random seeds (when specified)
- Configuration files in `config/`
- Timestamped outputs
- Version-tracked parameters

To reproduce results:
1. Use same configuration file
2. Set random seed explicitly
3. Use same software versions (see `requirements.txt`)

## Citation

If you use these results in research:

```
Thermo-AI Bio-Digital Organism - Emergence Validation Suite
https://github.com/vanj900/Thermo-AI
2026
```

## Support

For questions about interpreting results:
- Review this README
- Check experiment configs in `config/experiment_configs.yaml`
- See main project documentation in root `README.md`
- Open an issue on GitHub

---

**Last Updated**: 2026-02-09
**Version**: 1.0
