/** API client for workflow visualization backend. */

export interface WorkflowSummary {
  id: string;
  title: string;
  platforms: string[];
  description: string;
}

export interface WorkflowStep {
  step_id: number;
  description: string;
  method: string;
  sql_command: string | null;
  api_call: {
    tool: string;
    parameters: Record<string, any>;
  };
  expected_state_change: Record<string, any>;
  verification: Record<string, any>;
}

export interface WorkflowDetail {
  id: string;
  source_url: string;
  title: string;
  platforms: string[];
  description: string;
  prerequisites: string[];
  initial_state: Record<string, any>;
  goal_state: Record<string, any>;
  steps: WorkflowStep[];
}

export interface StateResponse {
  workflow_id: string;
  step_index?: number;
  step_id?: number;
  state: Record<string, any>;
}

const API_BASE = '/api';

export async function listWorkflows(): Promise<WorkflowSummary[]> {
  const response = await fetch(`${API_BASE}/workflows`);
  if (!response.ok) {
    throw new Error(`Failed to fetch workflows: ${response.statusText}`);
  }
  return response.json();
}

export async function getWorkflow(workflowId: string): Promise<WorkflowDetail> {
  const response = await fetch(`${API_BASE}/workflows/${workflowId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch workflow: ${response.statusText}`);
  }
  return response.json();
}

export async function getStateAtStep(
  workflowId: string,
  stepIndex: number
): Promise<StateResponse> {
  const response = await fetch(`${API_BASE}/workflows/${workflowId}/state/${stepIndex}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch state: ${response.statusText}`);
  }
  return response.json();
}

export async function getStateBeforeStep(
  workflowId: string,
  stepId: number
): Promise<StateResponse> {
  const response = await fetch(`${API_BASE}/workflows/${workflowId}/state/before/${stepId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch state: ${response.statusText}`);
  }
  return response.json();
}

export async function getStateAfterStep(
  workflowId: string,
  stepId: number
): Promise<StateResponse> {
  const response = await fetch(`${API_BASE}/workflows/${workflowId}/state/after/${stepId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch state: ${response.statusText}`);
  }
  return response.json();
}
