"""Core active-inference decision loop — EFE minimisation."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .perception_action import Action, ACTION_REGISTRY, PerceptionAction
from .predictive_model import PredictiveModel
from ..core.failure_modes import MetabolicFailure

if TYPE_CHECKING:
    from ..cognition.goal_manager import GoalManager
    from ..cognition.identity_persistence import IdentityPersistence
    from ..core.metabolic_engine import MetabolicEngine
    from ..environment.resource_world import ResourceWorld


def compute_efe(
    action: Action, prediction: dict[str, Any], dt: float = 1.0
) -> float:
    """Compute Expected Free Energy for one action candidate.

    EFE = Pragmatic_Value + Epistemic_Value - Action_Cost

    Lower EFE → preferred action.  We negate the standard formulation so
    that *min EFE = best action*.

    Returns a *negative* number; the action with the highest absolute value
    is the least costly option in free-energy terms.
    """
    pragmatic = prediction["survival_prob"]         # [0, 1] — higher is better
    epistemic = prediction["information_gain"]       # [0, 1]
    cost = action.thermodynamic_cost                 # raw energy units

    # Normalise cost to [0, 1] using a soft cap of 10 energy units
    cost_norm = min(1.0, cost / 10.0)

    return pragmatic + epistemic - cost_norm


def active_inference_step(
    engine: "MetabolicEngine",
    goal_manager: "GoalManager",
    predictive_model: "PredictiveModel",
    perception_action: "PerceptionAction",
    identity: "IdentityPersistence",
    resource_world: "ResourceWorld | None" = None,
    dt: float = 1.0,
) -> bool:
    """Execute one full active-inference cycle.

    Steps
    -----
    1. Perceive current state.
    2. Generate candidate actions from goal drives.
    3. Score each action by EFE.
    4. Execute the action with the highest EFE score.
    5. Update predictive model from actual outcome.
    6. Record event in identity narrative.
    7. Apply passive decay.

    Returns
    -------
    bool
        True if the agent is still alive after this step.
    """
    # 1. Perceive
    observations = perception_action.perceive()

    # 2. Generate candidate actions ordered by drive urgency
    action_names = goal_manager.generate_actions()
    name_to_action = {a.name: a for a in perception_action.available_actions()}
    actions = [name_to_action[n] for n in action_names if n in name_to_action]
    if not actions:
        actions = perception_action.available_actions()

    # 3. Compute EFE for each action
    efe_scores: dict[int, float] = {}
    predictions: dict[int, dict[str, Any]] = {}
    for i, action in enumerate(actions):
        prediction = predictive_model.predict_outcome(action)
        predictions[i] = prediction
        efe_scores[i] = compute_efe(action, prediction, dt)

    # 4. Select action with highest EFE (max = best survival + info - cost)
    best_idx = max(efe_scores, key=lambda k: efe_scores[k])
    chosen_action = actions[best_idx]
    chosen_prediction = predictions[best_idx]

    # 5. Execute and observe outcome
    try:
        outcome = perception_action.execute(chosen_action, resource_world)
        survived_action = True
    except MetabolicFailure:  # expected thermodynamic failure during action
        outcome = engine.snapshot()
        survived_action = False

    # 6. Update beliefs
    predictive_model.update_beliefs(outcome)

    # 7. Record event
    emotional_weight = 1.0 - chosen_prediction["survival_prob"]
    event_description = (
        f"Action '{chosen_action.name}': "
        f"E={outcome.get('energy', 0):.1f}, "
        f"T={outcome.get('temperature', 0):.1f}K, "
        f"M={outcome.get('memory_integrity', 0):.3f}, "
        f"S={outcome.get('stability', 0):.3f}"
    )
    identity.record_event(event_description, emotional_weight)

    # 8. Passive decay
    try:
        engine.passive_decay(dt)
    except MetabolicFailure:
        pass

    return engine.alive
