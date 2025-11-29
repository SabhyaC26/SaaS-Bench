"""Extract workflows from tutorial text using LLM with structured outputs."""

import re
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .llm_client import GrokClient


class WorkflowStep(BaseModel):
    """A single step in a workflow."""

    step_id: int
    description: str
    method: str = Field(description="Method used: 'sql', 'ui', or 'api'")
    sql_command: Optional[str] = Field(
        None, description="Original SQL command if applicable"
    )
    api_call: Dict = Field(
        description="API call specification with tool name and parameters"
    )
    expected_state_change: Dict = Field(
        default_factory=dict, description="Expected state changes"
    )
    verification: Dict = Field(
        default_factory=dict, description="How to verify this step succeeded"
    )


class Workflow(BaseModel):
    """Complete workflow extracted from tutorial."""

    id: str = Field(description="Unique workflow identifier")
    source_url: str = Field(description="Source tutorial URL")
    title: str = Field(description="Tutorial title")
    platforms: List[str] = Field(description="List of platforms involved")
    description: str = Field(description="Workflow description")
    prerequisites: List[str] = Field(
        default_factory=list, description="Prerequisites from tutorial"
    )
    initial_state: Dict = Field(default_factory=dict, description="Starting state")
    goal_state: Dict = Field(description="Final desired state")
    steps: List[WorkflowStep] = Field(description="Step-by-step instructions")


def generate_next_workflow_id(output_dir: str = "workflows/databricks") -> str:
    """Generate the next sequential workflow ID in format databricks-XXX."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Pattern to match databricks-XXX.yaml files
    pattern = re.compile(r"^databricks-(\d+)\.yaml$")

    max_num = 0
    for file_path in output_path.glob("databricks-*.yaml"):
        match = pattern.match(file_path.name)
        if match:
            num = int(match.group(1))
            max_num = max(max_num, num)

    # Return next ID with zero-padded 3 digits
    next_num = max_num + 1
    return f"databricks-{next_num:03d}"


def extract_workflow(
    tutorial_text: str, source_url: str, output_dir: str = "workflows/databricks"
) -> Workflow:
    """Extract workflow from tutorial text using LLM with structured outputs."""
    client = GrokClient()

    system_prompt = """You are an expert at analyzing SaaS platform tutorials and extracting structured workflows.

Your task is to analyze a Databricks tutorial and extract a complete workflow specification.

Key requirements:
1. Identify all prerequisites from "Before you begin" or "Requirements" sections
2. Break down the tutorial into clear, sequential steps
3. Map SQL commands to API tools:
   - "USE CATALOG <catalog>" → use_catalog tool
   - "CREATE TABLE IF NOT EXISTS <catalog>.<schema>.<table>" → create_table tool
   - "INSERT INTO <table> VALUES" → insert_into_table tool
   - "GRANT SELECT ON <table> TO <principal>" → grant_privilege tool
   - "SELECT * FROM <table>" → query_table tool
4. Map UI actions to API tools:
   - "Create notebook" → create_notebook tool
   - "Attach to cluster" → attach_to_cluster tool
   - "Create visualization" → create_visualization tool
5. Specify expected state changes for each step
6. Define initial state (starting conditions) and goal state (desired end result)

Generate a complete workflow specification following the Workflow schema."""

    user_prompt = f"""Analyze the following Databricks tutorial and extract a complete workflow:

Tutorial URL: {source_url}

Tutorial Content:
{tutorial_text}

Extract the workflow with:
- All prerequisites
- Step-by-step instructions with API tool mappings
- Expected state changes for each step
- Initial state (starting conditions)
- Goal state (desired end result)"""

    workflow = client.structured_output(user_prompt, system_prompt, Workflow)

    # Ensure source_url is set
    if not workflow.source_url:
        workflow = workflow.model_copy(update={"source_url": source_url})

    # Always generate sequential ID (ignore LLM-generated ID)
    workflow_id = generate_next_workflow_id(output_dir)
    workflow = workflow.model_copy(update={"id": workflow_id})

    return workflow
