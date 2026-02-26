"""
Three-Node Cell Simulation
===========================
Extends the two-agent demo to a full 3-node Cell (alice, bob, carol), demonstrating:

  - Offline → online sync across three independent queues
  - Joint governance with majority voting (≥2 of 3 APPROVE)
  - Asymmetric reputation divergence: carol receives more endorsements →
    higher PageRank score
  - Incentive balances after proposal creation and governance participation

Deed-ledger analogue (in-memory):
  - A lightweight ``DeedLedger`` records every governance decision as a
    "deed receipt" with a hash-chain anchor — the same concept as the
    deed-ledger Ceramic model but without a network dependency.
  - "Scars" are appended when a proposal is REJECTED or disputed.
  - Receipts are printed at the end so the scar/receipt lifecycle is
    visible end-to-end.

This script is self-contained — no imports from other example files needed.

Run:
    python 06_three_node_cell.py

Expected output (action and hash values vary):
    === Three-Node Cell ===
    [agent] alice   initialised (DID=did:sov:alice)
    [agent] bob     initialised (DID=did:sov:bob)
    [agent] carol   initialised (DID=did:sov:carol)
    ...
    [deed-ledger] receipt P-1: PASSED  hash=<hex>
    [deed-ledger] receipt P-2: PASSED  hash=<hex>
    [deed-ledger] scar      P-3: FAILED (minority-reject) hash=<hex>
    [reputation] scores: alice=0.2...  bob=0.2...  carol=0.5...
    [incentive] alice  balance: ...
    [incentive] bob    balance: ...
    [incentive] carol  balance: ...
"""

import hashlib
import json
import math
import os
import random
import sqlite3
import tempfile
import time
import uuid


# ===========================================================================
# Layer 1 — offline-first messaging
# ===========================================================================

class MeshDaemon:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self._online = False

    def bring_online(self) -> None:
        self._online = True
        print(f"[daemon] {self.node_id:<7} is now ONLINE")

    def is_online(self) -> bool:
        return self._online


class MessageQueue:
    def __init__(self, node_id: str, db_path: str):
        self.node_id = node_id
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                sender    TEXT NOT NULL,
                recipient TEXT NOT NULL,
                payload   TEXT NOT NULL,
                delivered INTEGER NOT NULL DEFAULT 0
            )"""
        )
        self._conn.commit()

    def enqueue(self, recipient: str, payload: str) -> int:
        cur = self._conn.execute(
            "INSERT INTO messages (sender, recipient, payload) VALUES (?, ?, ?)",
            (self.node_id, recipient, payload),
        )
        self._conn.commit()
        print(f"[queue] {self.node_id:<7} queued msg → {recipient}: \"{payload}\"")
        return cur.lastrowid

    def pending(self, recipient: str) -> list:
        cur = self._conn.execute(
            "SELECT id, sender, recipient, payload FROM messages "
            "WHERE recipient = ? AND delivered = 0",
            (recipient,),
        )
        return cur.fetchall()

    def mark_delivered(self, msg_id: int) -> None:
        self._conn.execute(
            "UPDATE messages SET delivered = 1 WHERE id = ?", (msg_id,)
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


class Inbox:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.messages: list = []

    def receive(self, msg_id: int, sender: str, payload: str) -> None:
        self.messages.append((msg_id, sender, payload))
        print(f"[inbox] {self.node_id:<7} received: {payload}")


def sync_deliver(queue: MessageQueue, daemon: MeshDaemon, inbox: Inbox) -> int:
    pending = queue.pending(daemon.node_id)
    if not daemon.is_online():
        count = len(pending)
        print(
            f"[daemon] {daemon.node_id:<7} is OFFLINE — "
            f"{count} message(s) held in {queue.node_id}'s queue"
        )
        return 0
    delivered = 0
    for msg_id, sender, recipient, payload in pending:
        print(f"[sync] delivering msg id={msg_id} from {sender} → {recipient}")
        inbox.receive(msg_id, sender, payload)
        queue.mark_delivered(msg_id)
        delivered += 1
    return delivered


# ===========================================================================
# Layer 2 — governance & trust
# ===========================================================================

class DIDService:
    def __init__(self):
        self._credentials: dict = {}

    def create_did(self, owner: str) -> str:
        return f"did:sov:{owner}"

    def issue_credential(
        self, issuer_did: str, subject_did: str, credential_type: str, claims: dict
    ) -> str:
        cred_id = str(uuid.uuid4())[:8]
        sig = hashlib.sha256(
            json.dumps(claims, sort_keys=True).encode()
        ).hexdigest()[:16]
        self._credentials[cred_id] = {
            "id": cred_id, "type": credential_type,
            "issuer": issuer_did, "subject": subject_did,
            "claims": claims, "signature": sig,
        }
        return cred_id


class GovernanceService:
    def __init__(self):
        self._proposals: dict = {}
        self._votes: dict = {}
        self._chain: list = []

    def create_proposal(self, proposer_did: str, description: str) -> str:
        prop_id = f"P-{len(self._proposals) + 1}"
        self._proposals[prop_id] = {
            "id": prop_id, "proposer": proposer_did,
            "description": description, "status": "open",
        }
        self._votes[prop_id] = {}
        owner = proposer_did.split(":")[-1]
        print(f"[governance] proposal {prop_id} created by {owner}: \"{description}\"")
        return prop_id

    def vote(self, prop_id: str, voter_did: str, choice: str) -> None:
        self._votes[prop_id][voter_did] = choice
        owner = voter_did.split(":")[-1]
        print(f"[vote] {owner:<7} → {choice} on {prop_id}")

    def tally(self, prop_id: str) -> str:
        votes = self._votes.get(prop_id, {})
        approve = sum(1 for v in votes.values() if v == "APPROVE")
        reject = sum(1 for v in votes.values() if v == "REJECT")
        result = "PASSED" if approve > reject else "FAILED"
        self._proposals[prop_id]["status"] = result
        print(f"[tally] {prop_id}: approve={approve} reject={reject} → {result}")
        prev = self._chain[-1]["hash"] if self._chain else "0" * 16
        payload = json.dumps(
            {"prop_id": prop_id, "result": result, "ts": int(time.time())},
            sort_keys=True,
        )
        block_hash = hashlib.sha256((prev + payload).encode()).hexdigest()[:16]
        self._chain.append({
            "index": len(self._chain), "prev_hash": prev,
            "payload": payload, "hash": block_hash,
        })
        print(f"[chain] block {len(self._chain) - 1}: {prev} → {block_hash}")
        return result


class ReputationService:
    def __init__(self, damping: float = 0.85, iterations: int = 20):
        self._damping = damping
        self._iterations = iterations
        self._nodes: set = set()
        self._edges: list = []

    def add_node(self, node_id: str) -> None:
        self._nodes.add(node_id)

    def add_endorsement(self, source: str, target: str, weight: float = 1.0) -> None:
        self._nodes.update([source, target])
        self._edges.append((source, target, weight))

    def compute_scores(self) -> dict:
        nodes = list(self._nodes)
        n = len(nodes)
        if n == 0:
            return {}
        out_weight: dict = {nd: 0.0 for nd in nodes}
        in_edges: dict = {nd: [] for nd in nodes}
        for src, tgt, w in self._edges:
            if src in out_weight:
                out_weight[src] += w
            if tgt in in_edges:
                in_edges[tgt].append((src, w))
        scores = {nd: 1.0 / n for nd in nodes}
        for _ in range(self._iterations):
            new_scores: dict = {}
            for nd in nodes:
                rank_sum = sum(
                    scores[src] * w / out_weight[src]
                    for src, w in in_edges[nd]
                    if out_weight[src] > 0
                )
                new_scores[nd] = (1 - self._damping) / n + self._damping * rank_sum
            scores = new_scores
        total = sum(scores.values()) or 1.0
        scores = {nd: round(v / total, 4) for nd, v in scores.items()}
        score_str = "  ".join(f"{nd}={v}" for nd, v in sorted(scores.items()))
        print(f"[reputation] scores: {score_str}")
        return scores


class IncentiveService:
    def __init__(self):
        self._balances: dict = {}

    def register(self, node_id: str, initial_balance: int = 100) -> None:
        self._balances[node_id] = initial_balance

    def reward(self, node_id: str, amount: int, reason: str = "") -> None:
        self._balances[node_id] = self._balances.get(node_id, 0) + amount

    def print_balances(self) -> None:
        for node_id, balance in sorted(self._balances.items()):
            print(f"[incentive] {node_id:<7} balance: {balance}")


# ===========================================================================
# Layer 3 — brain simulation (minimal inline)
# ===========================================================================

class LimbicSystem:
    DECAY = 0.1

    def __init__(self):
        self.valence: float = 0.5
        self.arousal: float = 0.3
        self.dopamine: float = 0.5

    def update(self, intensity: float, novelty: float) -> None:
        self.valence = round(max(0.0, min(1.0,
            self.valence * (1 - self.DECAY) + (0.5 + 0.3 * novelty) * self.DECAY
        )), 3)
        self.arousal = round(max(0.0, min(1.0,
            self.arousal * (1 - self.DECAY) + intensity * self.DECAY
        )), 3)

    def compute_dopamine(self, reward: float, predicted: float) -> float:
        self.dopamine = round(
            max(0.0, min(1.0, self.dopamine + 0.2 * (reward - predicted))), 3
        )
        return self.dopamine

    def state_dict(self) -> dict:
        return {"valence": self.valence, "arousal": self.arousal, "dopamine": self.dopamine}


class FrontalLobe:
    ACTIONS = ["explore", "wait", "signal", "conserve"]

    def decide(self, state: dict) -> str:
        v, a, d = state["valence"], state["arousal"], state["dopamine"]
        scores = {
            "explore": v * d + a,
            "wait": (1 - a) * 0.8,
            "signal": a * d,
            "conserve": (1 - v) * (1 - d),
        }
        exp_s = {k: math.exp(s * 3) for k, s in scores.items()}
        total = sum(exp_s.values())
        probs = {k: val / total for k, val in exp_s.items()}
        r, cumulative, chosen = random.random(), 0.0, self.ACTIONS[-1]
        for action, prob in probs.items():
            cumulative += prob
            if r <= cumulative:
                chosen = action
                break
        return chosen


class BrainSimulation:
    def __init__(self, agent_id: str = "agent"):
        self.agent_id = agent_id
        self.limbic = LimbicSystem()
        self.frontal = FrontalLobe()
        self._cycle = 0
        self._predicted_reward = 0.5
        self.state_path = f"/tmp/ghoststack_brain_{agent_id}.json"

    def step(self, stimulus_type: str, intensity: float, novelty: float) -> dict:
        self._cycle += 1
        self.limbic.update(intensity, novelty)
        reward = self.limbic.valence + 0.1 * novelty
        dopamine = self.limbic.compute_dopamine(reward, self._predicted_reward)
        self._predicted_reward = 0.9 * self._predicted_reward + 0.1 * reward
        action = self.frontal.decide(self.limbic.state_dict())
        e = self.limbic.state_dict()
        print(
            f"[brain] {self.agent_id} cycle {self._cycle:<2} "
            f"stimulus={stimulus_type:<8} "
            f"emotion=(valence={e['valence']}, arousal={e['arousal']})  "
            f"action={action:<8} dopamine={dopamine}"
        )
        return {"cycle": self._cycle, "stimulus": stimulus_type,
                "emotion": e, "action": action, "dopamine": dopamine}

    def save_state(self) -> None:
        state = {
            "cycle": self._cycle,
            "limbic": self.limbic.state_dict(),
            "predicted_reward": self._predicted_reward,
        }
        with open(self.state_path, "w") as f:
            json.dump(state, f)

    def load_state(self) -> bool:
        if not os.path.exists(self.state_path):
            return False
        with open(self.state_path) as f:
            state = json.load(f)
        self._cycle = state.get("cycle", 0)
        lim = state.get("limbic", {})
        self.limbic.valence = lim.get("valence", 0.5)
        self.limbic.arousal = lim.get("arousal", 0.3)
        self.limbic.dopamine = lim.get("dopamine", 0.5)
        self._predicted_reward = state.get("predicted_reward", 0.5)
        return True


# ===========================================================================
# Deed Ledger — in-memory scar/receipt ledger (analogue of Ceramic model)
# ===========================================================================

class DeedLedger:
    """
    Lightweight in-memory analogue of the deed-ledger Ceramic model.

    Records every governance decision as a *receipt* with a hash-chain anchor.
    When a proposal FAILS or is explicitly disputed, a *scar* is appended
    instead — marking the record visibly without deleting it.

    Scar/receipt lifecycle:
      1. tally() PASSED  →  receipt added to chain
      2. tally() FAILED  →  scar added to chain (not a receipt)
      3. submit_recovery() →  recovery record linked to the scar
      4. approve_recovery() → recovery status updated to 'approved'
    """

    def __init__(self):
        self._chain: list = []       # append-only hash-chain (receipts + scars)
        self._recoveries: dict = {}  # scar_id → recovery record

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _append(self, record_type: str, prop_id: str, result: str, note: str = "") -> str:
        """Append a record to the chain; return its hash."""
        prev_hash = self._chain[-1]["hash"] if self._chain else "0" * 16
        payload = json.dumps(
            {"type": record_type, "prop_id": prop_id, "result": result,
             "note": note, "ts": int(time.time())},
            sort_keys=True,
        )
        block_hash = hashlib.sha256((prev_hash + payload).encode()).hexdigest()[:16]
        entry = {
            "index": len(self._chain),
            "type": record_type,   # "receipt" | "scar"
            "prop_id": prop_id,
            "result": result,
            "note": note,
            "prev_hash": prev_hash,
            "hash": block_hash,
        }
        self._chain.append(entry)
        return block_hash

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record(self, prop_id: str, result: str) -> str:
        """
        Record a governance outcome.

        PASSED proposals generate a *receipt*; FAILED proposals generate a *scar*.
        Returns the block hash.
        """
        if result == "PASSED":
            record_type = "receipt"
            block_hash = self._append(record_type, prop_id, result)
            print(f"[deed-ledger] receipt  {prop_id}: {result}  hash={block_hash}")
        else:
            record_type = "scar"
            block_hash = self._append(record_type, prop_id, result, note="minority-reject")
            print(f"[deed-ledger] scar     {prop_id}: {result} (minority-reject) hash={block_hash}")
        return block_hash

    def submit_recovery(self, prop_id: str, note: str, recoverer_did: str) -> str:
        """
        Submit a recovery deed for a scarred proposal.

        The recovery is linked to the scar entry by prop_id.  Returns a
        recovery id.
        """
        scar = next(
            (e for e in self._chain if e["prop_id"] == prop_id and e["type"] == "scar"),
            None,
        )
        if scar is None:
            raise ValueError(f"No scar found for proposal {prop_id}")
        recovery_id = str(uuid.uuid4())[:8]
        self._recoveries[recovery_id] = {
            "id": recovery_id,
            "prop_id": prop_id,
            "scar_hash": scar["hash"],
            "note": note,
            "recoverer_did": recoverer_did,
            "status": "pending",
            "created_at": int(time.time()),
        }
        print(
            f"[deed-ledger] recovery submitted for scar on {prop_id} "
            f"by {recoverer_did.split(':')[-1]} (recovery_id={recovery_id})"
        )
        return recovery_id

    def approve_recovery(self, recovery_id: str, reviewer_did: str) -> None:
        """Approve a pending recovery, reducing the scar's weight."""
        rec = self._recoveries.get(recovery_id)
        if rec is None:
            raise KeyError(f"Unknown recovery: {recovery_id}")
        rec["status"] = "approved"
        rec["reviewer_did"] = reviewer_did
        rec["reviewed_at"] = int(time.time())
        print(
            f"[deed-ledger] recovery {recovery_id} APPROVED by "
            f"{reviewer_did.split(':')[-1]} — scar weight reduced"
        )

    def receipts(self) -> list:
        """Return all receipt entries."""
        return [e for e in self._chain if e["type"] == "receipt"]

    def scars(self) -> list:
        """Return all scar entries."""
        return [e for e in self._chain if e["type"] == "scar"]

    def verify_chain(self) -> bool:
        """
        Verify hash-chain integrity: each block's prev_hash must match the
        previous block's hash.

        Returns True if the chain is intact, False otherwise.
        """
        for i, block in enumerate(self._chain):
            expected_prev = self._chain[i - 1]["hash"] if i > 0 else "0" * 16
            if block["prev_hash"] != expected_prev:
                return False
        return True


# ===========================================================================
# Bridge: GhostAgent
# ===========================================================================

class GhostAgent:
    """Sovereign agent combining cognitive, governance, and messaging layers."""

    def __init__(
        self,
        agent_id: str,
        did_svc: DIDService,
        gov_svc: GovernanceService,
        rep_svc: ReputationService,
        inc_svc: IncentiveService,
        deed_ledger: DeedLedger,
        db_path: str,
    ):
        self.agent_id = agent_id
        self.did = did_svc.create_did(agent_id)
        self.gov_svc = gov_svc
        self.rep_svc = rep_svc
        self.inc_svc = inc_svc
        self.deed_ledger = deed_ledger

        self.brain = BrainSimulation(agent_id)
        self.brain.load_state()
        self.queue = MessageQueue(agent_id, db_path)
        self.daemon = MeshDaemon(agent_id)
        self.inbox = Inbox(agent_id)

        inc_svc.register(agent_id)
        rep_svc.add_node(agent_id)
        print(f"[agent] {agent_id:<7} initialised (DID={self.did})")

    def come_online(self) -> None:
        self.daemon.bring_online()

    def run_brain_cycle(
        self, stimulus_type: str, intensity: float = 0.6, novelty: float = 0.5
    ) -> str:
        result = self.brain.step(stimulus_type, intensity, novelty)
        action = result["action"]
        print(f"[agent] {self.agent_id} brain cycle complete → action={action}")
        return action

    def vote(self, prop_id: str, choice: str) -> None:
        self.gov_svc.vote(prop_id, self.did, choice)
        self.inc_svc.reward(self.agent_id, 5, "governance participation")

    def close(self) -> None:
        self.queue.close()
        self.brain.save_state()


# ===========================================================================
# Main demo — three-node Cell
# ===========================================================================

def main() -> None:
    print("=== Three-Node Cell ===\n")

    db_fd, db_path = tempfile.mkstemp(suffix=".db", prefix="ghoststack_cell3_")
    os.close(db_fd)

    try:
        did_svc = DIDService()
        gov_svc = GovernanceService()
        rep_svc = ReputationService()
        inc_svc = IncentiveService()
        ledger = DeedLedger()

        # --- Create three agents ---
        alice = GhostAgent("alice", did_svc, gov_svc, rep_svc, inc_svc, ledger, db_path)
        bob   = GhostAgent("bob",   did_svc, gov_svc, rep_svc, inc_svc, ledger, db_path)
        carol = GhostAgent("carol", did_svc, gov_svc, rep_svc, inc_svc, ledger, db_path)

        print()

        # -------------------------------------------------------------------
        # Step 1: Alice comes online; Bob and Carol are offline
        # -------------------------------------------------------------------
        alice.come_online()
        action = alice.run_brain_cycle("visual", intensity=0.8, novelty=0.9)

        # Alice queues messages for Bob and Carol
        alice.queue.enqueue("bob",   f"Hey bob, I chose: {action}")
        alice.queue.enqueue("carol", f"Hey carol, I chose: {action}")

        # Sync attempts — Bob and Carol are offline
        sync_deliver(alice.queue, bob.daemon,   bob.inbox)
        sync_deliver(alice.queue, carol.daemon, carol.inbox)
        print()

        # -------------------------------------------------------------------
        # Step 2: Bob comes online and syncs
        # -------------------------------------------------------------------
        bob.come_online()
        bob_count = sync_deliver(alice.queue, bob.daemon, bob.inbox)
        print(f"[sync] {bob_count} message(s) delivered to bob\n")

        # -------------------------------------------------------------------
        # Step 3: Carol comes online and syncs
        # -------------------------------------------------------------------
        carol.come_online()
        carol_count = sync_deliver(alice.queue, carol.daemon, carol.inbox)
        print(f"[sync] {carol_count} message(s) delivered to carol\n")

        # -------------------------------------------------------------------
        # Governance: Proposal 1 — unanimous APPROVE
        # -------------------------------------------------------------------
        prop1 = gov_svc.create_proposal(alice.did, f"cell proposal: {action}")
        alice.vote(prop1, "APPROVE")
        bob.vote(prop1,   "APPROVE")
        carol.vote(prop1, "APPROVE")
        result1 = gov_svc.tally(prop1)
        ledger.record(prop1, result1)
        inc_svc.reward("alice", 10, "proposal creation")
        print()

        # -------------------------------------------------------------------
        # Governance: Proposal 2 — carol proposes, majority APPROVE (2/3)
        # -------------------------------------------------------------------
        prop2 = gov_svc.create_proposal(carol.did, "expand cell bandwidth quota")
        alice.vote(prop2, "APPROVE")
        bob.vote(prop2,   "REJECT")   # bob dissents
        carol.vote(prop2, "APPROVE")
        result2 = gov_svc.tally(prop2)
        ledger.record(prop2, result2)
        inc_svc.reward("carol", 10, "proposal creation")
        print()

        # -------------------------------------------------------------------
        # Governance: Proposal 3 — bob proposes, minority APPROVE → FAILED
        # (alice and carol REJECT; this generates a scar)
        # -------------------------------------------------------------------
        prop3 = gov_svc.create_proposal(bob.did, "reduce relay timeout")
        alice.vote(prop3, "REJECT")
        bob.vote(prop3,   "APPROVE")
        carol.vote(prop3, "REJECT")
        result3 = gov_svc.tally(prop3)
        ledger.record(prop3, result3)
        print()

        # -------------------------------------------------------------------
        # Scar recovery: Bob submits a recovery for the failed proposal
        # -------------------------------------------------------------------
        recovery_id = ledger.submit_recovery(
            prop3,
            note="I've revised the timeout parameters after reviewing alice and carol's concerns",
            recoverer_did=bob.did,
        )
        # Alice (as observer) approves the recovery
        ledger.approve_recovery(recovery_id, reviewer_did=alice.did)
        print()

        # -------------------------------------------------------------------
        # Deed-ledger summary
        # -------------------------------------------------------------------
        print("--- Deed Ledger Summary ---")
        print(f"  Receipts : {len(ledger.receipts())}  "
              f"({', '.join(r['prop_id'] for r in ledger.receipts())})")
        print(f"  Scars    : {len(ledger.scars())}  "
              f"({', '.join(s['prop_id'] for s in ledger.scars())})")
        print(f"  Chain OK : {ledger.verify_chain()}")
        print()

        # -------------------------------------------------------------------
        # Reputation: asymmetric endorsements → carol scores highest
        # -------------------------------------------------------------------
        # Alice and Bob both endorse Carol with high weight.
        # Carol endorses alice and bob with low weight so the strong in-flow
        # concentrates at carol rather than flowing back to alice.
        rep_svc.add_endorsement("alice", "carol", weight=2.0)
        rep_svc.add_endorsement("bob",   "carol", weight=2.0)
        rep_svc.add_endorsement("alice", "bob",   weight=0.5)
        rep_svc.add_endorsement("bob",   "alice", weight=0.5)
        rep_svc.add_endorsement("carol", "alice", weight=0.3)
        rep_svc.add_endorsement("carol", "bob",   weight=0.3)
        scores = rep_svc.compute_scores()
        assert scores["carol"] > scores["alice"], (
            "carol should have a higher reputation score than alice "
            "(she received more endorsement weight)"
        )
        print()

        # -------------------------------------------------------------------
        # Final incentive balances
        # -------------------------------------------------------------------
        inc_svc.print_balances()

        alice.close()
        bob.close()
        carol.close()

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    main()
