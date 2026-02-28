"""
test_bridge.py — pytest suite for DeedMeshBridge.

Tests:
  - Deed model creation / serialisation
  - Packet → Deed conversion
  - Ingest POST (mocked)
  - send_proposal end-to-end (mocked)
  - Signature verification
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make bridge importable from sibling directory
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from DeedMeshBridge import (  # noqa: E402
    BridgeConfig,
    Deed,
    DeedMeshBridge,
    _sign_payload,
    load_config,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def cfg(tmp_path: Path) -> BridgeConfig:
    """Return a minimal BridgeConfig for testing."""
    return BridgeConfig(
        meshtastic_port="mock",
        deed_ingest_url="http://localhost:3000/api/deeds/ingest",
        cell_id="cell-test-001",
        private_key_path=str(tmp_path / "test.key"),
    )


@pytest.fixture()
def mock_interface() -> MagicMock:
    """A mock Meshtastic interface that records sent texts."""
    iface = MagicMock()
    iface.nodes = {
        "!aabbccdd": {"id": "!aabbccdd", "user": {"longName": "Test-Node"}},
    }
    return iface


@pytest.fixture()
def bridge(cfg: BridgeConfig, mock_interface: MagicMock) -> DeedMeshBridge:
    """Return a DeedMeshBridge pre-wired with a mock interface."""
    b = DeedMeshBridge.__new__(DeedMeshBridge)
    b.config = cfg
    b._interface = mock_interface
    b._last_deeds = []
    b._running = False
    return b


# ── Deed model tests ──────────────────────────────────────────────────────────

def test_deed_creation():
    deed = Deed(
        deed_id="abc123",
        deed_type="proposal",
        content="Share solar",
        cell_id="cell-alpha-001",
        timestamp=1700000000,
        source_node="!aabbccdd",
    )
    assert deed.deed_id == "abc123"
    assert deed.deed_type == "proposal"
    assert deed.cell_id == "cell-alpha-001"


def test_deed_serialises_to_dict():
    deed = Deed(
        deed_id="d1",
        deed_type="mesh_packet",
        content="hello mesh",
        cell_id="cell-beta",
        timestamp=1700000000,
        source_node="!00112233",
        pubkey="pub",
        signature="sig",
    )
    data = deed.model_dump()
    assert data["deed_id"] == "d1"
    assert data["pubkey"] == "pub"
    assert "signature" in data


# ── Config loader tests ───────────────────────────────────────────────────────

def test_load_config_defaults(tmp_path: Path):
    """load_config should return defaults when file is absent."""
    config = load_config(str(tmp_path / "nonexistent.yaml"))
    assert config.meshtastic_port == "/dev/ttyUSB0"
    assert config.cell_id == "cell-alpha-001"


def test_load_config_from_yaml(tmp_path: Path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "meshtastic_port: /dev/ttyACM0\n"
        "cell_id: cell-beta-002\n"
        "deed_ingest_url: http://example.com/ingest\n"
        "nostr_relay: wss://relay.example.com\n"
        "private_key_path: ~/.sov/keys/test.key\n"
    )
    config = load_config(str(cfg_file))
    assert config.meshtastic_port == "/dev/ttyACM0"
    assert config.cell_id == "cell-beta-002"


# ── Packet → Deed conversion tests ───────────────────────────────────────────

def test_packet_to_deed_basic(bridge: DeedMeshBridge):
    packet = {
        "fromId": "!aabbccdd",
        "rxTime": 1700000000,
        "decoded": {"text": "Hello mesh"},
    }
    deed = bridge._packet_to_deed(packet)
    assert deed is not None
    assert deed.deed_type == "mesh_packet"
    assert deed.content == "Hello mesh"
    assert deed.source_node == "!aabbccdd"
    assert deed.cell_id == bridge.config.cell_id


def test_packet_to_deed_missing_text(bridge: DeedMeshBridge):
    """Packets with no text produce an empty-content deed (not None)."""
    packet = {"fromId": "!aabbccdd", "rxTime": 1700000000, "decoded": {}}
    deed = bridge._packet_to_deed(packet)
    assert deed is not None
    assert deed.content == ""


def test_packet_to_deed_missing_from_id(bridge: DeedMeshBridge):
    packet = {"rxTime": 1700000000, "decoded": {"text": "anon msg"}}
    deed = bridge._packet_to_deed(packet)
    assert deed is not None
    assert deed.source_node == "unknown"


# ── Ingest POST tests ─────────────────────────────────────────────────────────

def test_post_deed_success(bridge: DeedMeshBridge):
    deed = Deed(
        deed_id="d2",
        deed_type="proposal",
        content="test",
        cell_id="cell-test",
        timestamp=1700000000,
        source_node="bridge",
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    with patch("requests.post", return_value=mock_resp) as mock_post:
        result = bridge._post_deed(deed)
    assert result is True
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs.kwargs["json"]["deed_id"] == "d2"


def test_post_deed_http_error(bridge: DeedMeshBridge):
    import requests as req_mod
    deed = Deed(
        deed_id="d3",
        deed_type="mesh_packet",
        content="fail",
        cell_id="cell-test",
        timestamp=1700000000,
        source_node="!xyz",
    )
    with patch("requests.post", side_effect=req_mod.RequestException("timeout")):
        result = bridge._post_deed(deed)
    assert result is False


# ── send_proposal end-to-end ──────────────────────────────────────────────────

def test_send_proposal_returns_deed(bridge: DeedMeshBridge):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    with patch("requests.post", return_value=mock_resp):
        deed = bridge.send_proposal("Proposal: share 50W solar")
    assert deed is not None
    assert deed.deed_type == "proposal"
    assert "solar" in deed.content
    assert deed.cell_id == bridge.config.cell_id


def test_send_proposal_queued_in_last_deeds(bridge: DeedMeshBridge):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("requests.post", return_value=mock_resp):
        bridge.send_proposal("P1")
        bridge.send_proposal("P2")
    assert len(bridge._last_deeds) == 2


def test_send_proposal_broadcasts_to_mesh(bridge: DeedMeshBridge, mock_interface: MagicMock):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("requests.post", return_value=mock_resp):
        bridge.send_proposal("mesh broadcast test")
    mock_interface.sendText.assert_called()


# ── on_mesh_receive integration ───────────────────────────────────────────────

def test_on_mesh_receive_valid_packet(bridge: DeedMeshBridge):
    packet = {
        "fromId": "!aabbccdd",
        "rxTime": 1700000000,
        "decoded": {"text": "vote yes on P-1"},
    }
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("requests.post", return_value=mock_resp):
        deed = bridge.on_mesh_receive(packet)
    assert deed is not None
    assert deed.content == "vote yes on P-1"


def test_on_mesh_receive_invalid_signature(bridge: DeedMeshBridge):
    """Packets with a bad signature should be dropped (return None)."""
    packet = {
        "fromId": "!aabbccdd",
        "rxTime": 1700000000,
        "decoded": {
            "text": "tampered content",
            "signature": "badhash",
        },
    }
    deed = bridge.on_mesh_receive(packet)
    assert deed is None


# ── Signing stub ──────────────────────────────────────────────────────────────

def test_sign_payload_without_key(tmp_path: Path):
    pubkey, sig = _sign_payload("hello", str(tmp_path / "missing.key"))
    assert pubkey == ""
    assert len(sig) == 64  # sha256 hex


def test_sign_payload_with_key(tmp_path: Path):
    key_file = tmp_path / "test.key"
    key_file.write_text("my-secret-key")
    pubkey, sig = _sign_payload("hello", str(key_file))
    assert pubkey != ""
    assert len(sig) == 64


# ── get_status ────────────────────────────────────────────────────────────────

def test_get_status_returns_nodes_and_deeds(bridge: DeedMeshBridge):
    status = bridge.get_status()
    assert "nodes" in status
    assert "last_deeds" in status
    assert len(status["nodes"]) == 1  # from mock_interface fixture
