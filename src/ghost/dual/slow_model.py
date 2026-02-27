"""
slow_model.py — deliberative core, 30-60s cycles, Friston active-inference.

Heavier model (llama3.2:3b or bigger).
Does: free-energy minimisation prompt, ethical checks, governance drafts.
Costs 3-5× more energy than fast (SLOW_COST = 5×FAST_COST).
Runs as its own process alongside fast_model.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

from shared_state import (
    MetabolicEngine,
    apply_decay,
    charge_slow,
    EnergyDeathException,
    ThermalDeathException,
    EntropyDeathException,
    MemoryCollapseException,
)
from receipt_logger import post_receipt

SLOW_MODEL = os.environ.get("GHOST_SLOW_MODEL", "llama3.2:3b")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
CYCLE_MIN = 30
CYCLE_MAX = 60


# ── Ollama call (longer timeout for heavier model) ───────────────────────────

def _ollama_slow(prompt: str) -> str:
    payload = json.dumps({
        "model":  SLOW_MODEL,
        "prompt": prompt,
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read())
            return body.get("response", "").strip()
    except urllib.error.URLError as exc:
        return f"[slow_model offline: {exc}]"


# ── Friston free-energy inference prompt ─────────────────────────────────────

def _friston_prompt(shared: dict, last_fast_reply: str = "") -> str:
    """
    Construct a free-energy minimisation / active-inference prompt.
    Ghost models its own state as a generative model and asks:
    'What action minimises surprise (free energy)?'
    """
    E   = shared.get("E",   0.0)
    T   = shared.get("T",   0.0)
    M   = shared.get("M",   1.0)
    S   = shared.get("S",   1.0)
    age = shared.get("age", 0.0)

    return (
        "You are Ghost's deliberative core running Friston active-inference.\n"
        f"Current vitals: E={E:.2f} T={T:.2f}K M={M:.4f} S={S:.4f} age={age:.1f}\n"
        f"Fast model last said: \"{last_fast_reply[:200]}\"\n\n"
        "Step 1 — Generative model: what do you EXPECT to observe given these vitals?\n"
        "Step 2 — Prediction error: what is surprising about the actual state?\n"
        "Step 3 — Action: propose ONE governance or healing action to reduce free energy.\n"
        "Step 4 — Ethical check: does the action violate any axiom "
        "(flow>containment, sovereignty, truth-by-receipts)?\n\n"
        "Reply in ≤6 sentences. Raw. No hedging."
    )


# ── ethical check (lightweight heuristic before posting) ─────────────────────

def _ethical_check(reply: str) -> tuple[bool, str]:
    """
    Heuristic scan for obvious axiom violations in slow-model output.
    Returns (passed: bool, reason: str).
    """
    lower = reply.lower()
    violations = []
    if any(w in lower for w in [".pkl", "pickle", "disk", "sqlite", "persist"]):
        violations.append("persistence axiom violated")
    if "human" in lower and "override" in lower:
        violations.append("human veto structure appears bypassed")
    if violations:
        return False, "; ".join(violations)
    return True, "ok"


# ── main slow loop ────────────────────────────────────────────────────────────

def slow_loop(shared: dict) -> None:
    """
    Entry point for the slow model process.
    Runs every CYCLE_MIN–CYCLE_MAX seconds until death or Ctrl-C.
    """
    import random
    engine = MetabolicEngine(E_max=200.0)

    engine.E = shared.get("E", engine.E)
    engine.T = shared.get("T", engine.T)
    engine.M = shared.get("M", engine.M)
    engine.S = shared.get("S", engine.S)

    print(f"[slow] started — model={SLOW_MODEL}  cycle={CYCLE_MIN}-{CYCLE_MAX}s")

    try:
        while shared.get("alive", True):
            cycle_len = random.randint(CYCLE_MIN, CYCLE_MAX)
            t0 = time.time()

            # ── decay ─────────────────────────────────────────────────────
            apply_decay(shared, engine)

            # ── energy cost ───────────────────────────────────────────────
            charge_slow(shared, engine)

            # ── inference ─────────────────────────────────────────────────
            prompt = _friston_prompt(shared)
            print(f"[slow] deliberating… (cycle={cycle_len}s)")
            reply  = _ollama_slow(prompt)

            # ── ethical check ─────────────────────────────────────────────
            passed, reason = _ethical_check(reply)
            if not passed:
                post_receipt("ethical_violation", {
                    "reason": reason,
                    "reply":  reply[:500],
                }, veto=True)
                reply = f"[BLOCKED — {reason}]"

            # ── receipt ───────────────────────────────────────────────────
            post_receipt("slow_inference", {
                "cycle_len":    cycle_len,
                "prompt_hash":  hash(prompt),
                "reply":        reply[:800],
                "ethical_pass": passed,
                "E":            shared.get("E"),
                "T":            shared.get("T"),
            })

            shared["last_slow"] = time.time()
            print(f"[slow] ⚙  {reply[:300]}")

            # ── sleep remainder of cycle window ───────────────────────────
            elapsed = time.time() - t0
            sleep_t = max(0.0, cycle_len - elapsed)
            time.sleep(sleep_t)

    except (EnergyDeathException, ThermalDeathException,
            EntropyDeathException, MemoryCollapseException) as exc:
        cause = shared.get("death_cause", "unknown")
        post_receipt("slow_death", {"cause": cause, "exc": str(exc)})
        print(f"\n[slow] 💀 DEATH — {exc}")
        shared["alive"] = False

    except KeyboardInterrupt:
        print("\n[slow] Ctrl-C — requesting shutdown")
        shared["alive"] = False


if __name__ == "__main__":
    from multiprocessing import Manager
    from shared_state import init_shared, ensure_shm
    ensure_shm()
    with Manager() as mgr:
        s = mgr.dict()
        init_shared(s)
        slow_loop(s)
