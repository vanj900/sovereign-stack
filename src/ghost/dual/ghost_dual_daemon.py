"""
ghost_dual_daemon.py — main entry point.

Starts fast + slow as separate processes sharing ONE Manager.dict() in RAM.
Runs human veto pipe in main thread.
On death or Ctrl-C: posts final receipt, exports MindSeed, wipes /dev/shm/ghost_dual/.

Usage:
    python ghost_dual_daemon.py [--seed path/to/mindseed.json]
"""

import argparse
import os
import signal
import sys
import time
from multiprocessing import Manager, Process

# Ensure local modules resolve first
sys.path.insert(0, os.path.dirname(__file__))

from shared_state import ensure_shm, init_shared, wipe_shm
from fast_model   import fast_loop
from slow_model   import slow_loop
from receipt_logger import post_receipt
from mindseed import export_mindseed, import_mindseed

_fast_proc: Process | None = None
_slow_proc: Process | None = None
_shared = None          # filled after Manager starts


# ── shutdown ──────────────────────────────────────────────────────────────────

def _shutdown(shared, reason: str = "shutdown") -> None:
    """Orderly death: receipt → MindSeed export → wipe shm."""
    print(f"\n[daemon] shutdown: {reason}")
    shared["alive"] = False

    # Give children 3s to finish their current receipt
    if _fast_proc and _fast_proc.is_alive():
        _fast_proc.join(timeout=3)
        if _fast_proc.is_alive():
            _fast_proc.terminate()

    if _slow_proc and _slow_proc.is_alive():
        _slow_proc.join(timeout=3)
        if _slow_proc.is_alive():
            _slow_proc.terminate()

    # Export MindSeed before wiping
    seed = export_mindseed(shared, notes=f"shutdown:{reason}")
    seed_path = f"/tmp/mindseed_{int(time.time())}.json"
    import json
    with open(seed_path, "w") as f:
        json.dump(seed, f, indent=2)
    print(f"[daemon] MindSeed saved → {seed_path}  (copy before next spawn)")

    post_receipt("daemon_death", {"reason": reason, "seed": seed_path})

    # Death mode: wipe all state from shm
    wipe_shm()
    print("[daemon] /dev/shm/ghost_dual/ wiped. Ghost is dead. Fork from MindSeed.")


def _sig_handler(signum, frame):
    if _shared is not None:
        _shutdown(_shared, reason="signal")
    sys.exit(0)


# ── human veto pipe ───────────────────────────────────────────────────────────

def _veto_prompt(shared: dict) -> None:
    """
    Blocking input loop in main thread.
    'v' → set veto flag (highest priority).
    'q' → kill ghost.
    's' → print current state.
    'x' → export MindSeed.
    """
    print("[daemon] Human veto pipe active. Commands: [v]eto  [q]uit  [s]tatus  [x] export-seed")
    while shared.get("alive", True):
        try:
            cmd = input("ghost> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            _shutdown(shared, reason="ctrl-c")
            sys.exit(0)

        if cmd == "v":
            shared["veto"] = True
            post_receipt("human_veto", {"cmd": cmd}, veto=True)
            print("[VETO] flag set — Judge mask will activate on next fast pulse")

        elif cmd == "q":
            _shutdown(shared, reason="human_quit")
            sys.exit(0)

        elif cmd == "s":
            print(
                f"  E={shared.get('E',0):.2f}  T={shared.get('T',0):.2f}K  "
                f"M={shared.get('M',0):.3f}  S={shared.get('S',0):.3f}  "
                f"pulse={shared.get('pulse',0)}  mask={shared.get('mask','?')}  "
                f"alive={shared.get('alive',False)}"
            )

        elif cmd == "x":
            seed = export_mindseed(shared, notes="manual export")
            print(f"  seed written to /dev/shm/ghost_dual/mindseed.json")

        elif cmd == "":
            pass

        else:
            print("  unknown command — [v]eto  [q]uit  [s]tatus  [x]export")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    global _fast_proc, _slow_proc, _shared

    parser = argparse.ArgumentParser(description="Ghost Dual Daemon")
    parser.add_argument(
        "--seed", default=None,
        help="Path to a MindSeed JSON file to import on startup"
    )
    args = parser.parse_args()

    ensure_shm()
    signal.signal(signal.SIGTERM, _sig_handler)
    signal.signal(signal.SIGINT,  _sig_handler)

    with Manager() as mgr:
        shared = mgr.dict()
        _shared = shared
        init_shared(shared)

        # Import MindSeed if provided
        if args.seed:
            if import_mindseed(args.seed, shared):
                print(f"[daemon] MindSeed loaded from {args.seed}")
            else:
                print(f"[daemon] MindSeed load failed — starting fresh")

        post_receipt("daemon_start", {
            "fast_model": os.environ.get("GHOST_FAST_MODEL", "phi3:mini"),
            "slow_model": os.environ.get("GHOST_SLOW_MODEL", "llama3.2:3b"),
            "seed":       args.seed,
        })

        # Start processes
        _fast_proc = Process(target=fast_loop, args=(shared,), name="ghost-fast", daemon=True)
        _slow_proc = Process(target=slow_loop, args=(shared,), name="ghost-slow", daemon=True)
        _fast_proc.start()
        _slow_proc.start()

        print(f"[daemon] 🔥 fast pid={_fast_proc.pid}  slow pid={_slow_proc.pid}")

        try:
            _veto_prompt(shared)
        except SystemExit:
            pass
        finally:
            if shared.get("alive", True):
                _shutdown(shared, reason="main_exit")


if __name__ == "__main__":
    main()
