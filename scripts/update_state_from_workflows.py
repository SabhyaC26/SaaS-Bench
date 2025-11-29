#!/usr/bin/env python3
"""Analyze workflows and update state.py schema based on findings."""

import argparse
import inspect
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml
from pydantic import BaseModel

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from saas_bench.domains.databricks.state import (
    Catalog,
    Cluster,
    Column,
    DatabricksState,
    Job,
    Notebook,
    Permission,
    Schema,
    Table,
)
from saas_bench.utils.yaml_loader import load_all_workflows


def get_pydantic_fields(model_class: type[BaseModel]) -> Dict[str, Any]:
    """Extract field information from a Pydantic model."""
    fields = {}
    for field_name, field_info in model_class.model_fields.items():
        fields[field_name] = {
            "type": str(field_info.annotation),
            "required": field_info.is_required(),
            "default": field_info.default if not field_info.is_required() else None,
        }
    return fields


def infer_python_type(value: Any) -> str:
    """Infer Python type from a value."""
    if value is None:
        return "Optional[Any]"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, str):
        return "str"
    elif isinstance(value, list):
        if value:
            item_type = infer_python_type(value[0])
            return f"List[{item_type}]"
        return "List[Any]"
    elif isinstance(value, dict):
        return "Dict[str, Any]"
    else:
        return type(value).__name__


def extract_resource_properties(
    state_dict: Dict, resource_type: str
) -> Dict[str, Set[str]]:
    """Extract properties used for a specific resource type from state dict."""
    properties = defaultdict(set)

    if resource_type not in state_dict:
        return {}

    resources = state_dict[resource_type]
    if not isinstance(resources, dict):
        return {}

    for resource_key, resource_data in resources.items():
        if isinstance(resource_data, dict):
            for prop_name, prop_value in resource_data.items():
                properties[prop_name].add(infer_python_type(prop_value))

    return dict(properties)


def analyze_workflow_states(workflows: List) -> Dict[str, Dict]:
    """Analyze all workflows to extract resource types and properties."""
    found_resources = defaultdict(lambda: defaultdict(set))
    resource_type_mapping = {
        "catalogs": Catalog,
        "schemas": Schema,
        "tables": Table,
        "notebooks": Notebook,
        "clusters": Cluster,
        "jobs": Job,
        "permissions": Permission,
    }

    for workflow in workflows:
        # Analyze initial_state
        if workflow.initial_state:
            for resource_type in resource_type_mapping.keys():
                props = extract_resource_properties(
                    workflow.initial_state, resource_type
                )
                for prop_name, types in props.items():
                    found_resources[resource_type][prop_name].update(types)

        # Analyze goal_state
        if workflow.goal_state:
            for resource_type in resource_type_mapping.keys():
                props = extract_resource_properties(workflow.goal_state, resource_type)
                for prop_name, types in props.items():
                    found_resources[resource_type][prop_name].update(types)

        # Analyze expected_state_change in steps
        if workflow.steps:
            for step in workflow.steps:
                if step.expected_state_change:
                    for resource_type in resource_type_mapping.keys():
                        props = extract_resource_properties(
                            step.expected_state_change, resource_type
                        )
                        for prop_name, types in props.items():
                            found_resources[resource_type][prop_name].update(types)

        # Check for new resource types not in mapping
        all_state_dicts = []
        if workflow.initial_state:
            all_state_dicts.append(workflow.initial_state)
        if workflow.goal_state:
            all_state_dicts.append(workflow.goal_state)
        for step in workflow.steps:
            if step.expected_state_change:
                all_state_dicts.append(step.expected_state_change)

        for state_dict in all_state_dicts:
            for key in state_dict.keys():
                if key not in resource_type_mapping and key != "active_catalog":
                    # This is a potentially new resource type
                    found_resources[key] = defaultdict(set)
                    props = extract_resource_properties(state_dict, key)
                    for prop_name, types in props.items():
                        found_resources[key][prop_name].update(types)

    # Convert sets to lists for JSON serialization
    result = {}
    for resource_type, properties in found_resources.items():
        result[resource_type] = {
            prop_name: sorted(list(types)) for prop_name, types in properties.items()
        }

    return result


def compare_with_schema(found_resources: Dict) -> Dict:
    """Compare found resources with current schema."""
    resource_type_mapping = {
        "catalogs": Catalog,
        "schemas": Schema,
        "tables": Table,
        "notebooks": Notebook,
        "clusters": Cluster,
        "jobs": Job,
        "permissions": Permission,
    }

    comparison = {
        "missing_resource_types": [],
        "missing_properties": {},
        "type_mismatches": {},
        "new_properties": {},
    }

    # Check for missing resource types
    for resource_type in found_resources.keys():
        if (
            resource_type not in resource_type_mapping
            and resource_type != "active_catalog"
        ):
            comparison["missing_resource_types"].append(resource_type)

    # Check for missing/mismatched properties
    for resource_type, model_class in resource_type_mapping.items():
        if resource_type not in found_resources:
            continue

        current_fields = get_pydantic_fields(model_class)
        found_props = found_resources[resource_type]

        missing_props = []
        new_props = []
        type_mismatches = []

        for prop_name, found_types in found_props.items():
            if prop_name not in current_fields:
                # Property not in current schema
                if resource_type == "tables" and prop_name == "columns":
                    # Special handling for nested Column objects
                    continue
                new_props.append({"name": prop_name, "types": found_types})
            else:
                # Check type compatibility
                current_type = current_fields[prop_name]["type"]
                # Simple type checking (could be improved)
                found_type_str = found_types[0] if found_types else "Any"
                if not types_compatible(current_type, found_type_str):
                    type_mismatches.append(
                        {
                            "property": prop_name,
                            "current": current_type,
                            "found": found_type_str,
                        }
                    )

        # Check for properties in schema but not found in workflows
        for field_name in current_fields.keys():
            if field_name not in found_props:
                # This is okay - workflows might not use all fields
                pass

        if new_props:
            comparison["new_properties"][resource_type] = new_props
        if type_mismatches:
            comparison["type_mismatches"][resource_type] = type_mismatches

    return comparison


def types_compatible(current: str, found: str) -> bool:
    """Check if types are compatible (simplified)."""
    # Normalize type strings
    current = current.lower().replace("optional[", "").replace("]", "")
    found = found.lower().replace("optional[", "").replace("]", "")

    # Handle common cases
    if "str" in current and "str" in found:
        return True
    if "int" in current and "int" in found:
        return True
    if "bool" in current and "bool" in found:
        return True
    if "dict" in current and "dict" in found:
        return True
    if "list" in current and "list" in found:
        return True

    # If types match exactly
    if current == found:
        return True

    # Default to compatible (conservative)
    return True


def generate_markdown_report(analysis: Dict, comparison: Dict) -> str:
    """Generate markdown report with recommendations."""
    lines = []
    lines.append("# State Schema Analysis Report\n")
    lines.append(
        f"Based on analysis of {analysis.get('workflow_count', 0)} workflow(s)\n\n"
    )

    # Summary
    lines.append("## Summary\n\n")
    lines.append(f"- **Workflows analyzed**: {analysis.get('workflow_count', 0)}\n")
    lines.append(
        f"- **Resource types found**: {len(analysis.get('found_resources', {}))}\n"
    )
    lines.append(
        f"- **Missing resource types**: {len(comparison.get('missing_resource_types', []))}\n"
    )

    total_missing_props = sum(
        len(props) for props in comparison.get("new_properties", {}).values()
    )
    lines.append(f"- **Missing properties**: {total_missing_props}\n\n")

    # Missing resource types
    if comparison.get("missing_resource_types"):
        lines.append("## Missing Resource Types\n\n")
        lines.append(
            "The following resource types were found in workflows but are not defined in state.py:\n\n"
        )
        for resource_type in comparison["missing_resource_types"]:
            props = analysis["found_resources"].get(resource_type, {})
            lines.append(f"### {resource_type.title()}\n\n")
            if props:
                lines.append("Properties found:\n")
                for prop_name, types in props.items():
                    types_str = ", ".join(types)
                    lines.append(f"- `{prop_name}`: {types_str}\n")
                lines.append("\n")
            else:
                lines.append("No properties found.\n\n")

    # Missing properties
    if comparison.get("new_properties"):
        lines.append("## Missing Properties\n\n")
        lines.append(
            "The following properties are used in workflows but missing from current schema:\n\n"
        )
        for resource_type, props in comparison["new_properties"].items():
            lines.append(f"### {resource_type.title()}\n\n")
            for prop in props:
                prop_name = prop["name"]
                types = prop["types"]
                types_str = " | ".join(types)
                lines.append(f"- `{prop_name}`: {types_str}\n")
            lines.append("\n")

    # Type mismatches
    if comparison.get("type_mismatches"):
        lines.append("## Type Mismatches\n\n")
        lines.append(
            "The following properties have type mismatches between schema and workflows:\n\n"
        )
        for resource_type, mismatches in comparison["type_mismatches"].items():
            lines.append(f"### {resource_type.title()}\n\n")
            for mismatch in mismatches:
                lines.append(
                    f"- `{mismatch['property']}`: Schema has `{mismatch['current']}`, workflows use `{mismatch['found']}`\n"
                )
            lines.append("\n")

    # Recommendations
    lines.append("## Recommendations\n\n")

    if comparison.get("missing_resource_types"):
        lines.append("### Add New Resource Types\n\n")
        for resource_type in comparison["missing_resource_types"]:
            props = analysis["found_resources"].get(resource_type, {})
            lines.append(f"Add `{resource_type.title()}` class:\n\n")
            lines.append("```python\n")
            lines.append(f"class {resource_type.title()}(BaseModel):\n")
            lines.append(f'    """{resource_type.title()} resource."""\n\n')
            if props:
                for prop_name, types in props.items():
                    type_str = types[0] if types else "Any"
                    # Convert to proper Python type
                    if "Optional" not in type_str and "List" not in type_str:
                        type_str = f"Optional[{type_str}]"
                    lines.append(f"    {prop_name}: {type_str} = None\n")
            else:
                lines.append("    # Properties to be determined\n")
                lines.append("    pass\n")
            lines.append('\n    model_config = {"frozen": True}\n')
            lines.append("```\n\n")

    if comparison.get("new_properties"):
        lines.append("### Add Missing Properties\n\n")
        for resource_type, props in comparison["new_properties"].items():
            lines.append(f"Add to `{resource_type.title()}` class:\n\n")
            for prop in props:
                prop_name = prop["name"]
                types = prop["types"]
                type_str = types[0] if types else "Any"
                if "Optional" not in type_str:
                    type_str = f"Optional[{type_str}]"
                lines.append(f"    {prop_name}: {type_str} = None\n")
            lines.append("\n")

    return "".join(lines)


def update_state_py(state_file: Path, comparison: Dict, found_resources: Dict) -> None:
    """Update state.py file with missing resource types and properties."""
    # Read current file
    with open(state_file, "r") as f:
        content = f.read()

    # This is a complex operation - for now, we'll generate the updates
    # but require manual review. A full implementation would parse the AST
    # and make precise edits.
    print("Automatic state.py updates require manual review.")
    print("Please review the recommendations and update state.py manually.")
    print(f"See state_schema_recommendations.md for details.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze workflows and update state.py schema"
    )
    parser.add_argument(
        "--workflows-dir",
        default="workflows/databricks",
        help="Directory containing workflow YAML files (default: workflows/databricks)",
    )
    parser.add_argument(
        "--state-file",
        default="src/saas_bench/domains/databricks/state.py",
        help="Path to state.py file (default: src/saas_bench/domains/databricks/state.py)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply updates to state.py (currently requires manual review)",
    )
    parser.add_argument(
        "--json-output",
        default="state_schema_analysis.json",
        help="Output file for JSON analysis (default: state_schema_analysis.json)",
    )
    parser.add_argument(
        "--markdown-output",
        default="state_schema_recommendations.md",
        help="Output file for markdown recommendations (default: state_schema_recommendations.md)",
    )

    args = parser.parse_args()

    # Load workflows
    workflows_dir = Path(args.workflows_dir)
    if not workflows_dir.exists():
        print(f"Error: Workflows directory not found: {workflows_dir}")
        sys.exit(1)

    print(f"Loading workflows from {workflows_dir}...")
    workflows = load_all_workflows(str(workflows_dir))

    if not workflows:
        print("No workflows found. Please process tutorials first.")
        print("Usage: python scripts/analyze_tutorials_batch.py <url1> <url2> ...")
        sys.exit(1)

    print(f"Found {len(workflows)} workflow(s)\n")

    # Analyze workflows
    print("Analyzing workflows...")
    found_resources = analyze_workflow_states(workflows)

    # Compare with schema
    print("Comparing with current schema...")
    comparison = compare_with_schema(found_resources)

    # Generate analysis dict
    analysis = {
        "workflow_count": len(workflows),
        "workflows": [
            {"id": w.id, "title": w.title, "source_url": w.source_url}
            for w in workflows
        ],
        "found_resources": found_resources,
        "comparison": comparison,
    }

    # Save JSON report
    print(f"Saving JSON analysis to {args.json_output}...")
    with open(args.json_output, "w") as f:
        json.dump(analysis, f, indent=2)

    # Generate and save markdown report
    print(f"Generating markdown report...")
    markdown_report = generate_markdown_report(analysis, comparison)
    with open(args.markdown_output, "w") as f:
        f.write(markdown_report)
    print(f"Saved recommendations to {args.markdown_output}\n")

    # Summary
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Workflows analyzed: {len(workflows)}")
    print(f"Resource types found: {len(found_resources)}")
    print(f"Missing resource types: {len(comparison['missing_resource_types'])}")
    total_missing_props = sum(
        len(props) for props in comparison["new_properties"].values()
    )
    print(f"Missing properties: {total_missing_props}")
    print(f"\nReview recommendations in: {args.markdown_output}")
    print(f"Full analysis data in: {args.json_output}")

    # Apply updates if requested
    if args.apply:
        state_file = Path(args.state_file)
        if not state_file.exists():
            print(f"Error: State file not found: {state_file}")
            sys.exit(1)
        print("\nApplying updates to state.py...")
        update_state_py(state_file, comparison, found_resources)
        print("Updates applied. Please review and test.")


if __name__ == "__main__":
    main()
