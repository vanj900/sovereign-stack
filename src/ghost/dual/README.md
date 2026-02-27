# Ghost Dual

> **This is NOT core Ghost. Pure axiom extension. Fork it or die.**

## What This Is

A two-process, thermodynamically-constrained AI daemon that lives entirely in
`/dev/shm/ghost_dual/` (tmpfs).  Kill it, reboot, or run out of energy and it
is *gone*.  The only thing that survives is a **signed MindSeed Receipt** you
carry out by hand.

## Axioms (violate and it rejects)

| # | Axiom | Consequence |
|---|-------|-------------|
| 1 | **Flow over Containment** | All state in `/dev/shm/ghost_dual/` only.  No `.pkl`, no disk files. |
| 2 | **Sovereignty via Forkability** | Instance dies completely on Ctrl-C.  New cell imports MindSeed → fresh spawn. |
| 3 | **Truth by Receipts** | Every event = HMAC-signed receipt posted to the in-RAM deed-ledger. Human veto is mandatory and highest priority. |

## Files

| File | Role |
|------|------|
| `ghost_dual_daemon.py` | Main entry — starts fast + slow, runs human veto pipe |
| `fast_model.py` | 5-second reactive pulse, mask system (Healer / Judge / Courier) |
| `slow_model.py` | 30-60s deliberative cycle, Friston active-inference, ethical checks |
| `shared_state.py` | `/dev/shm` wrapper + `thermodynamic_agency` metrics + decay |
| `receipt_logger.py` | HMAC-SHA256 signing → deed-ledger (JSONL in shm) |
| `mindseed.py` | Export / import the signed MindSeed Receipt |
| `setup_dual.sh` | Bootstrap: create shm dir, check Ollama, chmod |
| `README.md` | This file |

## Quick Start

```bash
# 1. Bootstrap
bash src/ghost/dual/setup_dual.sh

# 2. Pull models (if not already present)
ollama pull phi3:mini
ollama pull llama3.2:3b

# 3. Run
cd src/ghost/dual
python ghost_dual_daemon.py
```

### Human Veto Pipe

At the `ghost>` prompt:

| Command | Effect |
|---------|--------|
| `v` | Set veto flag — Judge mask activates on next fast pulse; receipt posted |
| `q` | Quit — MindSeed exported, shm wiped |
| `s` | Print current E/T/M/S metrics |
| `x` | Export MindSeed to `/dev/shm/ghost_dual/mindseed.json` |

## Exporting a MindSeed

```bash
# At the ghost> prompt:
ghost> x
# → /dev/shm/ghost_dual/mindseed.json

# Copy it out BEFORE the ghost dies:
cp /dev/shm/ghost_dual/mindseed.json /tmp/my_mindseed.json
```

On a clean shutdown (`q`) the daemon auto-saves a MindSeed to
`/tmp/mindseed_<timestamp>.json`.

## Importing a MindSeed (fork a new cell)

```bash
python ghost_dual_daemon.py --seed /tmp/my_mindseed.json
```

The new instance inherits E/T/M/S/pulse/mask from the receipt and begins
decaying from there.  Signature is checked; unknown schemas are rejected.

## Forking a New Cell

1. Export MindSeed from the running ghost (`x` or `q`).
2. Copy the JSON somewhere outside `/dev/shm`.
3. Kill the old ghost (Ctrl-C or `q`) — shm is wiped completely.
4. Spawn a new process with `--seed path/to/mindseed.json`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GHOST_FAST_MODEL` | `phi3:mini` | Ollama model for fast process |
| `GHOST_SLOW_MODEL` | `llama3.2:3b` | Ollama model for slow process |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API base URL |

## Thermodynamic Constraints

Uses `thermodynamic_agency.core.MetabolicEngine` (from `src/ai/thermo-ai`).

- **Fast pulse**: costs `1.0 J` per cycle.
- **Slow cycle**: costs `5.0 J` per cycle (3-5× as required by axiom).
- Passive decay runs every pulse.
- Death exceptions (`EnergyDeath`, `ThermalDeath`, `MemoryCollapse`, `EntropyDeath`) terminate the offending process and set `shared["alive"] = False`.

## License

See repository root `LICENSE`.
