"""
demo.py — Shadow-Net bridge smoke-test.

Starts the bridge with a mock interface, sends 3 test proposals,
and prints receipts in EventLog format.

Run:
    python demo.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Make bridge importable from this directory
sys.path.insert(0, str(Path(__file__).parent))

from DeedMeshBridge import DeedMeshBridge, BridgeConfig


# ── Mock Meshtastic interface ─────────────────────────────────────────────────

class _MockInterface:
    """Minimal mock that records sent texts without touching hardware."""

    def __init__(self) -> None:
        self.sent: list[str] = []
        self.nodes: dict = {
            "!aabbccdd": {"id": "!aabbccdd", "user": {"longName": "Node-Alpha"}},
            "!11223344": {"id": "!11223344", "user": {"longName": "Node-Beta"}},
            "!55667788": {"id": "!55667788", "user": {"longName": "Node-Gamma"}},
        }

    def sendText(self, text: str) -> None:
        self.sent.append(text)

    def close(self) -> None:
        pass


# ── Mock HTTP POST ─────────────────────────────────────────────────────────────

class _MockResponse:
    status_code = 200

    def raise_for_status(self) -> None:
        pass


def _mock_post(url: str, json: dict, timeout: int) -> _MockResponse:  # noqa: ARG001
    return _MockResponse()


# ── Demo runner ───────────────────────────────────────────────────────────────

def main() -> None:
    import requests  # patch before bridge uses it
    requests.post = _mock_post  # type: ignore[method-assign]

    cfg = BridgeConfig(
        meshtastic_port="mock",
        deed_ingest_url="http://localhost:3000/api/deeds/ingest",
        cell_id="cell-demo-001",
    )

    bridge = DeedMeshBridge.__new__(DeedMeshBridge)
    bridge.config = cfg
    bridge._interface = _MockInterface()
    bridge._last_deeds = []
    bridge._running = False

    proposals = [
        "Proposal: share 50W solar with Node-Beta during daylight hours",
        "Proposal: rotate water-filter duty weekly — Node-Alpha starts",
        "Proposal: fork cell if membership exceeds 7 nodes",
    ]

    receipts: list[dict] = []
    for text in proposals:
        deed = bridge.send_proposal(text)
        if deed:
            receipts.append({
                "event": "deed_receipt",
                "ts": deed.timestamp,
                "payload": deed.model_dump(),
            })
        time.sleep(0.05)  # small delay so timestamps differ

    print("\n=== EventLog receipts ===")
    for r in receipts:
        print(json.dumps(r, indent=2))

    print(f"\n✓ {len(receipts)}/3 proposals sent and receipted")
    status = bridge.get_status()
    print(f"✓ {len(status['nodes'])} mesh nodes visible")
    print(f"✓ {len(status['last_deeds'])} deeds in rolling window")


if __name__ == "__main__":
    main()
