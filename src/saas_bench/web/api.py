"""FastAPI application for workflow visualization."""

from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..tutorial_processor.workflow_extractor import Workflow
from ..utils.yaml_loader import load_all_workflows, load_workflow
from .state_computer import compute_state_at_step

app = FastAPI(title="SaaS-Bench Workflow Visualization API")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WorkflowSummary(BaseModel):
    """Summary of a workflow for listing."""

    id: str
    title: str
    platforms: List[str]
    description: str


class WorkflowDetail(BaseModel):
    """Full workflow details."""

    id: str
    source_url: str
    title: str
    platforms: List[str]
    description: str
    prerequisites: List[str]
    initial_state: Dict
    goal_state: Dict
    steps: List[Dict]


@app.get("/api/workflows", response_model=List[WorkflowSummary])
async def list_workflows():
    """List all available workflows."""
    workflows_dir = Path("workflows/databricks")
    workflows = load_all_workflows(str(workflows_dir))

    return [
        WorkflowSummary(
            id=wf.id,
            title=wf.title,
            platforms=wf.platforms,
            description=wf.description,
        )
        for wf in workflows
    ]


@app.get("/api/workflows/{workflow_id}", response_model=WorkflowDetail)
async def get_workflow(workflow_id: str):
    """Get full details of a specific workflow."""
    workflows_dir = Path("workflows/databricks")
    workflow_file = workflows_dir / f"{workflow_id}.yaml"

    if not workflow_file.exists():
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    try:
        workflow = load_workflow(str(workflow_file))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading workflow: {str(e)}")

    return WorkflowDetail(
        id=workflow.id,
        source_url=workflow.source_url,
        title=workflow.title,
        platforms=workflow.platforms,
        description=workflow.description,
        prerequisites=workflow.prerequisites,
        initial_state=workflow.initial_state,
        goal_state=workflow.goal_state,
        steps=[step.model_dump() for step in workflow.steps],
    )


@app.get("/api/workflows/{workflow_id}/state/{step_index}")
async def get_state_at_step(workflow_id: str, step_index: int):
    """Get state at a specific step index.

    Args:
        workflow_id: The workflow ID
        step_index: Step index (0 = initial, 1-N = after step N, -1 = goal)
    """
    workflows_dir = Path("workflows/databricks")
    workflow_file = workflows_dir / f"{workflow_id}.yaml"

    if not workflow_file.exists():
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    try:
        workflow = load_workflow(str(workflow_file))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading workflow: {str(e)}")

    # Validate step_index
    max_step = len(workflow.steps)
    if step_index < -1 or step_index > max_step:
        raise HTTPException(
            status_code=400,
            detail=f"Step index must be between -1 (goal) and {max_step} (after last step)",
        )

    state = compute_state_at_step(workflow, step_index)

    return {
        "workflow_id": workflow_id,
        "step_index": step_index,
        "state": state,
    }


@app.get("/api/workflows/{workflow_id}/state/before/{step_id}")
async def get_state_before_step(workflow_id: str, step_id: int):
    """Get state before a specific step."""
    from .state_computer import compute_state_before_step

    workflows_dir = Path("workflows/databricks")
    workflow_file = workflows_dir / f"{workflow_id}.yaml"

    if not workflow_file.exists():
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    try:
        workflow = load_workflow(str(workflow_file))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading workflow: {str(e)}")

    state = compute_state_before_step(workflow, step_id)

    return {
        "workflow_id": workflow_id,
        "step_id": step_id,
        "state": state,
    }


@app.get("/api/workflows/{workflow_id}/state/after/{step_id}")
async def get_state_after_step(workflow_id: str, step_id: int):
    """Get state after a specific step."""
    from .state_computer import compute_state_after_step

    workflows_dir = Path("workflows/databricks")
    workflow_file = workflows_dir / f"{workflow_id}.yaml"

    if not workflow_file.exists():
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    try:
        workflow = load_workflow(str(workflow_file))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading workflow: {str(e)}")

    state = compute_state_after_step(workflow, step_id)

    return {
        "workflow_id": workflow_id,
        "step_id": step_id,
        "state": state,
    }
