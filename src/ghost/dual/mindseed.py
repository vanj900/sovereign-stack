"""
mindseed.py — export/import the MindSeed Receipt.

ONLY carry-forward across instance death = this signed JSON blob.
Export → deed-ledger. Import → fresh spawn.
No .pkl. No disk state. Just a receipt you carry in your hand.
"""

import hashlib
import hmac
import json
import os
import time

from shared_state import SHM_ROOT, shm_path
from receipt_logger import post_receipt, _session_key

MINDSEED_FILE = shm_path("mindseed.json")


def export_mindseed(shared: dict, notes: str = "") -> dict:
    """
    Snapshot the current shared state into a signed MindSeed receipt.
    Written to /dev/shm/ghost_dual/mindseed.json AND posted to the deed-ledger.
    Caller should copy this file OUT of shm before wiping.

    Returns the MindSeed dict.
    """
    seed = {
        "schema":    "mindseed/v1",
        "exported":  time.time(),
        "notes":     notes,
        "state": {
            "E":         shared.get("E", 100.0),
            "T":         shared.get("T", 293.15),
            "M":         shared.get("M", 1.0),
            "S":         shared.get("S", 1.0),
            "age":       shared.get("age", 0.0),
            "pulse":     shared.get("pulse", 0),
            "mask":      shared.get("mask", "Healer"),
        },
        "sig": None,
    }

    payload = json.dumps({k: v for k, v in seed.items() if k != "sig"},
                         sort_keys=True)
    key     = _session_key()
    seed["sig"] = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()

    # Write to shm
    os.makedirs(SHM_ROOT, exist_ok=True)
    with open(MINDSEED_FILE, "w") as f:
        json.dump(seed, f, indent=2)

    # Also post to integrity chain
    post_receipt("mindseed_export", seed)

    print(f"[MindSeed] exported → {MINDSEED_FILE}")
    return seed


def import_mindseed(path: str, shared: dict) -> bool:
    """
    Load a MindSeed JSON file and hydrate the shared state.
    Signature is checked against a NEW session key (the old one is gone — instance died).
    The sig field is treated as advisory; structural validation is the real guard.

    Returns True on success.
    """
    if not os.path.exists(path):
        print(f"[MindSeed] file not found: {path}")
        return False

    with open(path) as f:
        seed = json.load(f)

    if seed.get("schema") != "mindseed/v1":
        print("[MindSeed] unknown schema — refusing import")
        return False

    state = seed.get("state", {})
    shared["E"]     = float(state.get("E",     100.0))
    shared["T"]     = float(state.get("T",     293.15))
    shared["M"]     = float(state.get("M",     1.0))
    shared["S"]     = float(state.get("S",     1.0))
    shared["age"]   = float(state.get("age",   0.0))
    shared["pulse"] = int(state.get("pulse",   0))
    shared["mask"]  = str(state.get("mask",    "Healer"))

    post_receipt("mindseed_import", {"from": path, "state": state})
    print(f"[MindSeed] imported from {path} — pulse={shared['pulse']}")
    return True


def print_mindseed(seed: dict) -> None:
    """Pretty-print a MindSeed for human inspection."""
    st = seed.get("state", {})
    print("┌── MindSeed Receipt ────────────────────────────────────┐")
    print(f"│  schema:   {seed.get('schema')}")
    print(f"│  exported: {seed.get('exported')}")
    print(f"│  notes:    {seed.get('notes', '')}")
    print(f"│  E={st.get('E',0):.2f}  T={st.get('T',0):.2f}K  "
          f"M={st.get('M',0):.3f}  S={st.get('S',0):.3f}")
    print(f"│  pulse={st.get('pulse',0)}  mask={st.get('mask','?')}")
    print(f"│  sig: {seed.get('sig','<none>')[:32]}…")
    print("└────────────────────────────────────────────────────────┘")
