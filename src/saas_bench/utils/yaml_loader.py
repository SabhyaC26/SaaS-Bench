"""YAML workflow loader utility."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from ..domains.databricks.state import DatabricksState
from ..tutorial_processor.workflow_extractor import Workflow


def validate_state_dict(
    state_dict: dict, state_name: str = "state"
) -> tuple[bool, str]:
    """Validate that a state dictionary conforms to DatabricksState schema."""
    if not isinstance(state_dict, dict):
        return False, f"{state_name} must be a dictionary"

    try:
        # Try to create DatabricksState from the dict
        DatabricksState(**state_dict)
        return True, ""
    except ValidationError as e:
        return False, f"Invalid {state_name} schema: {e}"
    except Exception as e:
        return False, f"Error validating {state_name}: {e}"


def load_workflow(path: str, validate_states: bool = True) -> Workflow:
    """Load and parse a workflow YAML file into a Pydantic model.

    Args:
        path: Path to workflow YAML file
        validate_states: If True, validate initial_state and goal_state against DatabricksState schema

    Returns:
        Workflow object

    Raises:
        ValueError: If workflow schema is invalid or state validation fails
    """
    workflow_path = Path(path)

    if not workflow_path.exists():
        raise FileNotFoundError(f"Workflow file not found: {path}")

    with open(workflow_path, "r") as f:
        workflow_dict = yaml.safe_load(f)

    try:
        workflow = Workflow(**workflow_dict)
    except ValidationError as e:
        raise ValueError(f"Invalid workflow schema: {e}")

    # Validate state dictionaries if requested
    if validate_states:
        if workflow.initial_state:
            is_valid, error_msg = validate_state_dict(
                workflow.initial_state, "initial_state"
            )
            if not is_valid:
                raise ValueError(f"Invalid initial_state: {error_msg}")

        if workflow.goal_state:
            is_valid, error_msg = validate_state_dict(workflow.goal_state, "goal_state")
            if not is_valid:
                raise ValueError(f"Invalid goal_state: {error_msg}")

    return workflow


def load_all_workflows(directory: str = "workflows/databricks") -> list[Workflow]:
    """Load all workflow YAML files from a directory."""
    workflows = []
    workflow_dir = Path(directory)

    if not workflow_dir.exists():
        return workflows

    for yaml_file in workflow_dir.glob("*.yaml"):
        try:
            workflow = load_workflow(str(yaml_file))
            workflows.append(workflow)
        except Exception as e:
            print(f"Error loading {yaml_file}: {e}")

    return workflows
