"""
Bridge Layer: GhostAgent
=========================
A single GhostAgent that combines brain cognition, governance participation,
and offline-first messaging in one coherent entity.

This script is self-contained — no imports from other example files needed.

Components (inline):
  - MeshDaemon / MessageQueue  (Layer 1: offline-first messaging)
  - DIDService / GovernanceService / IncentiveService  (Layer 2: governance)
  - BrainSimulation  (Layer 3: cognition)
  - GhostAgent  (Bridge: combines all three)

Run:
    python 04_bridge_agent.py

Expected output (values vary each run):
    [agent] agent001 initialised (DID=did:sov:agent001)
    [brain] cycle 1  stimulus=visual   ...
    [agent] brain cycle complete → action=explore
    [governance] proposal P-1 created by did:sov:agent001: "agent001 proposes: explore"
    [vote] agent001 → APPROVE on P-1
    [queue] agent001 queued msg → broadcast: "I chose: explore"
    [agent] message queued (delivery requires a sync step — see 05_multi_agent_demo.py)
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
    """Placeholder transport layer; tracks online/offline state."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self._online = False

    def bring_online(self) -> None:
        self._online = True
        print(f"[daemon] {self.node_id:<8} is now ONLINE")

    def is_online(self) -> bool:
        return self._online


class MessageQueue:
    """SQLite-backed per-node message queue."""

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
        print(f"[queue] {self.node_id:<8} queued msg → {recipient}: \"{payload}\"")
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


# ===========================================================================
# Layer 2 — governance & trust
# ===========================================================================

class DIDService:
    """Minimal decentralised-identity service."""

    def __init__(self):
        self._registry: dict = {}
        self._credentials: dict = {}

    def create_did(self, owner: str) -> str:
        did = f"did:sov:{owner}"
        self._registry[did] = {"did": did, "owner": owner}
        return did

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
    """Lightweight proposal/voting engine with a hash-chain anchor."""

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
        print(
            f"[governance] proposal {prop_id} created by {owner}: \"{description}\""
        )
        return prop_id

    def vote(self, prop_id: str, voter_did: str, choice: str) -> None:
        self._votes[prop_id][voter_did] = choice
        owner = voter_did.split(":")[-1]
        print(f"[vote] {owner:<8} → {choice} on {prop_id}")

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
        self._chain.append({"index": len(self._chain), "prev_hash": prev, "hash": block_hash})
        return result


class IncentiveService:
    """Token-based incentive ledger."""

    def __init__(self):
        self._balances: dict = {}

    def register(self, node_id: str, initial_balance: int = 100) -> None:
        self._balances[node_id] = initial_balance

    def reward(self, node_id: str, amount: int, reason: str = "") -> None:
        self._balances[node_id] = self._balances.get(node_id, 0) + amount

    def balance(self, node_id: str) -> int:
        return self._balances.get(node_id, 0)


# ===========================================================================
# Layer 3 — brain simulation
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
        rpe = reward - predicted
        self.dopamine = round(max(0.0, min(1.0, self.dopamine + 0.2 * rpe)), 3)
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
        probs = {k: v / total for k, v in exp_s.items()}
        r, cumulative, chosen = random.random(), 0.0, self.ACTIONS[-1]
        for action, prob in probs.items():
            cumulative += prob
            if r <= cumulative:
                chosen = action
                break
        return chosen


class BrainSimulation:
    """Minimal cognitive loop (stimulus → emotion → action)."""

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
            f"[brain] cycle {self._cycle:<3} stimulus={stimulus_type:<8} "
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
        print(f"[persist] {self.agent_id} state saved to {self.state_path}")

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
    A sovereign agent that combines cognitive, governance, and messaging layers.

    Lifecycle per interaction:
      1. run_brain_cycle()  – process a stimulus → pick an action
      2. propose_action()   – translate action into a governance proposal
      3. send_message()     – enqueue outcome for later delivery via sync
    """

    def __init__(
        self,
        agent_id: str,
        did_svc: DIDService,
        gov_svc: GovernanceService,
        inc_svc: IncentiveService,
        db_path: str,
    ):
        self.agent_id = agent_id
        self.did_svc = did_svc
        self.gov_svc = gov_svc
        self.inc_svc = inc_svc

        self.did = did_svc.create_did(agent_id)
        self.brain = BrainSimulation(agent_id)
        self.brain.load_state()
        self.queue = MessageQueue(agent_id, db_path)
        self.daemon = MeshDaemon(agent_id)
        inc_svc.register(agent_id)

        print(f"[agent] {agent_id} initialised (DID={self.did})")

    def run_brain_cycle(
        self, stimulus_type: str, intensity: float = 0.6, novelty: float = 0.5
    ) -> str:
        result = self.brain.step(stimulus_type, intensity, novelty)
        action = result["action"]
        print(f"[agent] brain cycle complete → action={action}")
        return action

    def propose_action(self, action: str) -> str:
        description = f"{self.agent_id} proposes: {action}"
        prop_id = self.gov_svc.create_proposal(self.did, description)
        self.gov_svc.vote(prop_id, self.did, "APPROVE")
        self.inc_svc.reward(self.agent_id, 5, "proposal creation")
        return prop_id

    def send_message(self, recipient: str, text: str) -> int:
        msg_id = self.queue.enqueue(recipient, text)
        print(
            "[agent] message queued "
            "(delivery requires a sync step — see 05_multi_agent_demo.py)"
        )
        return msg_id

    def save_brain(self) -> None:
        self.brain.save_state()


# ===========================================================================
# Main demo
# ===========================================================================

def main() -> None:
    db_fd, db_path = tempfile.mkstemp(suffix=".db", prefix="ghoststack_bridge_")
    os.close(db_fd)

    try:
        did_svc = DIDService()
        gov_svc = GovernanceService()
        inc_svc = IncentiveService()

        agent = GhostAgent(
            agent_id="agent001",
            did_svc=did_svc,
            gov_svc=gov_svc,
            inc_svc=inc_svc,
            db_path=db_path,
        )

        # 1. Brain cycle
        action = agent.run_brain_cycle("visual", intensity=0.8, novelty=0.9)

        # 2. Governance proposal based on the cognitive decision
        prop_id = agent.propose_action(action)

        # 3. Queue a message for later delivery
        agent.send_message("broadcast", f"I chose: {action}")

        # 4. Persist cognitive state
        agent.save_brain()

        print(f"\n[summary] proposal={prop_id}  queued messages: 1")

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    main()
