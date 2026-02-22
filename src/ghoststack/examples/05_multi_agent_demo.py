"""
Multi-Agent Integration Demo
==============================
Two GhostAgents (alice, bob) running the full offline → online → sync → govern
→ reputation → incentive loop together.

Scenario:
  1. Alice comes online first; Bob is still offline.
  2. Alice runs a brain cycle and queues a message for Bob.
  3. Bob comes online — sync delivers Alice's queued messages.
  4. Both participate in a governance proposal.
  5. Reputation scores and incentive balances are printed.

This script is self-contained — no imports from other example files needed.

Run:
    python 05_multi_agent_demo.py

Expected output (values vary per run):
    [agent] alice  initialised (DID=did:sov:alice)
    [agent] bob    initialised (DID=did:sov:bob)
    [daemon] alice  is now ONLINE
    [brain] cycle 1  stimulus=visual   ...  action=explore
    [agent] alice brain cycle complete → action=explore
    [queue] alice  queued msg → bob: "Hey bob, I chose: explore"
    [daemon] bob    is OFFLINE — 1 message(s) held in alice's queue
    [daemon] bob    is now ONLINE
    [sync] delivering msg id=1 from alice → bob
    [inbox] bob    received: Hey bob, I chose: explore
    [governance] proposal P-1 created by alice: "cell proposal: explore"
    [vote] alice   → APPROVE on P-1
    [vote] bob     → APPROVE on P-1
    [tally] P-1: approve=2 reject=0 → PASSED
    [reputation] scores: alice=0.59  bob=0.41
    [incentive] alice balance: 115   bob balance: 105
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
        payload = json.dumps({"prop_id": prop_id, "result": result})
        block_hash = hashlib.sha256((prev + payload).encode()).hexdigest()[:16]
        self._chain.append({
            "index": len(self._chain), "prev_hash": prev, "hash": block_hash
        })
        print(
            f"[chain] block {len(self._chain) - 1}: {prev} → {block_hash}"
        )
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
            print(f"[incentive] {node_id} balance: {balance}")


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
        self.valence = round(
            max(0.0, min(1.0,
                self.valence * (1 - self.DECAY) + (0.5 + 0.3 * novelty) * self.DECAY
            )), 3
        )
        self.arousal = round(
            max(0.0, min(1.0,
                self.arousal * (1 - self.DECAY) + intensity * self.DECAY
            )), 3
        )

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
            f"[brain] {self.agent_id} cycle {self._cycle:<2} stimulus={stimulus_type:<8} "
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
# Bridge: GhostAgent
# ===========================================================================

class GhostAgent:
    """
    Sovereign agent combining cognitive, governance, and messaging layers.
    """

    def __init__(
        self,
        agent_id: str,
        did_svc: DIDService,
        gov_svc: GovernanceService,
        rep_svc: ReputationService,
        inc_svc: IncentiveService,
        db_path: str,
    ):
        self.agent_id = agent_id
        self.did = did_svc.create_did(agent_id)
        self.gov_svc = gov_svc
        self.rep_svc = rep_svc
        self.inc_svc = inc_svc

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
# Main demo
# ===========================================================================

def main() -> None:
    db_fd, db_path = tempfile.mkstemp(suffix=".db", prefix="ghoststack_multi_")
    os.close(db_fd)

    try:
        did_svc = DIDService()
        gov_svc = GovernanceService()
        rep_svc = ReputationService()
        inc_svc = IncentiveService()

        # --- Create two agents ---
        alice = GhostAgent("alice", did_svc, gov_svc, rep_svc, inc_svc, db_path)
        bob = GhostAgent("bob", did_svc, gov_svc, rep_svc, inc_svc, db_path)

        # --- Alice comes online; Bob is still offline ---
        alice.come_online()

        action = alice.run_brain_cycle("visual", intensity=0.8, novelty=0.9)

        # Alice queues a message for Bob
        alice.queue.enqueue("bob", f"Hey bob, I chose: {action}")

        # Attempt sync — Bob is offline, nothing delivered
        sync_deliver(alice.queue, bob.daemon, bob.inbox)

        print()

        # --- Bob comes online ---
        bob.come_online()

        # Sync now delivers
        delivered = sync_deliver(alice.queue, bob.daemon, bob.inbox)
        print(f"[sync] {delivered} message(s) delivered to bob\n")

        # --- Both participate in governance ---
        prop_id = gov_svc.create_proposal(
            alice.did, f"cell proposal: {action}"
        )
        alice.vote(prop_id, "APPROVE")
        bob.vote(prop_id, "APPROVE")
        gov_svc.tally(prop_id)

        print()

        # --- Reputation: mutual endorsement ---
        rep_svc.add_endorsement("alice", "bob", weight=1.0)
        rep_svc.add_endorsement("bob", "alice", weight=0.5)
        rep_svc.compute_scores()

        # Bonus rewards
        inc_svc.reward("alice", 10, "proposal creation")
        inc_svc.print_balances()

        alice.close()
        bob.close()

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    main()
