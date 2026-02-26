"""
receipt_logger.py — signs every event and posts to the Integrity Chain (deed-ledger).

Every fast/slow interaction, mask flip, conflict, decision, human veto = signed receipt.
No receipt → didn't happen. That's the axiom.
HMAC-SHA256 with a per-session key stored ONLY in /dev/shm — dies with the ghost.
"""

import hashlib
import hmac
import json
import os
import time

from shared_state import SHM_ROOT, shm_path

LEDGER_FILE = shm_path("deed_ledger.jsonl")
_KEY_FILE   = shm_path("session.key")


def _session_key() -> bytes:
    """Load or generate the per-session signing key from tmpfs."""
    if os.path.exists(_KEY_FILE):
        with open(_KEY_FILE, "rb") as f:
            return f.read()
    key = os.urandom(32)
    os.makedirs(SHM_ROOT, exist_ok=True)
    with open(_KEY_FILE, "wb") as f:
        f.write(key)
    return key


def _sign(payload: str) -> str:
    key = _session_key()
    return hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()


def post_receipt(event_type: str, data: dict, *, veto: bool = False) -> dict:
    """
    Build, sign, and append a receipt to the in-RAM deed-ledger.

    Returns the signed receipt dict.
    """
    receipt = {
        "ts":         time.time(),
        "event":      event_type,
        "data":       data,
        "veto":       veto,
        "sig":        None,   # placeholder; filled below
    }
    payload = json.dumps({k: v for k, v in receipt.items() if k != "sig"},
                         sort_keys=True)
    receipt["sig"] = _sign(payload)

    # Append to the in-shm ledger (jsonlines)
    os.makedirs(SHM_ROOT, exist_ok=True)
    with open(LEDGER_FILE, "a") as f:
        f.write(json.dumps(receipt) + "\n")

    return receipt


def verify_receipt(receipt: dict) -> bool:
    """Check a receipt's HMAC against the current session key."""
    payload = json.dumps(
        {k: v for k, v in receipt.items() if k != "sig"}, sort_keys=True
    )
    expected = _sign(payload)
    return hmac.compare_digest(expected, receipt.get("sig", ""))


def read_ledger() -> list:
    """Return all receipts from the current session ledger."""
    if not os.path.exists(LEDGER_FILE):
        return []
    with open(LEDGER_FILE) as f:
        return [json.loads(line) for line in f if line.strip()]
