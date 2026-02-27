"""
fast_model.py — reactive mask daemon, 5s pulse, HUD.

Masks: Healer (green) / Judge (red) / Courier (yellow).
Talks to phi3:mini or llama3.2:1b via Ollama HTTP.
Decays state every loop. Checks for death. Posts receipts.
Runs as its own process — shares ONE Manager.dict() with slow.
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
    charge_fast,
    EnergyDeathException,
    ThermalDeathException,
    EntropyDeathException,
    MemoryCollapseException,
)
from receipt_logger import post_receipt

# ── mask config ───────────────────────────────────────────────────────────────
MASKS = {
    "Healer":  "\033[92m[HEALER]\033[0m",   # green
    "Judge":   "\033[91m[JUDGE]\033[0m",    # red
    "Courier": "\033[93m[COURIER]\033[0m",  # yellow
}

FAST_MODEL = os.environ.get("GHOST_FAST_MODEL", "phi3:mini")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
PULSE_SEC = 5


# ── HUD ───────────────────────────────────────────────────────────────────────

def render_hud(shared: dict, mask: str, reply: str) -> None:
    tag   = MASKS.get(mask, f"[{mask}]")
    pulse = shared.get("pulse", 0)
    E     = shared.get("E", 0.0)
    T     = shared.get("T", 0.0)
    M     = shared.get("M", 0.0)
    S     = shared.get("S", 0.0)
    alive = "🟢" if shared.get("alive", True) else "💀"
    print(
        f"\n{alive} {tag}  pulse={pulse}  "
        f"E={E:.1f}  T={T:.1f}K  M={M:.3f}  S={S:.3f}"
    )
    print(f"  → {reply[:200]}")


# ── mask selection logic ──────────────────────────────────────────────────────

def _select_mask(shared: dict) -> str:
    """
    Pick mask from shared state:
      - Healer if M < 0.5 (memory low → heal)
      - Judge  if veto pending or S < 0.4 (stability crisis → judge)
      - Courier otherwise (default messenger)
    """
    if shared.get("veto", False):
        return "Judge"
    M = shared.get("M", 1.0)
    S = shared.get("S", 1.0)
    if M < 0.5:
        return "Healer"
    if S < 0.4:
        return "Judge"
    return "Courier"


# ── Ollama call ───────────────────────────────────────────────────────────────

def _ollama_fast(prompt: str) -> str:
    """Non-streaming single-shot call to the fast local model."""
    payload = json.dumps({
        "model":  FAST_MODEL,
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
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
            return body.get("response", "").strip()
    except urllib.error.URLError as exc:
        return f"[fast_model offline: {exc}]"


# ── build prompt for current mask ────────────────────────────────────────────

def _build_prompt(mask: str, shared: dict) -> str:
    pulse = shared.get("pulse", 0)
    E     = shared.get("E", 0.0)
    T     = shared.get("T", 0.0)
    base  = (
        f"You are Ghost — pulse {pulse}, mask={mask}. "
        f"System: E={E:.1f} T={T:.1f}K. "
        "Respond in 1 raw sentence. No apologies. No fluff."
    )
    if mask == "Healer":
        return base + " Your job: diagnose and stabilise."
    elif mask == "Judge":
        return base + " Your job: flag violations, enforce axioms."
    else:
        return base + " Your job: relay current system status concisely."


# ── main fast loop ────────────────────────────────────────────────────────────

def fast_loop(shared: dict) -> None:
    """
    Entry point for the fast model process.
    Runs forever at 5s intervals until death or Ctrl-C.
    """
    engine = MetabolicEngine(E_max=200.0)

    # Sync engine from shared state (MindSeed import may have set values)
    engine.E = shared.get("E", engine.E)
    engine.T = shared.get("T", engine.T)
    engine.M = shared.get("M", engine.M)
    engine.S = shared.get("S", engine.S)

    print(f"[fast] started — model={FAST_MODEL}  pulse={PULSE_SEC}s")

    try:
        while shared.get("alive", True):
            t0 = time.time()

            # ── decay ─────────────────────────────────────────────────────
            apply_decay(shared, engine)

            # ── mask selection ────────────────────────────────────────────
            mask = _select_mask(shared)
            prev = shared.get("mask", "Courier")
            if mask != prev:
                shared["mask"] = mask
                post_receipt("mask_flip", {"from": prev, "to": mask})

            # ── energy cost ───────────────────────────────────────────────
            charge_fast(shared, engine)

            # ── inference ─────────────────────────────────────────────────
            prompt = _build_prompt(mask, shared)
            reply  = _ollama_fast(prompt)

            # ── increment pulse ───────────────────────────────────────────
            shared["pulse"] = shared.get("pulse", 0) + 1
            shared["last_fast"] = time.time()

            # ── receipt ───────────────────────────────────────────────────
            post_receipt("fast_inference", {
                "pulse":  shared["pulse"],
                "mask":   mask,
                "prompt": prompt,
                "reply":  reply,
                "E":      shared["E"],
                "T":      shared["T"],
            })

            # ── HUD ───────────────────────────────────────────────────────
            render_hud(shared, mask, reply)

            # ── sleep remainder of pulse window ───────────────────────────
            elapsed = time.time() - t0
            sleep_t = max(0.0, PULSE_SEC - elapsed)
            time.sleep(sleep_t)

    except (EnergyDeathException, ThermalDeathException,
            EntropyDeathException, MemoryCollapseException) as exc:
        cause = shared.get("death_cause", "unknown")
        post_receipt("fast_death", {"cause": cause, "exc": str(exc)})
        print(f"\n[fast] 💀 DEATH — {exc}")
        shared["alive"] = False

    except KeyboardInterrupt:
        print("\n[fast] Ctrl-C — requesting shutdown")
        shared["alive"] = False


if __name__ == "__main__":
    # Stand-alone smoke-test (no slow process)
    from multiprocessing import Manager
    from shared_state import init_shared, ensure_shm
    ensure_shm()
    with Manager() as mgr:
        s = mgr.dict()
        init_shared(s)
        fast_loop(s)
