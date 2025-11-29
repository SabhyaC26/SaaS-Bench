#!/usr/bin/env python3
"""Validate workflow YAML files."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from saas_bench.utils.yaml_loader import load_all_workflows, load_workflow


def validate_workflow(
    workflow_path: str, validate_states: bool = True
) -> tuple[bool, str]:
    """Validate a single workflow file.

    Args:
        workflow_path: Path to workflow YAML file
        validate_states: If True, validate initial_state and goal_state against DatabricksState schema
    """
    try:
        workflow = load_workflow(workflow_path, validate_states=validate_states)
        state_info = " (including state validation)" if validate_states else ""
        return True, f"✓ Valid: {workflow.title}{state_info}"
    except Exception as e:
        return False, f"✗ Invalid: {e}"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate workflow YAML files")
    parser.add_argument(
        "workflows",
        nargs="*",
        help="Specific workflow files to validate (if not provided, validates all in workflows/databricks)",
    )
    parser.add_argument(
        "--directory",
        default="workflows/databricks",
        help="Directory containing workflow files (default: workflows/databricks)",
    )
    parser.add_argument(
        "--skip-state-validation",
        action="store_true",
        help="Skip validation of initial_state and goal_state against DatabricksState schema",
    )

    args = parser.parse_args()

    if args.workflows:
        # Validate specific files
        workflows_to_validate = args.workflows
    else:
        # Validate all workflows in directory
        workflow_dir = Path(args.directory)
        if not workflow_dir.exists():
            print(f"Directory not found: {args.directory}")
            sys.exit(1)
        workflows_to_validate = [str(f) for f in workflow_dir.glob("*.yaml")]

    if not workflows_to_validate:
        print("No workflows found to validate")
        sys.exit(0)

    print(f"Validating {len(workflows_to_validate)} workflow(s)...\n")

    valid_count = 0
    invalid_count = 0

    for workflow_path in workflows_to_validate:
        is_valid, message = validate_workflow(
            workflow_path, validate_states=not args.skip_state_validation
        )
        print(f"{workflow_path}: {message}")
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1

    print(f"\nValidation complete: {valid_count} valid, {invalid_count} invalid")
    sys.exit(0 if invalid_count == 0 else 1)


if __name__ == "__main__":
    main()
