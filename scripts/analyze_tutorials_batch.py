#!/usr/bin/env python3
"""Analyze multiple tutorials and identify all resource types needed for comprehensive schema."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from saas_bench.domains.databricks.registry import TOOL_REGISTRY
from saas_bench.tutorial_processor.scraper import scrape_tutorial
from saas_bench.tutorial_processor.workflow_extractor import extract_workflow
from saas_bench.tutorial_processor.workflow_serializer import (
    generate_workflow_filename,
    serialize_to_yaml,
)


def analyze_resource_types(workflow_dict: Dict) -> Dict[str, Set[str]]:
    """Extract resource types and their properties from a workflow."""
    resources = defaultdict(set)

    # Analyze initial_state
    if "initial_state" in workflow_dict:
        for resource_type, resource_data in workflow_dict["initial_state"].items():
            if isinstance(resource_data, dict):
                resources[resource_type].update(resource_data.keys())

    # Analyze goal_state
    if "goal_state" in workflow_dict:
        for resource_type, resource_data in workflow_dict["goal_state"].items():
            if isinstance(resource_data, dict):
                # Get properties from first resource of each type
                if resource_data:
                    first_resource = (
                        next(iter(resource_data.values()))
                        if isinstance(resource_data, dict)
                        else resource_data
                    )
                    if isinstance(first_resource, dict):
                        resources[resource_type].update(first_resource.keys())

    # Analyze steps for API calls
    if "steps" in workflow_dict:
        for step in workflow_dict.get("steps", []):
            api_call = step.get("api_call", {})
            tool_name = api_call.get("tool", "")
            params = api_call.get("parameters", {})

            # Track tool usage
            resources["_tools"].add(tool_name)

            # Infer resource types from tool names
            if "catalog" in tool_name:
                resources["catalogs"].add("_inferred_from_tool")
            if "schema" in tool_name:
                resources["schemas"].add("_inferred_from_tool")
            if "table" in tool_name:
                resources["tables"].add("_inferred_from_tool")
            if "notebook" in tool_name:
                resources["notebooks"].add("_inferred_from_tool")
            if "cluster" in tool_name:
                resources["clusters"].add("_inferred_from_tool")
            if "job" in tool_name:
                resources["jobs"].add("_inferred_from_tool")
            if "volume" in tool_name:
                resources["volumes"].add("_inferred_from_tool")
            if "privilege" in tool_name or "permission" in tool_name:
                resources["permissions"].add("_inferred_from_tool")

    return dict(resources)


def process_tutorials_batch(
    urls: List[str], output_dir: str = "workflows/databricks"
) -> Dict:
    """Process multiple tutorials and analyze resource types."""
    print(f"Processing {len(urls)} tutorials...\n")

    all_resources = defaultdict(set)
    all_tools = set()
    workflows_processed = []
    errors = []

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Processing: {url}")
        try:
            # Scrape tutorial
            tutorial_text = scrape_tutorial(url)

            # Extract workflow
            workflow = extract_workflow(tutorial_text, url, output_dir)

            # Serialize to YAML
            output_path = generate_workflow_filename(workflow, output_dir)
            serialize_to_yaml(workflow, output_path)

            # Analyze resource types
            workflow_dict = workflow.model_dump()
            resources = analyze_resource_types(workflow_dict)

            # Aggregate resources
            for resource_type, properties in resources.items():
                all_resources[resource_type].update(properties)

            # Track tools
            all_tools.update(resources.get("_tools", set()))

            workflows_processed.append(
                {
                    "url": url,
                    "workflow_id": workflow.id,
                    "title": workflow.title,
                    "output_path": output_path,
                    "resources_found": list(resources.keys()),
                }
            )

            print(f"  ✓ Processed: {workflow.title}")
            print(
                f"    Resources: {', '.join([r for r in resources.keys() if not r.startswith('_')])}"
            )
            print()

        except Exception as e:
            error_msg = f"Error processing {url}: {e}"
            print(f"  ✗ {error_msg}\n")
            errors.append({"url": url, "error": str(e)})

    return {
        "workflows_processed": workflows_processed,
        "errors": errors,
        "resource_types": {
            k: list(v) for k, v in all_resources.items() if not k.startswith("_")
        },
        "tools_used": sorted(all_tools),
        "summary": {
            "total_tutorials": len(urls),
            "successful": len(workflows_processed),
            "failed": len(errors),
            "unique_resource_types": len(
                [k for k in all_resources.keys() if not k.startswith("_")]
            ),
            "unique_tools": len(all_tools),
        },
    }


def generate_schema_recommendations(analysis: Dict) -> str:
    """Generate recommendations for schema extensions."""
    current_schema_types = {
        "catalogs",
        "schemas",
        "tables",
        "notebooks",
        "clusters",
        "jobs",
        "permissions",
    }

    found_types = set(analysis["resource_types"].keys())
    missing_types = found_types - current_schema_types

    recommendations = []

    if missing_types:
        recommendations.append("## New Resource Types Needed\n")
        for resource_type in sorted(missing_types):
            properties = analysis["resource_types"].get(resource_type, [])
            recommendations.append(f"### {resource_type.title()}")
            recommendations.append(f"Properties found: {', '.join(sorted(properties))}")
            recommendations.append("")
    else:
        recommendations.append("✓ All resource types are already in the schema\n")

    # Check for missing tools - dynamically get from registry
    current_tools = set(TOOL_REGISTRY.keys())

    tools_used = set(analysis["tools_used"])
    missing_tools = tools_used - current_tools

    if missing_tools:
        recommendations.append("## Missing Tools\n")
        recommendations.append(
            "The following tools are referenced but not implemented:"
        )
        for tool in sorted(missing_tools):
            recommendations.append(f"- `{tool}`")
        recommendations.append("")

    return "\n".join(recommendations)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process Databricks tutorial URLs and generate workflows. Optionally analyze resource types for schema design."
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="Tutorial URLs to process",
    )
    parser.add_argument(
        "--output-dir",
        default="workflows/databricks",
        help="Output directory for workflow YAML files (default: workflows/databricks)",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Enable resource type analysis and generate recommendations",
    )
    parser.add_argument(
        "--analysis-output",
        default="tutorial_analysis.json",
        help="Output file for analysis results (default: tutorial_analysis.json, only used with --analyze)",
    )
    parser.add_argument(
        "--recommendations-output",
        default="schema_recommendations.md",
        help="Output file for schema recommendations (default: schema_recommendations.md, only used with --analyze)",
    )

    args = parser.parse_args()

    # Process all tutorials
    analysis = process_tutorials_batch(args.urls, args.output_dir)

    # Print basic summary
    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(
        f"✓ Processed: {analysis['summary']['successful']}/{analysis['summary']['total_tutorials']} tutorials"
    )

    if analysis["errors"]:
        print(f"⚠️  {len(analysis['errors'])} errors occurred")

    # If analysis requested, generate detailed analysis
    if args.analyze:
        # Save analysis
        with open(args.analysis_output, "w") as f:
            json.dump(analysis, f, indent=2)

        # Generate recommendations
        recommendations = generate_schema_recommendations(analysis)

        with open(args.recommendations_output, "w") as f:
            f.write("# Schema Recommendations\n\n")
            f.write(
                f"Based on analysis of {analysis['summary']['successful']} tutorials\n\n"
            )
            f.write(recommendations)
            f.write("\n## Analysis Summary\n\n")
            f.write(f"- Total tutorials: {analysis['summary']['total_tutorials']}\n")
            f.write(f"- Successfully processed: {analysis['summary']['successful']}\n")
            f.write(f"- Failed: {analysis['summary']['failed']}\n")
            f.write(
                f"- Unique resource types found: {analysis['summary']['unique_resource_types']}\n"
            )
            f.write(f"- Unique tools used: {analysis['summary']['unique_tools']}\n")

        print(f"✓ Resource types found: {len(analysis['resource_types'])}")
        print(f"✓ Tools used: {len(analysis['tools_used'])}")
        print(f"\nAnalysis saved to: {args.analysis_output}")
        print(f"Recommendations saved to: {args.recommendations_output}")
    else:
        print(
            "\nTip: Use --analyze flag to generate resource type analysis and schema recommendations"
        )

    sys.exit(0 if analysis["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
