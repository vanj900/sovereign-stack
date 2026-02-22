# Implementation Notes

Technical notes on the GhostStack prototype implementation, covering design
decisions, known limitations, and the gap between the prototype and a
production system.

---

## Overview

The prototype in `src/ghoststack/examples/` implements three layers of the
GhostStack middleware:

| Layer | Files | Status |
|-------|-------|--------|
| 1 — Offline-First Messaging | `01_layer1_messaging.py` | Prototype |
| 2 — Governance & Trust | `02_layer2_governance.py` | Prototype |
| 3 — Brain Simulation | `03_layer3_brain.py` | Prototype |
| Bridge (GhostAgent) | `04_bridge_agent.py` | Prototype |
| Multi-Agent Integration | `05_multi_agent_demo.py` | Prototype |

**Prototype** means: functionally correct for learning and local testing, but
not hardened for production deployment (see gap analysis below).

---

## Layer 1: Offline-First Messaging

### Design decisions

**SQLite as the queue backing store**

SQLite was chosen because it is:
- Bundled with Python (zero extra dependencies)
- ACID-compliant (no partial writes)
- File-based (survives process restarts)
- Trivially replaceable with a more robust store later

The queue schema is deliberately minimal:

```sql
CREATE TABLE messages (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    sender    TEXT    NOT NULL,
    recipient TEXT    NOT NULL,
    payload   TEXT    NOT NULL,
    delivered INTEGER NOT NULL DEFAULT 0
);
```

**MeshDaemon as a thin interface boundary**

`MeshDaemon` intentionally exposes only `is_online() → bool` and
`bring_online()`.  This makes it trivial to swap in a real transport:

```python
class CjdnsDaemon(MeshDaemon):
    def is_online(self) -> bool:
        return self._cjdns_peer_reachable(self.node_id)
```

### Known limitations (prototype)

| Limitation | Production fix |
|-----------|---------------|
| Payloads are plain text | Wrap in signed envelopes (see below) |
| No ACK / retry logic | Add a `delivered_at` timestamp + retry queue |
| No replay protection | Add a `nonce` column and deduplication table |
| Single SQLite file shared by all senders | One DB file per node pair, or use a WAL-mode shared DB |
| No end-to-end encryption | Encrypt payload with recipient's public key |

### Signed envelope format (target)

```json
{
  "id": "<uuid>",
  "sender_did": "did:sov:alice",
  "recipient_did": "did:sov:bob",
  "payload": "<base64-encrypted>",
  "payload_hash": "<sha256-of-plaintext>",
  "nonce": "<32-byte-random-hex>",
  "timestamp": 1700000000,
  "signature": "<ed25519-over-all-fields>"
}
```

---

## Layer 2: Governance & Trust

### Design decisions

**DIDService: prototype signatures**

The prototype uses `sha256(json(claims))[:16]` as a stand-in for a real
cryptographic signature.  This is sufficient to detect accidental corruption
but provides no security against forgery.

Production replacement: `ed25519` signatures via `cryptography` or `PyNaCl`.

**GovernanceService: hash-chain anchor**

Each proposal decision is anchored by appending a block to an in-memory list:

```python
block_hash = sha256(prev_hash + json({"prop_id": ..., "result": ...}))
```

This demonstrates the Integrity Chain concept (Truth by Receipts) without
requiring a full distributed ledger.  The in-memory chain is reset on restart.

Production replacement: write blocks to an append-only SQLite table (or a real
distributed ledger) so the chain persists and is independently auditable.

**ReputationService: PageRank variant**

The iterative algorithm converges in ~20 steps for small graphs (3-7 nodes).
For larger networks consider:
- Sparse matrix representation
- Incremental updates (rather than full recompute on each endorsement)
- Time-decay: `weight *= exp(-λ * age_in_days)` so stale endorsements fade

**IncentiveService: in-memory ledger**

Balances are held in a Python dict.  In production every reward should be a
signed receipt appended to the Integrity Chain.

### Known limitations (prototype)

| Limitation | Production fix |
|-----------|---------------|
| DIDs are just strings | Generate real W3C DID Documents with ed25519 keys |
| No credential revocation | Add a revocation registry (CRL or status list) |
| Governance has no quorum | Add minimum-votes threshold before `tally()` |
| Proposals never expire | Add `expires_at` field and auto-reject on timeout |
| Reputation resets on restart | Persist the endorsement graph to SQLite |
| Incentive balances are ephemeral | Persist to SQLite and anchor to hash chain |

---

## Layer 3: Brain Simulation

### Design decisions

**Decoupled emotional and decision layers**

`LimbicSystem` and `FrontalLobe` are intentionally separate classes.  This
allows swapping the decision policy (e.g., replacing softmax sampling with a
trained policy network) without touching the emotional state model.

**Dopamine as reward-prediction error**

The simplified Rescorla-Wagner model:

```
dopamine_t = dopamine_{t-1} + α × (reward_t − predicted_t)
predicted_t = γ × predicted_{t-1} + (1-γ) × reward_t
```

Parameters used in the prototype: `α = 0.2`, `γ = 0.9`.

**JSON persistence**

Brain state is saved to `/tmp/ghoststack_brain_<agent_id>.json` after each run.
This enables multi-run learning: emotional state and the predicted-reward
baseline carry over between sessions.

### Known limitations (prototype)

| Limitation | Production fix |
|-----------|---------------|
| `FrontalLobe` uses hardcoded heuristic weights | Train with RL (e.g., PPO) |
| `Hippocampus` is a plain list (no retrieval index) | Add embedding-based retrieval |
| Only 4 actions | Expand action space based on domain requirements |
| Stimuli are manually specified | Wire to real sensor inputs |
| State saved to `/tmp` | Use a configurable, persistent path |

---

## Bridge: GhostAgent

### Design decision: composition over inheritance

`GhostAgent` holds references to service instances rather than subclassing
them.  This keeps each layer independently testable and avoids tight coupling.

### Per-agent state isolation

Each agent writes its brain state to a unique path:

```
/tmp/ghoststack_brain_<agent_id>.json
```

This prevents state collisions when multiple agents run in the same process
(as in `05_multi_agent_demo.py`).

---

## Dependency summary

All prototype code uses only the Python standard library:

| Module | Used for |
|--------|---------|
| `sqlite3` | Message queue persistence |
| `hashlib` | Credential signatures, hash-chain blocks |
| `json` | State serialisation, chain payloads |
| `math` | Softmax computation in FrontalLobe |
| `os` | State file existence checks |
| `random` | Action sampling |
| `tempfile` | Temporary DB files in demos |
| `time` | Timestamps |
| `uuid` | Credential IDs |

Optional:

| Package | Used for |
|---------|---------|
| `matplotlib` | Brain simulation plots |

---

## Testing approach

The prototype is validated by running each example end-to-end and verifying
console output.  Key assertions checked manually:

- Layer 1: `delivered` flag flips from `False` to `True` after sync
- Layer 1: zero messages delivered when daemon is offline
- Layer 2: `verify_credential` returns `True` for freshly issued credential
- Layer 2: `tally` returns `PASSED` when approvals > rejections
- Layer 2: hash-chain blocks have correctly linked `prev_hash` values
- Layer 3: state file created after `save_state()`; loaded correctly on restart
- Layer 3: cycle number resumes (not reset) on second run
- Layer 4: `propose_action` self-vote appears in `gov_svc._votes`
- Layer 5: inbox contains correct payload after sync

To add automated tests, use Python's built-in `unittest` or `pytest` and
import the classes directly from the example scripts.

---

## Security considerations

**This prototype is not secure.**  It is intended for learning and local
demonstration only.  Known security gaps:

1. **No real signatures** — credential signatures are truncated SHA-256 hashes,
   not ed25519 signatures.  They cannot prevent forgery.

2. **No transport encryption** — message payloads are stored and transmitted as
   plain text.

3. **No authentication** — any caller can invoke `GovernanceService.vote()` with
   any DID.

4. **No replay protection** — the same message can be delivered multiple times
   if the `delivered` flag is somehow reset.

5. **Temp files** — brain state and (in some examples) SQLite DBs are written to
   `/tmp`.  These are world-readable on shared systems.

Address all five issues before any network deployment.  See the hardening
roadmap in [docs/TUTORIAL.md](docs/TUTORIAL.md#section-7-hardening-roadmap).

---

*For the full tutorial see [docs/TUTORIAL.md](docs/TUTORIAL.md).*
*For quick start instructions see [docs/QUICKSTART.md](docs/QUICKSTART.md).*
