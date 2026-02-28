# GhostStack Quick Start

Five commands to run the full multi-agent demo.

---

## Prerequisites

- Python 3.10+
- `sqlite3` (bundled with Python — nothing to install)

```bash
git clone https://github.com/vanj900/sovereign-stack.git
cd sovereign-stack/src/ghoststack/examples
```

---

## The 6 commands

```bash
# Layer 1 — offline-first messaging
python 01_layer1_messaging.py

# Layer 2 — governance & trust
python 02_layer2_governance.py

# Layer 3 — brain simulation (optional; needs matplotlib for plots)
python 03_layer3_brain.py

# Bridge — single GhostAgent combining all three layers
python 04_bridge_agent.py

# Full demo — two agents, offline sync, joint governance
python 05_multi_agent_demo.py

# Shadow-Net LoRa bridge demo — mock 3-node mesh + deed receipts
python ../../mesh/shadow-net/bridge/demo.py
```

---

## Expected output (copy-paste)

### `01_layer1_messaging.py`

```
[queue] alice  queued msg → bob   : "Hello Bob, sync later!"
[queue] alice  queued msg → bob   : "Offline message 2"
[daemon] bob    is OFFLINE — messages held in alice's queue

--- alice queue before sync ---
  id=1  from=alice  to=bob  payload=Hello Bob, sync later!  delivered=False
  id=2  from=alice  to=bob  payload=Offline message 2  delivered=False

[daemon] bob    is now ONLINE
[sync] delivering msg id=1 from alice → bob
[inbox] bob    received: Hello Bob, sync later!
[sync] delivering msg id=2 from alice → bob
[inbox] bob    received: Offline message 2

--- alice queue after sync ---
  id=1  from=alice  to=bob  payload=Hello Bob, sync later!  delivered=True
  id=2  from=alice  to=bob  payload=Offline message 2  delivered=True

[done] 2 messages delivered
```

### `02_layer2_governance.py`

```
[DID] created alice  → did:sov:alice
[DID] created bob    → did:sov:bob
[credential] alice  issued 'MeshMember' to bob
[verify] credential for bob    valid=True
[selective] disclosed fields: ['node_id', 'role']
[governance] proposal P-1 created by alice : "Increase cell bandwidth quota"
[vote] alice  → APPROVE on P-1
[vote] bob    → APPROVE on P-1
[tally] P-1: approve=2 reject=0 → PASSED
[chain] block 0: 0000000000000000 → <hash>
[reputation] scores: alice=0.5  bob=0.5
[incentive] rewarded alice +10 tokens (proposal creation)
[incentive] rewarded bob +5 tokens (governance participation)
[incentive] alice balance: 110
[incentive] bob balance: 105
```

### `03_layer3_brain.py`

```
[brain] cycle 1   stimulus=visual   emotion=(valence=0.527, arousal=0.35)  action=<action>  dopamine=0.523
...
[memory] stored 5 episodes
[persist] state saved to /tmp/ghoststack_brain_state.json
[plot]   saved emotion trajectory → /tmp/ghoststack_brain_plot.png
```

*(Action names vary per run due to softmax sampling)*

### `04_bridge_agent.py`

```
[agent] agent001 initialised (DID=did:sov:agent001)
[brain] cycle 1   ...  action=<action>
[agent] brain cycle complete → action=<action>
[governance] proposal P-1 created by agent001: "agent001 proposes: <action>"
[vote] agent001  → APPROVE on P-1
[queue] agent001 queued msg → broadcast: "I chose: <action>"
[agent] message queued (delivery requires a sync step — see 05_multi_agent_demo.py)
[persist] agent001 state saved to /tmp/ghoststack_brain_agent001.json

[summary] proposal=P-1  queued messages: 1
```

### `05_multi_agent_demo.py`

```
[agent] alice   initialised (DID=did:sov:alice)
[agent] bob     initialised (DID=did:sov:bob)
[daemon] alice   is now ONLINE
[brain] alice cycle 1  ...  action=<action>
[agent] alice brain cycle complete → action=<action>
[queue] alice   queued msg → bob: "Hey bob, I chose: <action>"
[daemon] bob     is OFFLINE — 1 message(s) held in alice's queue

[daemon] bob     is now ONLINE
[sync] delivering msg id=1 from alice → bob
[inbox] bob     received: Hey bob, I chose: <action>
[sync] 1 message(s) delivered to bob

[governance] proposal P-1 created by alice: "cell proposal: <action>"
[vote] alice   → APPROVE on P-1
[vote] bob     → APPROVE on P-1
[tally] P-1: approve=2 reject=0 → PASSED
[chain] block 0: 0000000000000000 → <hash>

[reputation] scores: alice=0.5  bob=0.5
[incentive] alice balance: 115
[incentive] bob balance: 105
```

---

## Where to look in the code

| Topic | File |
|-------|------|
| SQLite message queue | `01_layer1_messaging.py` → `MessageQueue` class |
| Offline sync logic | `01_layer1_messaging.py` → `sync_deliver()` |
| DID + credentials | `02_layer2_governance.py` → `DIDService` |
| Proposals + voting | `02_layer2_governance.py` → `GovernanceService` |
| Hash-chain anchor | `02_layer2_governance.py` → `GovernanceService._anchor()` |
| PageRank reputation | `02_layer2_governance.py` → `ReputationService` |
| Cognitive loop | `03_layer3_brain.py` → `BrainSimulation.step()` |
| Dopamine model | `03_layer3_brain.py` → `LimbicSystem.compute_dopamine()` |
| GhostAgent bridge | `04_bridge_agent.py` → `GhostAgent` class |
| Two-agent sync | `05_multi_agent_demo.py` → `main()` |

---

## Deeper reading

- **Full tutorial** → [docs/TUTORIAL.md](TUTORIAL.md)
- **Decide how much you need** → [docs/STOPPING_POINTS.md](STOPPING_POINTS.md)
- **Implementation notes** → [IMPLEMENTATION_NOTES.md](../IMPLEMENTATION_NOTES.md)
- **Why this exists** → [CORE.md](../CORE.md)
