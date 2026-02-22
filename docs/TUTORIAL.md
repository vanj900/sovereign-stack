# GhostStack Tutorial: From Zero to Running

**A practical, step-by-step guide that takes you from zero to a working
multi-agent GhostStack system in under an hour.**

---

## Prerequisites

- Python 3.10 or newer
- `sqlite3` (bundled with Python)
- `matplotlib` *(optional, for brain-simulation plots)*

```bash
# Verify Python version
python --version    # must be 3.10+

# Optional: install matplotlib for Layer 3 plots
pip install matplotlib
```

---

## How this guide is organised

| Section | What you build | Estimated time |
|---------|----------------|----------------|
| [Section 0](#section-0-what-youre-building) | Architecture overview | 5 min |
| [Section 1](#section-1-environment-setup) | Clone & verify | 5 min |
| [Section 2](#section-2-layer-1--offline-first-messaging) | Messaging (SQLite queue + sync) | 15 min |
| [Section 3](#section-3-layer-2--governance--trust) | DIDs, proposals, reputation | 15 min |
| [Section 4](#section-4-layer-3-optional--brain-simulation) | Cognitive loop (optional) | 15 min |
| [Section 5](#section-5-bridge-layer--ghostagent) | Single GhostAgent | 10 min |
| [Section 6](#section-6-multi-agent-integration) | Two agents, sync, governance | 10 min |
| [Section 7](#section-7-hardening-roadmap) | Path to production | 5 min |

**Not sure how far to go?** → See [STOPPING_POINTS.md](STOPPING_POINTS.md)

---

## Section 0: What You're Building

GhostStack is a three-layer middleware stack for sovereign, offline-capable,
multi-agent systems.

```
┌────────────────────────────────────────────────────────────────────┐
│  Layer 3 (Optional): Agent Cognition                               │
│    BrainSimulation · LimbicSystem · FrontalLobe · Hippocampus      │
├────────────────────────────────────────────────────────────────────┤
│  Layer 2: Governance & Trust                                       │
│    DIDService · GovernanceService · ReputationService              │
│    IncentiveService                                                │
├────────────────────────────────────────────────────────────────────┤
│  Layer 1: Offline-First Messaging                                  │
│    MeshDaemon · MessageQueue (SQLite) · sync_deliver               │
└────────────────────────────────────────────────────────────────────┘
             ▲ bridges to ▼
┌────────────────────────────────────────────────────────────────────┐
│  GhostAgent (Bridge): combines all three layers                    │
│    run_brain_cycle() · propose_action() · send_message()           │
└────────────────────────────────────────────────────────────────────┘
```

### Expected runtime behaviour

After completing all sections you will be able to run a demo where:

1. Two agents start with independent cognitive states.
2. Agent Alice comes online, runs a brain cycle, and queues a message.
3. Agent Bob is offline — Alice's message is held in the SQLite queue.
4. Bob comes online — a sync pass delivers the queued message.
5. Both agents participate in a governance proposal and vote.
6. Reputation scores and incentive balances are updated.

### Minimum viable stopping points

| Need | Stop after |
|------|-----------|
| Just offline messaging | Section 2 (Layer 1) |
| Governance without AI | Section 3 (Layer 2) |
| Personal agent with governance | Section 5 (Bridge) |
| Full multi-agent system | Section 6 |
| Production-ready | Section 7 + hardening work |

---

## Section 1: Environment Setup

```bash
# Clone the repository
git clone https://github.com/vanj900/sovereign-stack.git
cd sovereign-stack

# Navigate to the examples directory
cd src/ghoststack/examples

# Verify Python (no other dependencies required for Layers 1-2)
python --version

# Optional: install matplotlib for brain-simulation plots
pip install matplotlib
```

All example scripts use only the Python standard library
(`sqlite3`, `hashlib`, `json`, `math`, `os`, `random`, `tempfile`, `time`,
`uuid`) plus the optional `matplotlib`.

---

## Section 2: Layer 1 — Offline-First Messaging

> **Goal:** Understand how messages survive offline periods and are delivered
> once a peer reconnects.

### Architecture

```
Alice node                         Bob node
─────────                          ────────
MessageQueue (SQLite)              MeshDaemon (offline)
  enqueue("bob", msg)  ───────►    [held in queue]
                                   ...time passes...
                                   daemon.bring_online()
sync_deliver() ──────────────────► Inbox.receive(msg)
                                   queue.mark_delivered()
```

### Key components

| Class | Responsibility |
|-------|---------------|
| `MeshDaemon` | Placeholder for real transport (cjdns / libp2p); tracks online state |
| `MessageQueue` | SQLite-backed queue per node; survives restarts |
| `Inbox` | In-memory receive buffer for a live node |
| `sync_deliver()` | Transfers pending messages when the destination daemon is online |

### Code walkthrough

```python
# Create Alice's queue backed by a SQLite file
alice_queue = MessageQueue("alice", db_path)

# Create Bob's transport handle (starts offline)
bob_daemon = MeshDaemon("bob")
bob_inbox  = Inbox("bob")

# Alice queues two messages while Bob is offline
alice_queue.enqueue("bob", "Hello Bob, sync later!")
alice_queue.enqueue("bob", "Offline message 2")

# Attempt delivery — returns 0 because Bob is offline
sync_deliver(alice_queue, bob_daemon, bob_inbox)

# Bob comes online
bob_daemon.bring_online()

# Retry sync — now both messages are delivered
count = sync_deliver(alice_queue, bob_daemon, bob_inbox)
# count == 2
```

The SQLite schema for `MessageQueue`:

```sql
CREATE TABLE messages (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    sender    TEXT    NOT NULL,
    recipient TEXT    NOT NULL,
    payload   TEXT    NOT NULL,
    delivered INTEGER NOT NULL DEFAULT 0
);
```

### Run the example

```bash
python 01_layer1_messaging.py
```

**Expected output:**

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

---

## Section 3: Layer 2 — Governance & Trust

> **Goal:** Create decentralised identities, issue and verify credentials,
> run a proposal through the vote cycle, compute reputation, and distribute
> incentive rewards.

### Architecture

```
DIDService           GovernanceService         ReputationService
──────────           ─────────────────         ─────────────────
create_did()         create_proposal()         add_node()
issue_credential()   vote()                    add_endorsement()
verify_credential()  tally()          ──────►  compute_scores()
selective_          _anchor()                         │
  disclosure()       (hash chain)                     ▼
                                              IncentiveService
                                              ────────────────
                                              register()
                                              reward()
```

### Key components

| Class | Responsibility |
|-------|---------------|
| `DIDService` | Create DIDs, issue verifiable credentials, verify & selectively disclose |
| `GovernanceService` | Proposals, votes, tally, hash-chain anchor (Integrity Chain) |
| `ReputationService` | PageRank-style trust scoring over an endorsement graph |
| `IncentiveService` | Token balances and reward distribution |

### Code walkthrough

```python
did_svc = DIDService()
gov_svc = GovernanceService()
rep_svc = ReputationService()
inc_svc = IncentiveService()

# --- Identity ---
alice_did = did_svc.create_did("alice")   # "did:sov:alice"
bob_did   = did_svc.create_did("bob")     # "did:sov:bob"

# Alice issues Bob a role credential
cred_id = did_svc.issue_credential(
    issuer_did=alice_did,
    subject_did=bob_did,
    credential_type="MeshMember",
    claims={"node_id": "bob", "role": "relay", "cell": "cell-01"},
)
did_svc.verify_credential(cred_id)                       # valid=True
did_svc.selective_disclosure(cred_id, ["node_id","role"]) # no 'cell' leaked

# --- Governance ---
prop_id = gov_svc.create_proposal(alice_did, "Increase cell bandwidth quota")
gov_svc.vote(prop_id, alice_did, "APPROVE")
gov_svc.vote(prop_id, bob_did,   "APPROVE")
gov_svc.tally(prop_id)          # PASSED; anchors to hash chain

# --- Reputation ---
rep_svc.add_endorsement("alice", "bob", weight=1.0)
rep_svc.add_endorsement("bob",   "alice", weight=0.5)
scores = rep_svc.compute_scores()   # {"alice": 0.65, "bob": 0.35}

# --- Incentives ---
inc_svc.register("alice")
inc_svc.reward("alice", 10, "proposal creation")
```

### Run the example

```bash
python 02_layer2_governance.py
```

**Expected output (hash values vary):**

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
[chain] block 0: 0000000000000000 → 4a411792a5752a64
[reputation] scores: alice=0.5  bob=0.5
[incentive] rewarded alice +10 tokens (proposal creation)
[incentive] rewarded bob +5 tokens (governance participation)
[incentive] alice balance: 110
[incentive] bob balance: 105
```

> **Note on reputation scores:** With only two nodes and symmetric endorsement
> weights, PageRank converges to equal scores.  Add more nodes and asymmetric
> weights to see differentiation.

---

## Section 4: Layer 3 (Optional) — Brain Simulation

> **Goal:** Understand how GhostStack models agent cognition: stimuli drive
> emotions, emotions modulate decisions, and a dopamine signal captures
> reward prediction error.

Skip this section if you only need messaging + governance.

### Architecture

```
Stimulus
   │
   ▼
SensoryProcessor ──► {type, intensity, novelty}
                                   │
                                   ▼
                           LimbicSystem
                         valence · arousal · dopamine
                                   │
                                   ▼
                           FrontalLobe ──► action
                                   │
                                   ▼
                           Hippocampus  (episode store)
                                   │
                                   ▼
                     JSON state file  (persistent across runs)
```

### Dopamine model (reward-prediction error)

```
dopamine += 0.2 × (actual_reward − predicted_reward)
predicted_reward = 0.9 × predicted_reward + 0.1 × actual_reward
```

This is a simplified Rescorla-Wagner / temporal-difference model.  The
dopamine signal rises when reality exceeds expectations and falls when it
falls short.

### Run the example

```bash
python 03_layer3_brain.py
```

**Expected output (values vary):**

```
[brain] cycle 1   stimulus=visual   emotion=(valence=0.527, arousal=0.35)  action=conserve dopamine=0.523
[brain] cycle 2   stimulus=auditory emotion=(valence=0.536, arousal=0.365)  action=explore  dopamine=0.536
[brain] cycle 3   stimulus=visual   emotion=(valence=0.538, arousal=0.359)  action=explore  dopamine=0.544
[brain] cycle 4   stimulus=auditory emotion=(valence=0.558, arousal=0.393)  action=explore  dopamine=0.567
[brain] cycle 5   stimulus=visual   emotion=(valence=0.567, arousal=0.414)  action=conserve dopamine=0.584
[memory] stored 5 episodes
[persist] state saved to /tmp/ghoststack_brain_state.json
[plot]   saved emotion trajectory → /tmp/ghoststack_brain_plot.png
```

Run the script a second time to see the agent continuing from its saved state
(cycle numbers resume rather than resetting to 1).

---

## Section 5: Bridge Layer — GhostAgent

> **Goal:** Combine all three layers into a single `GhostAgent` entity.

### Architecture

```
GhostAgent
├── brain          : BrainSimulation  (Layer 3)
├── did            : DIDService entry (Layer 2)
├── gov_svc        : GovernanceService (Layer 2)
├── inc_svc        : IncentiveService  (Layer 2)
├── queue          : MessageQueue     (Layer 1)
└── daemon         : MeshDaemon       (Layer 1)

Methods:
  run_brain_cycle(stimulus, intensity, novelty) → action
  propose_action(action)  → prop_id
  send_message(recipient, text) → msg_id
  save_brain()
```

### Code walkthrough

```python
agent = GhostAgent(
    agent_id="agent001",
    did_svc=DIDService(),
    gov_svc=GovernanceService(),
    inc_svc=IncentiveService(),
    db_path=db_path,
)

# 1. Cognitive cycle
action = agent.run_brain_cycle("visual", intensity=0.8, novelty=0.9)
# e.g. action = "explore"

# 2. Translate action into a governance proposal
prop_id = agent.propose_action(action)
# creates "P-1: agent001 proposes: explore" and self-votes APPROVE

# 3. Queue a message (not delivered until another agent syncs)
agent.send_message("broadcast", f"I chose: {action}")
```

### Run the example

```bash
python 04_bridge_agent.py
```

**Expected output (action varies):**

```
[agent] agent001 initialised (DID=did:sov:agent001)
[brain] cycle 1   stimulus=visual   emotion=(valence=0.527, arousal=0.35)  action=wait     dopamine=0.523
[agent] brain cycle complete → action=wait
[governance] proposal P-1 created by agent001: "agent001 proposes: wait"
[vote] agent001  → APPROVE on P-1
[queue] agent001 queued msg → broadcast: "I chose: wait"
[agent] message queued (delivery requires a sync step — see 05_multi_agent_demo.py)
[persist] agent001 state saved to /tmp/ghoststack_brain_agent001.json

[summary] proposal=P-1  queued messages: 1
```

---

## Section 6: Multi-Agent Integration

> **Goal:** Run the full scenario with two agents, offline sync, and joint
> governance.

### Scenario walkthrough

```
Step 1: Create alice and bob (both offline initially)
Step 2: alice.come_online()
Step 3: alice.run_brain_cycle()  →  action
Step 4: alice.queue.enqueue("bob", msg)
Step 5: sync_deliver() with bob offline  →  0 delivered (message held)
Step 6: bob.come_online()
Step 7: sync_deliver() with bob online  →  1 delivered
Step 8: gov_svc.create_proposal(alice.did, ...)
Step 9: alice.vote("APPROVE")  +  bob.vote("APPROVE")
Step 10: gov_svc.tally()  →  PASSED, anchored to hash chain
Step 11: rep_svc.compute_scores()
Step 12: inc_svc.print_balances()
```

### Run the example

```bash
python 05_multi_agent_demo.py
```

**Expected output (action and hash vary):**

```
[agent] alice   initialised (DID=did:sov:alice)
[agent] bob     initialised (DID=did:sov:bob)
[daemon] alice   is now ONLINE
[brain] alice cycle 1  stimulus=visual   ...  action=wait
[agent] alice brain cycle complete → action=wait
[queue] alice   queued msg → bob: "Hey bob, I chose: wait"
[daemon] bob     is OFFLINE — 1 message(s) held in alice's queue

[daemon] bob     is now ONLINE
[sync] delivering msg id=1 from alice → bob
[inbox] bob     received: Hey bob, I chose: wait
[sync] 1 message(s) delivered to bob

[governance] proposal P-1 created by alice: "cell proposal: wait"
[vote] alice   → APPROVE on P-1
[vote] bob     → APPROVE on P-1
[tally] P-1: approve=2 reject=0 → PASSED
[chain] block 0: 0000000000000000 → d48a3176a5e40d3c

[reputation] scores: alice=0.5  bob=0.5
[incentive] alice balance: 115
[incentive] bob balance: 105
```

### How multi-agent reputation diverges

With only two nodes and symmetric activity, scores are equal.  In a larger
cell (3-7 nodes) with asymmetric endorsement patterns the PageRank algorithm
naturally differentiates contributors.  Try adding a third agent and
asymmetric votes to observe this:

```python
rep_svc.add_node("carol")
rep_svc.add_endorsement("alice", "carol", weight=2.0)
rep_svc.add_endorsement("bob",   "carol", weight=1.0)
scores = rep_svc.compute_scores()
# carol will have a higher score than alice or bob
```

---

## Section 7: Hardening Roadmap

The examples in this tutorial are **prototype-quality**.  Moving toward
production requires the following work, roughly in priority order.

### 1. Replace MeshDaemon with real transport

| Option | Use case |
|--------|----------|
| [cjdns](https://github.com/cjdelisle/cjdns) | IPv6 mesh, end-to-end encrypted |
| [BATMAN-adv](https://www.open-mesh.org/projects/batman-adv/wiki) | Layer-2 mesh, good for local area |
| [libp2p](https://libp2p.io/) | Modular P2P transport, works over internet |

Replace `MeshDaemon.is_online()` with a real peer-discovery query and
`sync_deliver()` with a push/pull protocol over the chosen transport.

### 2. Add signed envelopes, ack tracking, replay protection

Each message in `MessageQueue` should be wrapped in a signed envelope:

```json
{
  "id": "<uuid>",
  "sender_did": "did:sov:alice",
  "recipient_did": "did:sov:bob",
  "payload_hash": "<sha256>",
  "payload": "...",
  "signature": "<ed25519>",
  "nonce": "<random>",
  "timestamp": 1700000000
}
```

Add a `nonce` table to detect replays.  Add ACK messages flowing back through
`sync_deliver`.

### 3. Harden identity (ed25519, credential schemas)

Replace the prototype `DIDService` with:
- ed25519 key pairs stored in a secure keystore
- W3C DID Document generation and resolution
- JSON-LD credential schemas aligned with W3C VC Data Model

### 4. Add governance lifecycle (quorum, expiration)

Extend `GovernanceService`:
- Quorum threshold (minimum votes before tally)
- Proposal expiration (auto-reject after N seconds)
- Multi-stage proposals (draft → review → vote)
- Fork manifests for irreconcilable proposals

### 5. Add reputation hardening (sybil resistance, decay)

Extend `ReputationService`:
- Time-decay so stale endorsements fade
- Sybil-resistance: cap the total weight a single node can inject
- Cross-cell reputation bridges with discount factors

---

## Bridging back to the philosophy

| Tutorial concept | Sovereign Stack principle |
|-----------------|--------------------------|
| Fork-able cell structure | **Sovereignty via Forkability** (CORE.md §2) |
| Hash-chain anchoring | **Truth by Receipts** (CORE.md §3) |
| Offline-first messaging | **Flow Over Containment** (CORE.md §1) |
| Exit rights (fork governance) | No thrones, no heirs |
| Decentralised identity | Power requires proof, not proclamation |

For philosophical context see [CORE.md](../CORE.md).
For system architecture see [docs/01_Core_Architecture/README.md](01_Core_Architecture/README.md).
For protocol specifications see [protocols/README.md](../protocols/README.md).

---

## Next steps

- **Run the quick-start** → [QUICKSTART.md](QUICKSTART.md)
- **Decide how much you need** → [STOPPING_POINTS.md](STOPPING_POINTS.md)
- **Read implementation notes** → [IMPLEMENTATION_NOTES.md](../IMPLEMENTATION_NOTES.md)
- **Browse the examples** → [src/ghoststack/examples/README.md](../src/ghoststack/examples/README.md)

---

*"Flow over containment. Replication over scaling. Sovereignty as verb, not noun."*

**Maintained by:** O1 Labs CIC | **License:** AGPL-3.0
