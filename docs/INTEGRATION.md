# Integration Map — Sovereign OS

This document maps the 5-layer Sovereign OS architecture to the concrete source modules in this monorepo, explains how `deed-ledger` **is** the GhostStack Integrity Chain, shows the Ghost → deed bridge design, and lists the next concrete wiring tasks.

All design decisions here are bound by [CORE.md](../CORE.md) axioms:
- **Flow over Containment** — data and trust circulate; nothing pools or gates
- **Sovereignty via Forkability** — every layer can be forked; exit is unconditional
- **Truth by Receipts** — meaningful actions produce signed, append-only evidence
- **NO blockchain** — cryptographic proofs without tokenisation or mining
- **Mortality** — processes are ephemeral; scars are healable; state doesn't accumulate

---

## 5-Layer Architecture Map

The architecture has **5 conceptual layers**. The source tree maps several modules onto the same layer (e.g. Ghost + thermo-ai + precisionlocked all live in Layer 4 — GhostBrain).

```
┌─────────────────────────────────────────────────────────────────────┐
│  Layer 5 — Physical                                                 │
│  hardware/  (SOV-HAB, MLDT, HabCal, energy, water)                  │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 4 — GhostBrain (AI Advisor)                                  │
│  src/ai/ghost/              Ghost bash daemon + deed bridge          │
│  src/ai/thermo-ai/          Thermodynamic AI organism                │
│  src/psych/precisionlocked/ Cognitive integrity + pattern analysis   │
│  src/tools/red-flag-auditor/ Governance audit tooling               │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 3 — GhostStack (Civic OS / Integrity Chain)                  │
│  src/governance/deed-ledger/  ← THIS IS GHOSTSTACK                  │
│  Proposals · Voting · Deeds · Scars · Demurrage                     │
│  Portable exit · Nostr broadcast                                    │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 2 — Mesh                                                     │
│  src/mesh/shadow-net/   P2P routing, no ISP needed                  │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 1 — Energy                                                   │
│  src/energy-coupler/    Bidirectional flow control                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## deed-ledger = GhostStack (Truth-by-Receipts)

`src/governance/deed-ledger` is the live implementation of the Integrity Chain described in CORE.md §3 "Truth by Receipts". It is the governance and reputation backbone of the entire stack.

### How it implements the CORE axioms

| CORE axiom | deed-ledger mechanism |
|-----------|----------------------|
| **Truth by Receipts** | Every action (vote, energy transfer, task completion) becomes a `Deed` record on Ceramic (append-only, cryptographically verifiable) and is broadcast as a Nostr event |
| **Scars healable** | Disputes produce a `Scar` linked to the original Deed. A `RecoveryDeed` can be submitted and peer-reviewed — the scar is visible but the arc of recovery is also visible |
| **Demurrage** | Influence decays without ongoing contribution. Dormant reputation fades — legacy capture is structurally prevented |
| **Portable exit** | Reputation is DID-anchored and relay-broadcast via Nostr — it leaves with the person, not with the platform |
| **Flow over Containment** | Deeds circulate across Nostr relays; no single node holds canonical state |
| **Forkability** | ComposeDB models and Nostr event kinds are defined in open GraphQL schemas — fork and diverge at will |
| **NO blockchain** | Ceramic + ComposeDB uses IPFS-backed streams with DID signatures. No tokens, no mining, no consensus delay |

### Key data types (`packages/schemas/src/models/reputation.graphql`)

```graphql
type Deed           # A completed action — the atomic unit of reputation
type Scar           # Dispute mark linked to a Deed (visible, not deleted)
type RecoveryDeed   # Rehabilitation arc — dispute resolution on-chain
type UserReputation # Running score with demurrage decay
```

### Nostr event format (kind 30023 — long-form deed announcement)

```json
{
  "kind": 30023,
  "created_at": 1700000000,
  "tags": [
    ["d", "<deed-id>"],
    ["t", "<deed-type>"],
    ["layer", "ghoststack"],
    ["stage", "<ghost-stage>"],
    ["mask", "<ghost-mask>"]
  ],
  "content": "<deed description>",
  "pubkey": "<node-did-pubkey>",
  "id": "<sha256-of-canonical-event>",
  "sig": "<schnorr-signature>"
}
```

The `layer`, `stage`, and `mask` tags are added by the Ghost → deed bridge to link AI advisor state to the governance record.

---

## Ghost → deed-ledger Bridge

Ghost (`src/ai/ghost/`) is an ephemeral RAM-resident AI daemon. By design it has no persistent storage — its diary vanishes on exit. The bridge posts a deed **before** Ghost forgets a cycle, creating an externalised receipt on the Integrity Chain.

### Bridge script: `src/ai/ghost/ghostdeed.sh`

The bridge is a sourced bash module. When Ghost completes an `adapt` cycle it calls `ghost_deed_post`, which:

1. Reads current Ghost state (`GHOST_STAGE`, `GHOST_MASK`, `GHOST_CYCLES`, metrics)
2. Constructs a Nostr-compatible event JSON
3. Attempts to publish via `websocat` to configured relays (falls back to a local append-only deed journal at `GHOST_DEED_JOURNAL`)

This honours **ephemerality** (Ghost's RAM diary still vanishes; the deed journal is the externalised receipt) and **mortality** (the deed is a scar/receipt of a cycle that already died).

### Example deed event emitted by Ghost

```json
{
  "kind": 30023,
  "created_at": 1740000000,
  "tags": [
    ["d", "ghost-adapt-42-1740000000"],
    ["t", "ghost_adapt"],
    ["layer", "ghostbrain"],
    ["stage", "aware"],
    ["mask", "Healer"],
    ["consistency", "72"],
    ["adaptability", "50"],
    ["proactivity", "80"],
    ["curiosity", "25"]
  ],
  "content": "Ghost adaptation cycle 42: stage=aware mask=Healer consistency=72 adaptability=50 proactivity=80 curiosity=25",
  "pubkey": "",
  "id": "",
  "sig": ""
}
```

The unsigned `pubkey`/`id`/`sig` fields are stubs until a Nostr keypair is configured (`GHOST_NOSTR_NSEC`). Without a keypair the deed is written to the local journal only.

### Wiring in `ghostbrain.sh`

`ghostdeed.sh` is sourced by `ghostbrain.sh` alongside the other modules. `ghost_deed_post` is called at the end of each `adapt` cycle:

```bash
# Every 15 cycles: adapt (also updates mask + stage)
if (( GHOST_CYCLES % GHOST_ADAPT_EVERY == 0 )); then
  declare -f ghost_adapt     &>/dev/null && ghost_adapt     >/dev/null 2>&1 || true
  declare -f ghost_deed_post &>/dev/null && ghost_deed_post >/dev/null 2>&1 || true
fi
```

---

## 4. Shadow-Net LoRa Bridge

`src/mesh/shadow-net/bridge/` is the **Layer 2 LoRa mesh transport** for the
Sovereign Stack.  It bridges Meshtastic hardware to the deed-ledger Integrity
Chain so off-grid nodes can participate in governance without any internet
connection.

### How it connects to the three previous tasks

| Previous task | Connection |
|--------------|------------|
| **✅ Task 1 — Nostr signing** (`ghostdeed.sh`) | `DeedMeshBridge._sign_payload()` uses the same key path (`private_key_path` in `config.yaml`).  Signed deeds from the mesh are broadcast to the same Nostr relay. |
| **✅ Task 2 — deed-ledger ingest endpoint** | Every received mesh packet is converted to a `Deed` and POSTed to `deed_ingest_url` (`POST /ghost-deed` or `/api/deeds/ingest`). |
| **✅ Task 3 — EventLog Ghost deeds** | Receipts emitted by `_broadcast_receipt()` carry `kind: 30023` tags compatible with the `EventLog.tsx` filter — they appear alongside Ghost adapt receipts in the governance dashboard. |

### Data flow

```
Mesh node → DeedMeshBridge.on_mesh_receive()
              ↓ verify sig
              ↓ _packet_to_deed()     ← same Deed schema as deed-ledger
              ↓ _post_deed()          ← Task 2 ingest endpoint
              ↓ _broadcast_receipt()  ← Nostr kind 30023 (Task 1 signing)
              ↓ EventLog display      ← Task 3 subscription filter
```

### GhostAgent hook

```python
# In src/ghost/dual/ghost_dual_daemon.py (slow_loop):
from shadow_net.bridge import DeedMeshBridge
bridge.send_proposal(ghost_proposal)  # proposal → mesh + ledger
```

### Files

- `bridge/DeedMeshBridge.py` — core bridge class
- `bridge/cli.py` — `start` / `send` / `status` commands
- `bridge/demo.py` — smoke-test with mock hardware
- `bridge/config.yaml` — port, URLs, cell ID, key path
- `tests/test_bridge.py` — pytest suite (17 tests, all mocked)

---

## Next Wiring Tasks (one evening each) — ALL COMPLETE ✅

These three wiring tasks are now complete and linked via the Shadow-Net bridge.

### ✅ Task 1 — Nostr signing in `ghostdeed.sh` (~1 h)

`ghostdeed.sh` currently emits unsigned events. Wire in a signing step:

```bash
# In ghostdeed.sh ghost_deed_sign():
# 1. Set GHOST_NOSTR_NSEC in environment (bech32 private key)
# 2. Use `nak` (https://github.com/fiatjaf/nak) to sign:
#    go install github.com/fiatjaf/nak@v0.10.0
#    echo "$json" | nak event --sec "$GHOST_NOSTR_NSEC"
# 3. Replace the unsigned JSON with the signed output before publishing
```

`nak` v0.10.0 is a single-binary CLI for Nostr. Pin to a specific release rather than `@latest` to keep the Nostr event format stable.

### ✅ Task 2 — deed-ledger ingest endpoint (~2 h)

Add a small HTTP handler to `src/governance/deed-ledger/packages/backend/src/index.ts` that:

1. Accepts `POST /ghost-deed` with the unsigned deed JSON body
2. Signs it with the backend's Nostr key using `nostr-tools`
3. Publishes it to the configured Nostr relays via the existing `NostrClient.publishEvent()`
4. Optionally writes it to Ceramic as a `Deed` record via ComposeDB

This lets Ghost (or any layer) POST deeds to the backend without needing a Nostr keypair locally.

### ✅ Task 3 — deed-ledger EventLog shows Ghost deeds (~1 h)

In `src/governance/deed-ledger/packages/frontend/app/components/EventLog.tsx`, extend the Nostr subscription filter to include `kind: 30023` events with tag `["layer", "ghostbrain"]`:

```typescript
// In EventLog.tsx NostrClient subscribeToEvents():
const filters = [
  { kinds: [30023], '#t': ['ghost_adapt', 'ghost_reflect'] },
];
```

Ghost's adapt receipts will then appear in the governance dashboard alongside human deeds — AI actions made legible and accountable under the same Truth-by-Receipts logic that governs human actions.

---

## Audit Tools

`src/tools/red-flag-auditor/` provides governance auditing that operates directly on the Integrity Chain. It flags:

- Dormant nodes that haven't posted a deed recently (demurrage trigger)
- Cells approaching the 7-node limit (fork trigger)
- Deed disputes with no recovery arc (unresolved scars)

---

*"Receipts replace bureaucracy. Ghost dreams. The ledger remembers."*
