# GhostStack Stopping Points

**How much of GhostStack do you actually need?**

Use this decision tree to identify the minimum set of layers for your use case,
then stop there.  You can always add layers later — each layer is independent
and builds cleanly on the one below.

---

## Decision tree

```
Do you need agents to communicate when some are offline?
  │
  ├─ YES → You need Layer 1 (offline-first messaging)
  │          Stop here if: you only need message delivery with no governance
  │          → Run: 01_layer1_messaging.py
  │          → See: Section 2 of TUTORIAL.md
  │
  └─ NO  → You can skip Layer 1 and use simple in-process calls

Do you need identity, proposals, voting, or trust scoring?
  │
  ├─ YES → You need Layer 2 (governance & trust)
  │          Stop here if: you want governance but no AI decision-making
  │          → Run: 02_layer2_governance.py
  │          → See: Section 3 of TUTORIAL.md
  │
  └─ NO  → You can skip Layer 2

Do you want agents that form opinions and make autonomous decisions?
  │
  ├─ YES → You need Layer 3 (brain simulation)
  │          Stop here if: you want a personal cognitive agent
  │          but don't need it to interact with others yet
  │          → Run: 03_layer3_brain.py
  │          → See: Section 4 of TUTORIAL.md
  │
  └─ NO  → You can skip Layer 3

Do you want a single agent that governs AND reasons?
  │
  ├─ YES → You need the Bridge layer (GhostAgent)
  │          Stop here if: you're running a single-node setup
  │          → Run: 04_bridge_agent.py
  │          → See: Section 5 of TUTORIAL.md
  │
  └─ NO  → You can skip the bridge layer

Do you need multiple agents to coordinate, sync, and govern together?
  │
  └─ YES → You need the full multi-agent stack
             → Run: 05_multi_agent_demo.py
             → See: Section 6 of TUTORIAL.md
             → Then follow Section 7 for the hardening roadmap
```

---

## Profiles at a glance

### Just messaging

> *"I need nodes to exchange messages reliably even when some are offline."*

**Use:** Layer 1 only

**Components needed:**
- `MeshDaemon` (or a real transport)
- `MessageQueue` (SQLite)
- `sync_deliver()`

**What you skip:** governance, reputation, incentives, cognition

**Example:** `01_layer1_messaging.py`

---

### Governance without AI

> *"I need a group of nodes to make collective decisions and keep an
> immutable audit trail — no autonomous AI decision-making."*

**Use:** Layer 1 + Layer 2

**Components needed:**
- Everything from "Just messaging"
- `DIDService`, `GovernanceService`
- `ReputationService`, `IncentiveService`

**What you skip:** brain simulation, autonomous action proposals

**Examples:** `01_layer1_messaging.py`, `02_layer2_governance.py`

---

### Personal agent with governance

> *"I want an agent that reasons autonomously and participates in governance,
> but I'm only running one node."*

**Use:** Layers 1 + 2 + 3 + Bridge

**Components needed:**
- All previous components
- `BrainSimulation` (LimbicSystem, FrontalLobe, Hippocampus)
- `GhostAgent` (bridge combining all layers)

**What you skip:** multi-agent coordination

**Examples:** `01_layer1_messaging.py` through `04_bridge_agent.py`

---

### Full multi-agent system

> *"I want multiple autonomous agents that reason, communicate, and govern
> together — including offline-then-sync scenarios."*

**Use:** All layers

**Components needed:** Everything

**Examples:** All five scripts

**Next step:** Follow the hardening roadmap in Section 7 of TUTORIAL.md

---

### Production system

> *"I want to deploy this in a real cell (3–7 nodes) with real networking."*

**Use:** All layers + hardening roadmap

**Required hardening (Section 7 of TUTORIAL.md):**
1. Replace `MeshDaemon` with cjdns / BATMAN-adv / libp2p
2. Add signed envelopes, ACK tracking, replay protection
3. Harden identity with ed25519 and W3C DID Documents
4. Add governance lifecycle (quorum, expiration, fork manifests)
5. Add reputation decay and sybil resistance

---

## Component dependency map

```
05_multi_agent_demo ──► GhostAgent (bridge)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         Layer 1          Layer 2         Layer 3
     (Messaging)       (Governance)     (Cognition)
    MeshDaemon         DIDService       BrainSimulation
    MessageQueue       GovernanceService  LimbicSystem
    sync_deliver()     ReputationService  FrontalLobe
    Inbox              IncentiveService   Hippocampus
```

Each layer is **independently usable** — you can import and instantiate any
layer's classes without instantiating the others.

---

## Estimated complexity

| Profile | Lines of code to understand | Setup time |
|---------|---------------------------|-----------|
| Just messaging | ~100 | 15 min |
| + Governance | ~250 | 30 min |
| + Cognition | ~400 | 45 min |
| + Bridge agent | ~500 | 1 hour |
| Full multi-agent | ~600 | 1.5 hours |
| Production-ready | Much more | Weeks |

---

*For the full guide see [docs/TUTORIAL.md](TUTORIAL.md).*
*For the 5-command quick start see [docs/QUICKSTART.md](QUICKSTART.md).*
