# SaaS-Bench

Benchmark for evaluating AI agents on cross-platform enterprise SaaS workflows.

## Overview

SaaS-Bench is a benchmark for evaluating AI agents on cross-platform enterprise SaaS workflows. The implementation follows a four-phase approach, building from foundation to full validation.

## Phase 1: Foundation

Phase 1 focuses on Databricks platform support, including:

- Tutorial processing service for extracting workflows from documentation
- Databricks state schema (Unity Catalog, notebooks, clusters, jobs)
- API tools for Databricks operations
- Policy document with validation rules
- Environment class for orchestrating agent interactions
- Basic evaluation logic

## Installation

1. Install dependencies using `uv`:

```bash
uv sync
```

1. Set up environment variables:

```bash
cp .env.example .env
# Edit .env and add your GROK_API_KEY
```

## Usage

### Processing Tutorials

Process one or more tutorials and optionally analyze resource types:

```bash
# Process tutorials without analysis (simple workflow extraction)
python scripts/analyze_tutorials_batch.py \
  https://docs.databricks.com/aws/en/getting-started/create-table \
  https://docs.databricks.com/aws/en/getting-started/quick-start

# Process tutorials WITH analysis (recommended for schema design)
python scripts/analyze_tutorials_batch.py \
  https://docs.databricks.com/aws/en/getting-started/create-table \
  https://docs.databricks.com/aws/en/getting-started/quick-start \
  --analyze \
  --analysis-output tutorial_analysis.json \
  --recommendations-output schema_recommendations.md
```

**With `--analyze` flag**, the script will:

- Process all tutorials and extract workflows
- Analyze resource types and properties needed
- Generate schema recommendations
- Create workflow YAML files

**Without `--analyze` flag**, the script will:

- Process tutorials and extract workflows
- Create workflow YAML files
- Skip analysis (faster for simple processing)

### Validating Workflows

Validate generated workflow files (validates both workflow structure and state schemas):

```bash
python scripts/validate_workflows.py
```

Validate specific files:

```bash
python scripts/validate_workflows.py workflows/databricks/create-table-tutorial.yaml
```

Skip state validation (only validate workflow structure):

```bash
python scripts/validate_workflows.py --skip-state-validation
```

**What gets validated:**

- ✓ Workflow structure (id, title, steps, etc.)
- ✓ `initial_state` and `goal_state` conform to `DatabricksState` schema
- ✓ All resource types and properties match the schema

### Analyzing State Schema

Analyze existing workflows to identify missing resource types and properties in the state schema:

```bash
python scripts/update_state_from_workflows.py
```

This script will:

- Analyze all workflows in `workflows/databricks/`
- Compare found resources with the current `DatabricksState` schema
- Generate recommendations for missing resource types and properties
- Output JSON analysis and markdown recommendations

Options:

```bash
# Specify custom workflows directory
python scripts/update_state_from_workflows.py --workflows-dir workflows/databricks

# Custom output files
python scripts/update_state_from_workflows.py \
  --json-output my_analysis.json \
  --markdown-output my_recommendations.md
```

### Web Visualization Interface

SaaS-Bench includes a web-based visualization interface for exploring workflows and state transitions.

**Backend Setup:**

Start the FastAPI server:

```bash
python -m uvicorn saas_bench.web.api:app --reload
```

The API will be available at `http://localhost:8000`.

**Frontend Setup:**

Navigate to the web directory:

```bash
cd web
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will run on `http://localhost:5173` (Vite default port).

**Features:**

- **Workflow Selection**: Browse and select from available workflows
- **Interactive Step Navigation**: Click on workflow steps to see state transitions
- **State Visualization**: Hierarchical view of Databricks state (catalogs, schemas, tables, notebooks, clusters)
- **State Transitions**: Side-by-side comparison showing what changed between steps
- **Initial/Goal State**: View initial and goal states independently

**API Endpoints:**

- `GET /api/workflows` - List all available workflows
- `GET /api/workflows/{workflow_id}` - Get full workflow details
- `GET /api/workflows/{workflow_id}/state/{step_index}` - Get state at a specific step (0 = initial, -1 = goal, 1-N = after step N)
- `GET /api/workflows/{workflow_id}/state/before/{step_id}` - Get state before a specific step
- `GET /api/workflows/{workflow_id}/state/after/{step_id}` - Get state after a specific step

### Running Tests

Run the test suite:

```bash
pytest
```

Run specific test files:

```bash
pytest tests/test_databricks_state.py
pytest tests/test_databricks_tools.py
pytest tests/test_environment.py
pytest tests/test_evaluation.py
```

## Project Structure

```text
SaaS-Bench/
├── src/saas_bench/
│   ├── tutorial_processor/    # Tutorial scraping and workflow extraction
│   ├── domains/databricks/    # Databricks domain implementation
│   ├── core/                  # Environment and evaluation
│   ├── web/                   # Web visualization API and state computation
│   └── utils/                 # Utility functions
├── workflows/databricks/      # Generated workflow YAML files
├── web/                       # React frontend for workflow visualization
├── tests/                     # Test suite
└── scripts/                   # CLI scripts
```

## Development

### Key Components

- **State Schema**: Pydantic models for Databricks resources (catalogs, schemas, tables, notebooks, clusters, jobs, permissions)
- **API Tools**: Pure functions implementing Databricks operations
- **Environment**: Orchestrates state transitions and tool execution
- **Evaluation**: Compares final state to goal state for task success determination
- **Web Visualization**: React frontend with FastAPI backend for interactive workflow exploration
- **State Computation**: Logic for computing state at any workflow step from initial state and step changes

### Design Principles

1. **State Immutability**: All state updates create new state objects
2. **Pure Functions**: API tools are pure functions with no side effects
3. **Type Safety**: Pydantic models throughout for validation
4. **Modularity**: Clear separation between tutorial processing, domain logic, and evaluation
5. **Extensibility**: Schema can be extended when new resource types are discovered

### Schema Design

#### Recommended Approach: Batch Analysis

Process all tutorials upfront, then build one comprehensive schema:

1. **Batch process all tutorials:**

   ```bash
   python scripts/analyze_tutorials_batch.py <all-tutorial-urls>
   ```

2. **Review recommendations:**
   - Check `schema_recommendations.md` for resource types needed
   - Review `tutorial_analysis.json` for detailed analysis

3. **Build comprehensive schema:**
   - Add all resource types at once
   - Create all API tools
   - Update evaluation logic

See [docs/BATCH_SCHEMA_DESIGN.md](docs/BATCH_SCHEMA_DESIGN.md) for the complete process.

#### Incremental Extension (Alternative)

If you need to extend the schema after initial design, you have two options:

- Use the analyze flag when processing new tutorials:

```bash
python scripts/analyze_tutorials_batch.py <tutorial-urls> --analyze
```

- Analyze existing workflows to find schema gaps:

```bash
python scripts/update_state_from_workflows.py
```

This will compare all existing workflows against the current schema and generate recommendations for missing properties and resource types.
