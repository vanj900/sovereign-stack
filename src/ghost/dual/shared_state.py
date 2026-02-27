"""
shared_state.py — /dev/shm/ghost_dual/ wrapper + thermo metrics + decay

ALL state lives here. tmpfs only. Reboot = death. That's the deal.
No .pkl. No disk. State rots every pulse — that's not a bug, it's the axiom.
"""

import os
import json
import time
import sys

# Pull the real thermo engine from the existing package
_PKG = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "ai", "thermo-ai", "src"
)
sys.path.insert(0, os.path.abspath(_PKG))

from thermodynamic_agency.core.metabolic_engine import (
    MetabolicEngine,
    EnergyDeathException,
    ThermalDeathException,
    EntropyDeathException,
    MemoryCollapseException,
)

SHM_ROOT = "/dev/shm/ghost_dual"

# ── thermo constants tuned for a 5-60s dual loop ──────────────────────────────
FAST_COST = 1.0    # energy per fast pulse
SLOW_COST = 5.0    # energy per slow cycle (3-5× expensive, just like axiom says)
DECAY_DT = 1.0     # time-step fed to passive_decay every pulse


def ensure_shm() -> None:
    """Blow up if /dev/shm doesn't exist — we only run on tmpfs."""
    os.makedirs(SHM_ROOT, exist_ok=True)
    assert os.path.ismount("/dev/shm") or os.path.exists("/dev/shm"), \
        "/dev/shm not available — not running on a real system?"


def shm_path(filename: str) -> str:
    return os.path.join(SHM_ROOT, filename)


# ── shared dict helpers (works with multiprocessing.Manager.dict) ─────────────

def init_shared(shared: dict) -> None:
    """Seed the shared Manager.dict with clean starting state."""
    shared["E"]         = 100.0
    shared["T"]         = 293.15
    shared["M"]         = 1.0
    shared["S"]         = 1.0
    shared["age"]       = 0.0
    shared["pulse"]     = 0
    shared["mask"]      = "Healer"       # Healer / Judge / Courier
    shared["alive"]     = True
    shared["last_fast"] = 0.0
    shared["last_slow"] = 0.0
    shared["veto"]      = False          # human veto flag
    shared["death_cause"] = None


def apply_decay(shared: dict, engine: MetabolicEngine) -> None:
    """
    Decay → death-check → sync shared state from engine.
    Called every pulse inside both fast and slow loops.
    Raises the right exception if the ghost hits a death condition.
    """
    engine.passive_decay(dt=DECAY_DT)

    # Sync engine state back into shared dict
    st = engine.get_state()
    shared["E"]   = st["energy"]
    shared["T"]   = st["temperature"]
    shared["M"]   = st["memory_integrity"]
    shared["S"]   = st["stability"]
    shared["age"] = st["age"]

    if not engine.is_alive:
        shared["alive"]       = False
        shared["death_cause"] = engine.death_cause
        _raise_death(engine.death_cause)


def charge_fast(shared: dict, engine: MetabolicEngine) -> None:
    """Burn energy for a fast model call; raises on death."""
    try:
        engine.compute(lambda: None, cost=FAST_COST)
    except EnergyDeathException:
        shared["alive"]       = False
        shared["death_cause"] = "energy_death"
        raise
    _sync(shared, engine)


def charge_slow(shared: dict, engine: MetabolicEngine) -> None:
    """Burn energy for a slow model call (3-5× expensive)."""
    try:
        engine.compute(lambda: None, cost=SLOW_COST)
    except (EnergyDeathException, ThermalDeathException,
            EntropyDeathException, MemoryCollapseException):
        shared["alive"]       = False
        shared["death_cause"] = engine.death_cause
        raise
    _sync(shared, engine)


def _sync(shared: dict, engine: MetabolicEngine) -> None:
    st = engine.get_state()
    shared["E"] = st["energy"]
    shared["T"] = st["temperature"]
    shared["M"] = st["memory_integrity"]
    shared["S"] = st["stability"]


def _raise_death(cause: str) -> None:
    if cause == "energy_death":
        raise EnergyDeathException(f"Ghost died: {cause}")
    elif cause == "thermal_death":
        raise ThermalDeathException(f"Ghost died: {cause}")
    elif cause == "entropy_death":
        raise EntropyDeathException(f"Ghost died: {cause}")
    elif cause == "memory_collapse":
        raise MemoryCollapseException(f"Ghost died: {cause}")
    else:
        raise RuntimeError(f"Ghost died: {cause}")


def wipe_shm() -> None:
    """Nuke /dev/shm/ghost_dual/ entirely. Called on death/Ctrl-C."""
    import shutil
    if os.path.exists(SHM_ROOT):
        shutil.rmtree(SHM_ROOT, ignore_errors=True)
