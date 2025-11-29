import { useState } from 'react';
import './StateVisualization.css';

interface StateVisualizationProps {
  state: Record<string, any>;
  title?: string;
}

export default function StateVisualization({
  state,
  title = 'State',
}: StateVisualizationProps) {
  return (
    <div className="state-visualization">
      {title && <h3>{title}</h3>}
      <StateTree data={state} path="" />
    </div>
  );
}

interface StateTreeProps {
  data: any;
  path: string;
  level?: number;
}

function StateTree({ data, path, level = 0 }: StateTreeProps) {
  const [expanded, setExpanded] = useState(level < 2); // Auto-expand first 2 levels

  if (data === null || data === undefined) {
    return <span className="state-value null">null</span>;
  }

  if (typeof data === 'string' || typeof data === 'number' || typeof data === 'boolean') {
    return <span className="state-value">{String(data)}</span>;
  }

  if (Array.isArray(data)) {
    if (data.length === 0) {
      return <span className="state-value empty">[]</span>;
    }
    return (
      <div className="state-array">
        <button
          className="state-toggle"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? '▼' : '▶'} Array [{data.length}]
        </button>
        {expanded && (
          <div className="state-children">
            {data.map((item, index) => (
              <div key={index} className="state-item">
                <span className="state-key">[{index}]</span>
                <StateTree data={item} path={`${path}[${index}]`} level={level + 1} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (typeof data === 'object') {
    const keys = Object.keys(data);
    if (keys.length === 0) {
      return <span className="state-value empty">{'{}'}</span>;
    }

    // Special handling for DatabricksState structure
    const isDatabricksState = keys.some(
      (k) =>
        k === 'catalogs' ||
        k === 'schemas' ||
        k === 'tables' ||
        k === 'notebooks' ||
        k === 'clusters' ||
        k === 'jobs' ||
        k === 'permissions'
    );

    return (
      <div className={`state-object ${isDatabricksState ? 'databricks-state' : ''}`}>
        <button
          className="state-toggle"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? '▼' : '▶'} {isDatabricksState ? 'DatabricksState' : 'Object'} ({keys.length})
        </button>
        {expanded && (
          <div className="state-children">
            {keys.map((key) => (
              <div key={key} className="state-item">
                <span className="state-key">{key}:</span>
                <StateTree data={data[key]} path={`${path}.${key}`} level={level + 1} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return <span className="state-value">{String(data)}</span>;
}
