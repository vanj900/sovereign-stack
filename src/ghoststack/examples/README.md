# GhostStack Examples

Runnable Python scripts that walk you through each layer of the GhostStack
middleware.  Every script is **self-contained** — just run it with a plain
Python 3.10+ interpreter; no extra packages are required (matplotlib is
optional for plots in Layer 3).

---

## Quick reference

| Script | Layer | What it shows |
|--------|-------|---------------|
| [`01_layer1_messaging.py`](01_layer1_messaging.py) | 1 | Offline → online message sync via SQLite queue |
| [`02_layer2_governance.py`](02_layer2_governance.py) | 2 | DIDs, credentials, proposals, voting, reputation, incentives |
| [`03_layer3_brain.py`](03_layer3_brain.py) | 3 | Cognitive loop: stimulus → emotion → action → memory |
| [`04_bridge_agent.py`](04_bridge_agent.py) | Bridge | Single GhostAgent combining all three layers |
| [`05_multi_agent_demo.py`](05_multi_agent_demo.py) | Full | Two agents, offline sync, multi-agent governance |

---

## Running the examples

```bash
# From the repo root
cd src/ghoststack/examples

python 01_layer1_messaging.py
python 02_layer2_governance.py
python 03_layer3_brain.py
python 04_bridge_agent.py
python 05_multi_agent_demo.py
```

Each script prints annotated output so you can follow every step.

---

## What each example covers

### `01_layer1_messaging.py`
Sets up a `MeshDaemon` (placeholder transport) and a `MessageQueue`
(SQLite-backed).  Alice queues two messages while Bob is offline.  The queue
contents are printed before and after Bob comes online and a `sync_deliver`
pass transfers the messages.

### `02_layer2_governance.py`
Covers the full governance stack:
- `DIDService` — create DIDs, issue credentials, verify, selectively disclose
- `GovernanceService` — proposals, votes, hash-chain anchoring
- `ReputationService` — PageRank-style trust scoring
- `IncentiveService` — token balance and rewards

### `03_layer3_brain.py`
Runs a 5-step cognitive simulation:
- `SensoryProcessor` — normalises stimuli
- `LimbicSystem` — emotional valence/arousal with decay
- `FrontalLobe` — softmax action selection
- `Hippocampus` — episodic memory
- Dopamine reward-prediction-error model
- Saves state to `/tmp/ghoststack_brain_state.json` (persistent across runs)
- Optionally plots emotion & dopamine trajectories if `matplotlib` is installed

### `04_bridge_agent.py`
Introduces `GhostAgent` — a single entity that runs a brain cycle, creates a
governance proposal from the chosen action, and queues a message for later
delivery.

### `05_multi_agent_demo.py`
Full multi-agent scenario:
- Two agents (alice, bob) with independent brains
- Alice comes online first, queues a message for the still-offline Bob
- Bob comes online; sync delivers
- Both vote on a joint governance proposal
- Reputation scores and incentive balances are printed

---

## Detailed tutorial

See [`docs/TUTORIAL.md`](../../docs/TUTORIAL.md) for the complete step-by-step
guide including architecture diagrams, code walkthroughs, and the hardening
roadmap.

See [`docs/QUICKSTART.md`](../../docs/QUICKSTART.md) for a 5-command summary.

See [`docs/STOPPING_POINTS.md`](../../docs/STOPPING_POINTS.md) to decide which
layers you actually need.
