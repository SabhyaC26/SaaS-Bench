"""State computation logic for workflow visualization."""

from copy import deepcopy
from typing import Dict

from ..tutorial_processor.workflow_extractor import Workflow


def deep_merge(base: Dict, update: Dict) -> Dict:
    """Deep merge two dictionaries, with update taking precedence.

    Args:
        base: Base dictionary
        update: Dictionary with updates to apply

    Returns:
        Merged dictionary
    """
    result = deepcopy(base)

    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def compute_state_at_step(workflow: Workflow, step_index: int) -> Dict:
    """Compute the state at a specific step index.

    Args:
        workflow: The workflow to compute state for
        step_index: Step index (0 = initial, 1-N = after step N, -1 = goal)

    Returns:
        State dictionary at the specified step
    """
    if step_index == -1:
        # Return goal state
        return deepcopy(workflow.goal_state) if workflow.goal_state else {}

    if step_index == 0:
        # Return initial state
        return deepcopy(workflow.initial_state) if workflow.initial_state else {}

    # Start with initial state
    state = deepcopy(workflow.initial_state) if workflow.initial_state else {}

    # Apply state changes from steps 1 through step_index
    for step in workflow.steps:
        if step.step_id <= step_index:
            if step.expected_state_change:
                state = deep_merge(state, step.expected_state_change)

    return state


def compute_state_before_step(workflow: Workflow, step_id: int) -> Dict:
    """Compute the state before a specific step.

    Args:
        workflow: The workflow to compute state for
        step_id: The step ID to compute state before

    Returns:
        State dictionary before the specified step
    """
    if step_id <= 1:
        return deepcopy(workflow.initial_state) if workflow.initial_state else {}

    # Start with initial state
    state = deepcopy(workflow.initial_state) if workflow.initial_state else {}

    # Apply state changes from steps 1 through step_id - 1
    for step in workflow.steps:
        if step.step_id < step_id:
            if step.expected_state_change:
                state = deep_merge(state, step.expected_state_change)

    return state


def compute_state_after_step(workflow: Workflow, step_id: int) -> Dict:
    """Compute the state after a specific step.

    Args:
        workflow: The workflow to compute state for
        step_id: The step ID to compute state after

    Returns:
        State dictionary after the specified step
    """
    return compute_state_at_step(workflow, step_id)
