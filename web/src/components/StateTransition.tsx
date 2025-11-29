import StateVisualization from './StateVisualization';
import './StateTransition.css';

interface StateTransitionProps {
  beforeState: Record<string, any>;
  afterState: Record<string, any>;
  stepDescription?: string;
}

export default function StateTransition({
  beforeState,
  afterState,
  stepDescription,
}: StateTransitionProps) {
  const changes = computeChanges(beforeState, afterState);

  return (
    <div className="state-transition">
      {stepDescription && (
        <div className="transition-header">
          <h3>State Transition</h3>
          <p className="step-description">{stepDescription}</p>
        </div>
      )}
      <div className="transition-comparison">
        <div className="state-panel">
          <h4>Before</h4>
          <StateVisualization state={beforeState} />
        </div>
        <div className="transition-arrow">→</div>
        <div className="state-panel">
          <h4>After</h4>
          <StateVisualization state={afterState} />
        </div>
      </div>
      {changes.length > 0 && (
        <div className="changes-summary">
          <h4>Changes Detected:</h4>
          <ul>
            {changes.map((change, index) => (
              <li key={index} className={`change-${change.type}`}>
                <strong>{change.path}:</strong> {change.description}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

interface Change {
  path: string;
  type: 'added' | 'modified' | 'removed';
  description: string;
}

function computeChanges(
  before: Record<string, any>,
  after: Record<string, any>
): Change[] {
  const changes: Change[] = [];

  function compare(
    beforeObj: any,
    afterObj: any,
    path: string = ''
  ): void {
    if (beforeObj === afterObj) {
      return;
    }

    if (beforeObj === null || beforeObj === undefined) {
      changes.push({
        path: path || 'root',
        type: 'added',
        description: `Added: ${JSON.stringify(afterObj)}`,
      });
      return;
    }

    if (afterObj === null || afterObj === undefined) {
      changes.push({
        path: path || 'root',
        type: 'removed',
        description: `Removed: ${JSON.stringify(beforeObj)}`,
      });
      return;
    }

    if (typeof beforeObj !== 'object' || typeof afterObj !== 'object') {
      if (beforeObj !== afterObj) {
        changes.push({
          path: path || 'root',
          type: 'modified',
          description: `${beforeObj} → ${afterObj}`,
        });
      }
      return;
    }

    if (Array.isArray(beforeObj) || Array.isArray(afterObj)) {
      if (JSON.stringify(beforeObj) !== JSON.stringify(afterObj)) {
        changes.push({
          path: path || 'root',
          type: 'modified',
          description: `Array changed (length: ${beforeObj?.length || 0} → ${afterObj?.length || 0})`,
        });
      }
      return;
    }

    const allKeys = new Set([
      ...Object.keys(beforeObj),
      ...Object.keys(afterObj),
    ]);

    for (const key of allKeys) {
      const newPath = path ? `${path}.${key}` : key;
      if (!(key in beforeObj)) {
        changes.push({
          path: newPath,
          type: 'added',
          description: `Added: ${JSON.stringify(afterObj[key])}`,
        });
      } else if (!(key in afterObj)) {
        changes.push({
          path: newPath,
          type: 'removed',
          description: `Removed: ${JSON.stringify(beforeObj[key])}`,
        });
      } else {
        compare(beforeObj[key], afterObj[key], newPath);
      }
    }
  }

  compare(before, after);
  return changes;
}
