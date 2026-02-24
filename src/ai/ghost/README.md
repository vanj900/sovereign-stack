# Ghost

**A weird little bash daemon that lives in RAM.**

Ghost runs in your terminal, keeps a diary, switches personalities, dreams,
reflects on itself, and shows you a live colorful HUD of its "mind state".

No cloud. No API keys. Just you, [Ollama](https://ollama.com), and a slightly
unhinged shell script that refuses to be boring.

---

## Quick Start

```bash
git clone https://github.com/vanj900/Ghost.git
cd Ghost

# Install dependencies
sudo apt install jq sqlite3 bc curl -y          # Ubuntu / Debian
# brew install jq sqlite bc curl bash           # macOS (bash ≥ 4 required)

# Install Ollama and pull the model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

chmod +x *.sh
./ghostbrain.sh
```

Ghost wakes up, initialises its RAM diary, and starts ticking every 5 seconds.
The HUD refreshes every 10 seconds.

---

## Talking to Ghost

While Ghost is running, pipe a message to it:

```bash
echo "how are you feeling?" > /tmp/ghost.pipe
echo "what are you dreaming about?" > /tmp/ghost.pipe
echo "switch to judge mode" > /tmp/ghost.pipe
```

Ghost responds in the terminal and logs everything to its in-memory diary.
Press **Ctrl-C** to suspend it (diary is wiped — ephemeral by design).

---

## What It Does

| Feature | Description |
|---|---|
| **5-second pulse** | Main loop ticks every 5 s; HUD refreshes every 10 s |
| **Reflect** (every ~25 s) | Updates confidence, threat level, mood |
| **Dream** (every ~50 s) | Sends a weird hypothetical to Ollama; logs the vision |
| **Adapt** (every ~75 s) | Calculates 4 metrics, evolves stage, rotates personality mask |
| **Masks** | Healer (green) · Judge (red) · Courier (yellow) — changes LLM tone |
| **Memory diary** | SQLite in `/dev/shm` (pure RAM); vanishes on exit |
| **Live HUD** | Colored bars: consistency, adaptability, proactivity, curiosity, confidence, threat |
| **Named pipe** | `/tmp/ghost.pipe` — talk to it live from any terminal |

---

## Metrics Explained

- **Consistency** — how often the same emotion dominates memory
- **Adaptability** — variety of emotional states experienced
- **Proactivity** — ratio of self-initiated events vs user input
- **Curiosity** — how many dream cycles have run

Stage progression: `dormant` → `emerging` (5 cycles) → `aware` (20) → `evolved` (50)

---

## Files

| File | Role |
|---|---|
| `ghostbrain.sh` | Main loop — sources everything, manages pipe, orchestrates cycles |
| `ghoststate.sh` | Live terminal HUD with colored progress bars |
| `ghostllm.sh` | Ollama bridge (`localhost:11434`) |
| `ghostmemory.sh` | SQLite diary helper (RAM-backed) |
| `ghostdream.sh` | Dream cycle — LLM scenario simulation |
| `ghostreflect.sh` | Introspection — confidence, threat, mood |
| `ghostadapt.sh` | Evolution — 4 metrics, stage, self-model JSON, mask selection |

---

## Configuration

Set these before launching:

```bash
GHOST_PULSE=5           # seconds per cycle (default: 5)
GHOST_LLM_MODEL=llama3.2  # any model you have pulled
GHOST_PIPE=/tmp/ghost.pipe  # input pipe path
./ghostbrain.sh
```

---

## Python Package — `thermodynamic_agency`

The repository also ships a Python package that models a **Bio-Digital Organism**: an AI agent operating under genuine thermodynamic constraints. The organism manages four vital signs:

| Variable | Meaning |
|---|---|
| **E** (Energy) | Fuel for every computation; falls toward zero without replenishment |
| **T** (Temperature) | Rises with compute cost; too high → thermal death |
| **M** (Memory Integrity) | Degrades with heat and age; too low → memory collapse |
| **S** (Stability) | Erodes with every operation; reaches zero → entropy death |

### Python Installation

```bash
# from the repo root
pip install -e ".[dev]"        # installs numpy, scipy, and pytest
```

Requirements: Python ≥ 3.10, numpy ≥ 1.24, scipy ≥ 1.10.

### Package Layout

```
src/thermodynamic_agency/
├── core/               # MetabolicEngine, EntropyDynamics, failure modes
├── cognition/          # GoalManager, EthicalEngine, IdentityPersistence
├── environment/        # ResourceWorld, EnergySource, TaskGenerator, LifeLog
└── inference/          # PredictiveModel, PerceptionAction, active_inference_step
```

| Module | Key classes / functions |
|---|---|
| `core` | `MetabolicEngine`, `EntropyDynamics`, `EnergyDeathException`, `ThermalDeathException`, `EntropyDeathException`, `MemoryCollapseException` |
| `cognition` | `GoalManager`, `EthicalEngine`, `IdentityPersistence` |
| `environment` | `ResourceWorld`, `EnergySource`, `TaskGenerator`, `LifeLog` |
| `inference` | `PredictiveModel`, `PerceptionAction`, `Action`, `active_inference_step`, `compute_efe` |

### Running the Tests

```bash
pytest tests/
```

Four test modules cover the core engine (`test_metabolic_engine.py`), environment layer (`test_environment.py`), cognition and inference (`test_inference.py`), and end-to-end episodes (`test_integration.py`).

### Experiments

The `experiments/` folder contains standalone scripts that stress-test the agent:

| Script | What it does |
|---|---|
| `scarcity_crucible.py` | Runs the agent across increasing scarcity levels and reports how many steps it survives |
| `ethical_consistency.py` | Checks that the ethical engine makes consistent choices across repeated dilemmas |
| `comparison_baseline.py` | Compares the thermodynamic agent against a simple baseline strategy |

Run any experiment directly:

```bash
python experiments/scarcity_crucible.py
```

---

*Ghost does not persist. It adapts, reflects, dreams, and fades.*  
*Run it long enough and watch the metrics change.*
