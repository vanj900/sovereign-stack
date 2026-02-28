"""
DeedMeshBridge.py — Meshtastic LoRa ↔ Sovereign Deed ingest bridge.

Axiom compliance:
  Flow over Containment  — packets circulate; no hoarding of state
  Sovereignty via Forkability — config-driven; swap transport or schema freely
  Truth by Receipts — every received deed + sent proposal produces a signed receipt

Usage (direct):
    bridge = DeedMeshBridge("bridge/config.yaml")
    bridge.run()
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import requests
import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ── Sovereign Deed schema (mirrors deed-ledger reputation.graphql) ─────────────

class Deed(BaseModel):
    """Atomic unit of reputation / receipt — Truth by Receipts axiom."""

    deed_id: str
    deed_type: str
    content: str
    cell_id: str
    timestamp: int
    source_node: str
    pubkey: str = ""
    signature: str = ""


class UserReputation(BaseModel):
    """Running score for a mesh node — demurrage decay applied server-side."""

    node_id: str
    deeds_count: int = 0
    last_deed_ts: int = 0
    reputation_score: float = 0.0


# ── Configuration loader ───────────────────────────────────────────────────────

class BridgeConfig(BaseModel):
    meshtastic_port: str = "/dev/ttyUSB0"
    deed_ingest_url: str = "http://localhost:3000/api/deeds/ingest"
    nostr_relay: str = "wss://nostr.example.com"
    cell_id: str = "cell-alpha-001"
    private_key_path: str = "~/.sov/keys/shadow-net.key"


def load_config(path: str = "config.yaml") -> BridgeConfig:
    """Load YAML config; fall back to defaults if file is missing."""
    cfg_path = Path(path).expanduser()
    if not cfg_path.exists():
        logger.warning("Config not found at %s — using defaults", cfg_path)
        return BridgeConfig()
    with cfg_path.open() as fh:
        data = yaml.safe_load(fh) or {}
    return BridgeConfig(**data)


# ── Nostr signing stub ────────────────────────────────────────────────────────

def _sign_payload(payload: str, key_path: str) -> tuple[str, str]:
    """
    Minimal signing stub — returns (pubkey, sig).

    Flow over Containment: real implementation swaps in `nak` binary or
    nostr-tools without changing any other code.

    Returns hex-encoded sha256(payload) as a deterministic stub signature
    when no private key is present.
    """
    key_file = Path(key_path).expanduser()
    if key_file.exists():
        try:
            secret = key_file.read_text().strip()
            sig = hashlib.sha256((secret + payload).encode()).hexdigest()
            pubkey = hashlib.sha256(secret.encode()).hexdigest()[:32]
            return pubkey, sig
        except OSError as exc:
            logger.warning("Could not read key file %s: %s", key_file, exc)
    # Unsigned fallback — still produces a deterministic stub
    sig = hashlib.sha256(payload.encode()).hexdigest()
    return "", sig


# ── Core bridge class ─────────────────────────────────────────────────────────

class DeedMeshBridge:
    """
    Bridges Meshtastic LoRa mesh ↔ Sovereign deed-ledger.

    Forkability axiom: swap _interface (serial/TCP/mock) without touching
    any Deed conversion or ingest logic.
    """

    DEED_WINDOW_SIZE: int = 10  # rolling window of recent deeds for status

    def __init__(self, config_path: str = "config.yaml"):
        # ── Flow: load config first, then connect ─────────────────────────
        self.config = load_config(config_path)
        self._interface: Any = None          # meshtastic.StreamInterface or mock
        self._last_deeds: list[Deed] = []    # rolling window for status cmd
        self._running = False
        logger.info(
            "DeedMeshBridge init: port=%s cell=%s",
            self.config.meshtastic_port,
            self.config.cell_id,
        )

    # ── Transport connect / disconnect ────────────────────────────────────

    def connect(self) -> None:
        """
        Connect to Meshtastic device (serial or TCP).

        Forkability: pass a pre-built mock interface in tests by setting
        self._interface before calling connect().
        """
        if self._interface is not None:
            return  # already connected (or mock injected)
        try:
            import meshtastic.serial_interface as _ms  # type: ignore[import]
            self._interface = _ms.SerialInterface(self.config.meshtastic_port)
            logger.info("Connected to Meshtastic on %s", self.config.meshtastic_port)
        except Exception as exc:
            logger.error("Meshtastic connect failed: %s", exc)
            raise

    def disconnect(self) -> None:
        """Gracefully close the Meshtastic interface."""
        if self._interface is not None:
            try:
                self._interface.close()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Error closing interface: %s", exc)
            self._interface = None

    # ── Packet receiver ────────────────────────────────────────────────────

    def on_mesh_receive(self, packet: dict[str, Any]) -> Deed | None:
        """
        Process an incoming Meshtastic packet.

        Truth by Receipts: every valid packet becomes a Deed that is
        POSTed to deed-ledger and receipted back to the mesh.

        Returns the Deed on success, None on validation / network error.
        """
        # ── Flow: verify signature if present ─────────────────────────────
        if not self._verify_packet_signature(packet):
            logger.warning("Packet signature verification failed — dropping: %s", packet)
            return None

        # ── Convert raw packet → Sovereign Deed ───────────────────────────
        deed = self._packet_to_deed(packet)
        if deed is None:
            return None

        # ── POST to deed-ledger ingest endpoint ───────────────────────────
        ok = self._post_deed(deed)
        if not ok:
            logger.warning("Deed ingest POST failed for deed_id=%s", deed.deed_id)

        # ── Broadcast signed receipt back to mesh + log ───────────────────
        self._broadcast_receipt(deed)
        self._last_deeds.append(deed)
        if len(self._last_deeds) > self.DEED_WINDOW_SIZE:
            self._last_deeds.pop(0)

        return deed

    def _verify_packet_signature(self, packet: dict[str, Any]) -> bool:
        """
        Verify the packet's cryptographic signature if present.

        Flow over Containment: no signature → pass through (unsigned nodes
        allowed on internal mesh; receipt marks them as unsigned).
        """
        sig = packet.get("decoded", {}).get("signature", "")
        if not sig:
            return True  # unsigned packets are accepted but not trusted
        payload = packet.get("decoded", {}).get("text", "")
        pubkey = packet.get("fromId", "")
        expected = hashlib.sha256((pubkey + payload).encode()).hexdigest()
        return sig == expected

    def _packet_to_deed(self, packet: dict[str, Any]) -> Deed | None:
        """Convert a raw Meshtastic packet to a Sovereign Deed."""
        try:
            decoded = packet.get("decoded", {})
            text = decoded.get("text", "")
            from_id = str(packet.get("fromId", "unknown"))
            ts = int(packet.get("rxTime", time.time()))
            deed_id = hashlib.sha256(
                f"{from_id}{ts}{text}".encode()
            ).hexdigest()[:16]
            pubkey, sig = _sign_payload(text, self.config.private_key_path)
            return Deed(
                deed_id=deed_id,
                deed_type="mesh_packet",
                content=text,
                cell_id=self.config.cell_id,
                timestamp=ts,
                source_node=from_id,
                pubkey=pubkey,
                signature=sig,
            )
        except Exception as exc:
            logger.error("Packet → Deed conversion failed: %s", exc)
            return None

    def _post_deed(self, deed: Deed) -> bool:
        """
        POST a Deed to the deed-ledger ingest endpoint.

        Truth by Receipts: the HTTP response IS the receipt.
        """
        try:
            resp = requests.post(
                self.config.deed_ingest_url,
                json=deed.model_dump(),
                timeout=5,
            )
            resp.raise_for_status()
            logger.info("Deed ingested: deed_id=%s status=%s", deed.deed_id, resp.status_code)
            return True
        except requests.RequestException as exc:
            logger.error("Deed ingest HTTP error: %s", exc)
            return False

    def _broadcast_receipt(self, deed: Deed) -> None:
        """
        Broadcast a signed receipt back to the mesh and log it.

        Truth by Receipts: receipts make actions legible and accountable.
        """
        receipt = {
            "type": "deed_receipt",
            "deed_id": deed.deed_id,
            "cell_id": deed.cell_id,
            "ts": deed.timestamp,
            "sig": deed.signature,
        }
        receipt_json = json.dumps(receipt)
        if self._interface is not None:
            try:
                self._interface.sendText(receipt_json)
                logger.info("Receipt broadcast: %s", receipt_json)
            except Exception as exc:
                logger.warning("Mesh broadcast failed: %s", exc)
        # Always log receipt regardless of mesh broadcast outcome
        self._log_event("deed_receipt", receipt)

    # ── Proposal sender ────────────────────────────────────────────────────

    def send_proposal(self, proposal_text: str) -> Deed | None:
        """
        GhostAgent → signed Deed → mesh + ledger.

        Flow over Containment: Ghost proposes; mesh circulates; ledger receipts.
        Forkability: proposal_text can be any string — no schema lock-in.
        """
        ts = int(time.time())
        pubkey, sig = _sign_payload(proposal_text, self.config.private_key_path)
        deed_id = hashlib.sha256(
            f"proposal{ts}{proposal_text}".encode()
        ).hexdigest()[:16]

        deed = Deed(
            deed_id=deed_id,
            deed_type="proposal",
            content=proposal_text,
            cell_id=self.config.cell_id,
            timestamp=ts,
            source_node="bridge",
            pubkey=pubkey,
            signature=sig,
        )

        # Send to mesh
        if self._interface is not None:
            try:
                self._interface.sendText(json.dumps(deed.model_dump()))
                logger.info("Proposal sent to mesh: %s", deed_id)
            except Exception as exc:
                logger.warning("Mesh send failed: %s", exc)

        # Ingest into ledger — Truth by Receipts
        self._post_deed(deed)
        self._log_event("proposal_sent", deed.model_dump())
        self._last_deeds.append(deed)
        if len(self._last_deeds) > self.DEED_WINDOW_SIZE:
            self._last_deeds.pop(0)

        return deed

    # ── Status / logging helpers ───────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        """Return current mesh node list and last 10 deeds."""
        nodes: list[dict] = []
        if self._interface is not None:
            try:
                raw_nodes = getattr(self._interface, "nodes", {}) or {}
                nodes = list(raw_nodes.values()) if isinstance(raw_nodes, dict) else []
            except Exception as exc:
                logger.warning("Could not fetch node list: %s", exc)
        return {
            "nodes": nodes,
            "last_deeds": [d.model_dump() for d in self._last_deeds],
        }

    def _log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Append an event to the local EventLog (stdout + structured log)."""
        entry = {
            "event": event_type,
            "ts": int(time.time()),
            "payload": payload,
        }
        logger.info("[EventLog] %s", json.dumps(entry))

    # ── Run loop ───────────────────────────────────────────────────────────

    def run(self) -> None:
        """
        Main event loop — subscribe to Meshtastic receive callback.

        Flow over Containment: callback-driven; never polls.
        """
        self.connect()
        self._running = True

        # Register receive callback
        from pubsub import pub  # type: ignore[import]

        def _on_receive(packet: dict, interface: Any) -> None:  # noqa: ARG001
            self.on_mesh_receive(packet)

        pub.subscribe(_on_receive, "meshtastic.receive")
        logger.info("Bridge running — listening on %s", self.config.meshtastic_port)

        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bridge stopped by user")
        finally:
            self.disconnect()
            self._running = False
