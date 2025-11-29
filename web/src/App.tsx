import { useEffect, useState } from 'react';
import { getWorkflow, getStateBeforeStep, getStateAfterStep, getStateAtStep, WorkflowDetail } from './api';
import WorkflowSelector from './components/WorkflowSelector';
import WorkflowSteps from './components/WorkflowSteps';
import StateVisualization from './components/StateVisualization';
import StateTransition from './components/StateTransition';
import './App.css';

function App() {
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);
  const [workflow, setWorkflow] = useState<WorkflowDetail | null>(null);
  const [selectedStepId, setSelectedStepId] = useState<number | null>(null);
  const [currentState, setCurrentState] = useState<Record<string, any> | null>(null);
  const [beforeState, setBeforeState] = useState<Record<string, any> | null>(null);
  const [afterState, setAfterState] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedWorkflowId) {
      async function fetchWorkflow() {
        try {
          setLoading(true);
          setError(null);
          const data = await getWorkflow(selectedWorkflowId);
          setWorkflow(data);
          setSelectedStepId(null);
          setCurrentState(data.initial_state);
          setBeforeState(null);
          setAfterState(null);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to load workflow');
        } finally {
          setLoading(false);
        }
      }

      fetchWorkflow();
    }
  }, [selectedWorkflowId]);

  const handleStepSelect = async (stepId: number) => {
    if (!workflow || !selectedWorkflowId) return;

    setSelectedStepId(stepId);
    setLoading(true);
    setError(null);

    try {
      const [before, after] = await Promise.all([
        getStateBeforeStep(selectedWorkflowId, stepId),
        getStateAfterStep(selectedWorkflowId, stepId),
      ]);

      setBeforeState(before.state);
      setAfterState(after.state);
      setCurrentState(after.state);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load state');
    } finally {
      setLoading(false);
    }
  };

  const handleShowInitial = () => {
    if (workflow) {
      setSelectedStepId(null);
      setCurrentState(workflow.initial_state);
      setBeforeState(null);
      setAfterState(null);
    }
  };

  const handleShowGoal = async () => {
    if (!workflow || !selectedWorkflowId) return;

    setSelectedStepId(null);
    setLoading(true);
    setError(null);

    try {
      const data = await getStateAtStep(selectedWorkflowId, -1);
      setCurrentState(data.state);
      setBeforeState(null);
      setAfterState(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load goal state');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>SaaS-Bench Workflow Visualization</h1>
      </header>

      <div className="app-content">
        <div className="sidebar">
          <WorkflowSelector
            onSelectWorkflow={setSelectedWorkflowId}
            selectedWorkflowId={selectedWorkflowId}
          />
        </div>

        <div className="main-content">
          {error && (
            <div className="error-banner">
              Error: {error}
            </div>
          )}

          {loading && (
            <div className="loading-banner">
              Loading...
            </div>
          )}

          {workflow && (
            <>
              <div className="workflow-info">
                <h2>{workflow.title}</h2>
                <p>{workflow.description}</p>
                <div className="workflow-meta">
                  <span>{workflow.platforms.join(', ')}</span>
                </div>
                <div className="state-navigation">
                  <button onClick={handleShowInitial}>Show Initial State</button>
                  <button onClick={handleShowGoal}>Show Goal State</button>
                </div>
              </div>

              <WorkflowSteps
                steps={workflow.steps}
                selectedStepId={selectedStepId}
                onStepSelect={handleStepSelect}
              />

              {selectedStepId && beforeState && afterState && (
                <StateTransition
                  beforeState={beforeState}
                  afterState={afterState}
                  stepDescription={
                    workflow.steps.find((s) => s.step_id === selectedStepId)?.description
                  }
                />
              )}

              {currentState && !selectedStepId && (
                <div className="current-state">
                  <StateVisualization
                    state={currentState}
                    title={selectedStepId ? `State After Step ${selectedStepId}` : 'Current State'}
                  />
                </div>
              )}
            </>
          )}

          {!workflow && !loading && (
            <div className="empty-state">
              <p>Select a workflow from the sidebar to begin visualization</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
