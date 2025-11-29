import { useEffect, useState } from 'react';
import { listWorkflows, WorkflowSummary } from '../api';
import './WorkflowSelector.css';

interface WorkflowSelectorProps {
  onSelectWorkflow: (workflowId: string) => void;
  selectedWorkflowId: string | null;
}

export default function WorkflowSelector({
  onSelectWorkflow,
  selectedWorkflowId,
}: WorkflowSelectorProps) {
  const [workflows, setWorkflows] = useState<WorkflowSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchWorkflows() {
      try {
        setLoading(true);
        setError(null);
        const data = await listWorkflows();
        setWorkflows(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load workflows');
      } finally {
        setLoading(false);
      }
    }

    fetchWorkflows();
  }, []);

  if (loading) {
    return <div className="workflow-selector loading">Loading workflows...</div>;
  }

  if (error) {
    return <div className="workflow-selector error">Error: {error}</div>;
  }

  return (
    <div className="workflow-selector">
      <h2>Select Workflow</h2>
      <div className="workflow-list">
        {workflows.map((workflow) => (
          <div
            key={workflow.id}
            className={`workflow-item ${selectedWorkflowId === workflow.id ? 'selected' : ''}`}
            onClick={() => onSelectWorkflow(workflow.id)}
          >
            <div className="workflow-header">
              <h3>{workflow.title}</h3>
            </div>
            <p className="workflow-description">{workflow.description}</p>
            <div className="workflow-platforms">
              {workflow.platforms.map((platform) => (
                <span key={platform} className="platform-tag">
                  {platform}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
