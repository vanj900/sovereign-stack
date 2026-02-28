"""
cli.py — command-line entrypoint for Shadow-Net LoRa bridge.

Commands:
    python cli.py start              → run the bridge (blocking)
    python cli.py send "Proposal: …" → send one proposal and exit
    python cli.py status             → print mesh nodes + last 10 deeds
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

DEFAULT_CONFIG = "config.yaml"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shadow-net-bridge",
        description="Shadow-Net LoRa ↔ Deed-ledger bridge",
    )
    parser.add_argument(
        "--config", default=DEFAULT_CONFIG,
        help="Path to config.yaml (default: config.yaml)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("start", help="Run the bridge (blocking event loop)")

    send_p = sub.add_parser("send", help="Send a single proposal to the mesh")
    send_p.add_argument("proposal", help="Proposal text to broadcast")

    sub.add_parser("status", help="Show mesh nodes and last 10 deeds")

    return parser


def cmd_start(config: str) -> None:
    """Start the bridge in blocking mode."""
    from DeedMeshBridge import DeedMeshBridge  # noqa: PLC0415
    bridge = DeedMeshBridge(config)
    bridge.run()


def cmd_send(config: str, proposal_text: str) -> None:
    """Send a single proposal; does not require a persistent run loop."""
    from DeedMeshBridge import DeedMeshBridge  # noqa: PLC0415
    bridge = DeedMeshBridge(config)
    try:
        bridge.connect()
        deed = bridge.send_proposal(proposal_text)
        if deed:
            print(json.dumps(deed.model_dump(), indent=2))
        else:
            print("[error] Proposal failed — check logs", file=sys.stderr)
            sys.exit(1)
    finally:
        bridge.disconnect()


def cmd_status(config: str) -> None:
    """Print mesh node list and last 10 deeds as JSON."""
    from DeedMeshBridge import DeedMeshBridge  # noqa: PLC0415
    bridge = DeedMeshBridge(config)
    try:
        bridge.connect()
        status = bridge.get_status()
        print(json.dumps(status, indent=2))
    finally:
        bridge.disconnect()


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "start":
        cmd_start(args.config)
    elif args.command == "send":
        cmd_send(args.config, args.proposal)
    elif args.command == "status":
        cmd_status(args.config)


if __name__ == "__main__":
    main()
