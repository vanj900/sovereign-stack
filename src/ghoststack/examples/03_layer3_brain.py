"""
Layer 3 (Optional): Brain Simulation
======================================
A lightweight cognitive-loop prototype demonstrating stimulus processing,
emotional modulation, decision-making, episodic memory, and dopamine dynamics.

Components:
  - SensoryProcessor  : converts raw stimuli into normalised feature vectors
  - LimbicSystem      : tracks valence/arousal, dopamine level, applies decay
  - FrontalLobe       : picks an action from a softmax over weighted options
  - Hippocampus       : stores and retrieves episodic memories
  - BrainSimulation   : orchestrates one full cognitive cycle per step
  - persistence       : saves/loads state to JSON so runs can learn over time

Run:
    python 03_layer3_brain.py

Expected output (values vary each run):
    [brain] cycle 1  stimulus=visual   emotion=(valence=0.62, arousal=0.55)  action=explore   dopamine=0.72
    [brain] cycle 2  stimulus=auditory emotion=(valence=0.48, arousal=0.61)  action=wait      dopamine=0.64
    ...
    [memory] stored 5 episodes
    [persist] state saved to /tmp/ghoststack_brain_state.json
    [plot]   saved emotion trajectory → /tmp/ghoststack_brain_plot.png  (if matplotlib available)
"""

import json
import math
import os
import random
import time


# ---------------------------------------------------------------------------
# SensoryProcessor
# ---------------------------------------------------------------------------

class SensoryProcessor:
    """
    Transforms raw stimulus descriptors into normalised feature vectors.

    Each modality (visual / auditory) produces a 2-element vector:
      [intensity, novelty]  both in [0, 1].
    """

    def process(self, stimulus_type: str, intensity: float, novelty: float) -> dict:
        intensity = max(0.0, min(1.0, intensity))
        novelty = max(0.0, min(1.0, novelty))
        return {
            "type": stimulus_type,
            "intensity": round(intensity, 3),
            "novelty": round(novelty, 3),
        }


# ---------------------------------------------------------------------------
# LimbicSystem
# ---------------------------------------------------------------------------

class LimbicSystem:
    """
    Simulates the emotional core of the agent.

    State:
      valence  – pleasure (0=negative, 1=positive)
      arousal  – activation level (0=calm, 1=excited)
      dopamine – current dopamine level driving reward learning
    """

    DECAY = 0.1   # per-cycle decay toward neutral (0.5 valence, 0.3 arousal)

    def __init__(self):
        self.valence: float = 0.5
        self.arousal: float = 0.3
        self.dopamine: float = 0.5

    def update(self, features: dict) -> None:
        """Adjust emotional state based on incoming sensory features."""
        intensity = features.get("intensity", 0.5)
        novelty = features.get("novelty", 0.5)

        # Positive novelty boosts valence; high intensity raises arousal
        self.valence = (
            self.valence * (1 - self.DECAY)
            + (0.5 + 0.3 * novelty) * self.DECAY
        )
        self.arousal = (
            self.arousal * (1 - self.DECAY)
            + intensity * self.DECAY
        )
        self.valence = round(max(0.0, min(1.0, self.valence)), 3)
        self.arousal = round(max(0.0, min(1.0, self.arousal)), 3)

    def compute_dopamine(self, reward: float, predicted_reward: float) -> float:
        """
        Reward-prediction-error (RPE) model:
          dopamine ∝ (actual_reward − predicted_reward) + novelty_bonus
        """
        rpe = reward - predicted_reward
        self.dopamine = round(max(0.0, min(1.0, self.dopamine + 0.2 * rpe)), 3)
        return self.dopamine

    def state_dict(self) -> dict:
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "dopamine": self.dopamine,
        }


# ---------------------------------------------------------------------------
# FrontalLobe
# ---------------------------------------------------------------------------

class FrontalLobe:
    """
    Decision-making module.

    Given a list of candidate actions, computes a softmax score weighted by
    emotional state and returns the chosen action.
    """

    ACTIONS = ["explore", "wait", "signal", "conserve"]

    def decide(self, limbic_state: dict) -> str:
        """Return an action string based on current emotional state."""
        valence = limbic_state.get("valence", 0.5)
        arousal = limbic_state.get("arousal", 0.3)
        dopamine = limbic_state.get("dopamine", 0.5)

        # Simple heuristic weights (replace with learned policy in production)
        scores = {
            "explore":  valence * dopamine + arousal,
            "wait":     (1 - arousal) * 0.8,
            "signal":   arousal * dopamine,
            "conserve": (1 - valence) * (1 - dopamine),
        }

        # Softmax
        exp_scores = {a: math.exp(s * 3) for a, s in scores.items()}
        total = sum(exp_scores.values())
        probs = {a: v / total for a, v in exp_scores.items()}

        # Sample from distribution
        r = random.random()
        cumulative = 0.0
        chosen = self.ACTIONS[-1]
        for action, prob in probs.items():
            cumulative += prob
            if r <= cumulative:
                chosen = action
                break
        return chosen


# ---------------------------------------------------------------------------
# Hippocampus
# ---------------------------------------------------------------------------

class Hippocampus:
    """
    Episodic memory store.

    Each episode records: cycle number, stimulus type, emotional snapshot, and
    action taken.  Episodes are stored in insertion order and can be persisted
    to disk.
    """

    def __init__(self, max_episodes: int = 1000):
        self._episodes: list = []
        self._max = max_episodes

    def store(self, cycle: int, stimulus_type: str, emotional_state: dict, action: str) -> None:
        episode = {
            "cycle": cycle,
            "stimulus": stimulus_type,
            "emotion": emotional_state,
            "action": action,
            "ts": int(time.time()),
        }
        self._episodes.append(episode)
        if len(self._episodes) > self._max:
            self._episodes.pop(0)

    def recent(self, n: int = 5) -> list:
        return self._episodes[-n:]

    def to_list(self) -> list:
        return list(self._episodes)

    def load_from_list(self, episodes: list) -> None:
        self._episodes = episodes[: self._max]


# ---------------------------------------------------------------------------
# BrainSimulation
# ---------------------------------------------------------------------------

STIMULI = [
    ("visual", 0.8, 0.9),
    ("auditory", 0.5, 0.4),
    ("visual", 0.3, 0.2),
    ("auditory", 0.7, 0.8),
    ("visual", 0.6, 0.5),
]


class BrainSimulation:
    """
    Orchestrates one full cognitive cycle per call to ``step()``.

    Cycle:
      1. Receive stimulus → SensoryProcessor
      2. Update emotions  → LimbicSystem
      3. Compute dopamine (RPE + novelty)
      4. Choose action    → FrontalLobe
      5. Store episode    → Hippocampus
    """

    STATE_PATH = "/tmp/ghoststack_brain_state.json"

    def __init__(self):
        self.sensory = SensoryProcessor()
        self.limbic = LimbicSystem()
        self.frontal = FrontalLobe()
        self.hippocampus = Hippocampus()
        self._cycle = 0
        self._predicted_reward = 0.5   # naive starting prediction

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def step(self, stimulus_type: str, intensity: float, novelty: float) -> dict:
        """Run one cognitive cycle and return a summary dict."""
        self._cycle += 1

        # 1. Sensory processing
        features = self.sensory.process(stimulus_type, intensity, novelty)

        # 2. Emotional update
        self.limbic.update(features)

        # 3. Dopamine: reward = valence (simplified), plus novelty bonus
        reward = self.limbic.valence + 0.1 * novelty
        dopamine = self.limbic.compute_dopamine(reward, self._predicted_reward)
        # Update prediction with exponential moving average
        self._predicted_reward = 0.9 * self._predicted_reward + 0.1 * reward

        # 4. Decision
        action = self.frontal.decide(self.limbic.state_dict())

        # 5. Store episode
        self.hippocampus.store(
            self._cycle, stimulus_type, self.limbic.state_dict(), action
        )

        summary = {
            "cycle": self._cycle,
            "stimulus": stimulus_type,
            "emotion": self.limbic.state_dict(),
            "action": action,
            "dopamine": dopamine,
        }
        _print_cycle(summary)
        return summary

    def save_state(self, path: str = None) -> str:
        """Persist brain state to a JSON file."""
        path = path or self.STATE_PATH
        state = {
            "cycle": self._cycle,
            "limbic": self.limbic.state_dict(),
            "predicted_reward": self._predicted_reward,
            "episodes": self.hippocampus.to_list(),
        }
        with open(path, "w") as f:
            json.dump(state, f, indent=2)
        print(f"[persist] state saved to {path}")
        return path

    def load_state(self, path: str = None) -> bool:
        """Restore brain state from a JSON file; returns True on success."""
        path = path or self.STATE_PATH
        if not os.path.exists(path):
            return False
        with open(path) as f:
            state = json.load(f)
        self._cycle = state.get("cycle", 0)
        limbic = state.get("limbic", {})
        self.limbic.valence = limbic.get("valence", 0.5)
        self.limbic.arousal = limbic.get("arousal", 0.3)
        self.limbic.dopamine = limbic.get("dopamine", 0.5)
        self._predicted_reward = state.get("predicted_reward", 0.5)
        self.hippocampus.load_from_list(state.get("episodes", []))
        print(f"[persist] state loaded from {path} (cycle={self._cycle})")
        return True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_cycle(summary: dict) -> None:
    e = summary["emotion"]
    print(
        f"[brain] cycle {summary['cycle']:<3} "
        f"stimulus={summary['stimulus']:<8} "
        f"emotion=(valence={e['valence']}, arousal={e['arousal']})  "
        f"action={summary['action']:<8} "
        f"dopamine={summary['dopamine']}"
    )


def _try_plot(history: list) -> None:
    """Attempt to draw an emotion/dopamine trajectory plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt  # noqa: PLC0415

        cycles = [h["cycle"] for h in history]
        valences = [h["emotion"]["valence"] for h in history]
        arousals = [h["emotion"]["arousal"] for h in history]
        dopamines = [h["dopamine"] for h in history]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
        ax1.plot(cycles, valences, label="valence", marker="o")
        ax1.plot(cycles, arousals, label="arousal", marker="s")
        ax1.set_ylabel("Emotional state")
        ax1.legend()
        ax1.set_ylim(0, 1)
        ax2.plot(cycles, dopamines, label="dopamine", color="orange", marker="^")
        ax2.set_ylabel("Dopamine")
        ax2.set_xlabel("Cycle")
        ax2.legend()
        ax2.set_ylim(0, 1)
        fig.tight_layout()

        plot_path = "/tmp/ghoststack_brain_plot.png"
        plt.savefig(plot_path)
        plt.close(fig)
        print(f"[plot]   saved emotion trajectory → {plot_path}")
    except ImportError:
        print("[plot]   matplotlib not installed — skipping plot generation")


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

def main() -> None:
    brain = BrainSimulation()

    # Load prior state if available (enables multi-run learning)
    brain.load_state()

    history = []
    for stim_type, intensity, novelty in STIMULI:
        result = brain.step(stim_type, intensity, novelty)
        history.append(result)

    print(f"[memory] stored {len(brain.hippocampus.to_list())} episodes")
    brain.save_state()
    _try_plot(history)


if __name__ == "__main__":
    main()
