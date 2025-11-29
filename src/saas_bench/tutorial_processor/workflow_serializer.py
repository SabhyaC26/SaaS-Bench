"""Serialize workflows to YAML format."""

import os
from pathlib import Path

import yaml

from .workflow_extractor import Workflow


def serialize_to_yaml(workflow: Workflow, output_path: str):
    """Convert workflow object to YAML format and save to file."""
    # Convert Pydantic model to dict
    workflow_dict = workflow.model_dump()

    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write YAML file
    with open(output_path, "w") as f:
        yaml.dump(workflow_dict, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return output_path


def generate_workflow_filename(workflow: Workflow, output_dir: str = "workflows/databricks") -> str:
    """Generate filename for workflow based on its ID."""
    filename = f"{workflow.id}.yaml"
    return os.path.join(output_dir, filename)

