import { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  ConnectionMode,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { WorkflowStep } from '../api';
import './WorkflowSteps.css';

interface WorkflowStepsProps {
  steps: WorkflowStep[];
  selectedStepId: number | null;
  onStepSelect: (stepId: number) => void;
}

export default function WorkflowSteps({
  steps,
  selectedStepId,
  onStepSelect,
}: WorkflowStepsProps) {
  const nodes: Node[] = useMemo(() => {
    const workflowNodes: Node[] = [
      {
        id: 'initial',
        type: 'default',
        position: { x: 250, y: 0 },
        data: { label: 'Initial State' },
        style: {
          background: '#e3f2fd',
          border: '2px solid #2196f3',
          borderRadius: '8px',
          padding: '10px',
        },
      },
    ];

    steps.forEach((step, index) => {
      const y = (index + 1) * 150;
      const isSelected = selectedStepId === step.step_id;

      workflowNodes.push({
        id: `step-${step.step_id}`,
        type: 'default',
        position: { x: 250, y },
        data: {
          label: (
            <div className="step-node-content">
              <div className="step-header">
                <span className="step-id">Step {step.step_id}</span>
                <span className="step-method">{step.method.toUpperCase()}</span>
              </div>
              <div className="step-description">{step.description}</div>
              <div className="step-tool">
                Tool: <strong>{step.api_call.tool}</strong>
              </div>
            </div>
          ),
        },
        style: {
          background: isSelected ? '#fff3cd' : '#ffffff',
          border: isSelected ? '3px solid #ffc107' : '2px solid #ddd',
          borderRadius: '8px',
          padding: '10px',
          minWidth: '300px',
          cursor: 'pointer',
        },
      });
    });

    workflowNodes.push({
      id: 'goal',
      type: 'default',
      position: { x: 250, y: (steps.length + 1) * 150 },
      data: { label: 'Goal State' },
      style: {
        background: '#e8f5e9',
        border: '2px solid #4caf50',
        borderRadius: '8px',
        padding: '10px',
      },
    });

    return workflowNodes;
  }, [steps, selectedStepId]);

  const edges: Edge[] = useMemo(() => {
    const workflowEdges: Edge[] = [
      {
        id: 'initial-step-1',
        source: 'initial',
        target: 'step-1',
        animated: true,
      },
    ];

    for (let i = 1; i < steps.length; i++) {
      workflowEdges.push({
        id: `step-${i}-step-${i + 1}`,
        source: `step-${i}`,
        target: `step-${i + 1}`,
        animated: true,
      });
    }

    if (steps.length > 0) {
      workflowEdges.push({
        id: `step-${steps.length}-goal`,
        source: `step-${steps.length}`,
        target: 'goal',
        animated: true,
      });
    }

    return workflowEdges;
  }, [steps]);

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      if (node.id.startsWith('step-')) {
        const stepId = parseInt(node.id.replace('step-', ''), 10);
        onStepSelect(stepId);
      }
    },
    [onStepSelect]
  );

  return (
    <div className="workflow-steps">
      <h2>Workflow Steps</h2>
      <div style={{ width: '100%', height: '600px' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodeClick={onNodeClick}
          connectionMode={ConnectionMode.Loose}
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}
