# SaaS-Bench Technical Architecture Overview

## Project Purpose

SaaS-Bench is a benchmark for evaluating AI agents on cross-platform enterprise SaaS workflows. The system simulates enterprise SaaS platforms (currently Databricks, with plans for Snowflake and Salesforce) to test how well AI agents can complete complex, multi-step tasks without requiring actual platform access.

## Core Architecture

### 1. State-Machine Model (τ-bench methodology)

The system uses a state-machine approach where:

- **State** represents the entire simulated workspace (catalogs, schemas, tables, notebooks, clusters, jobs, permissions)
- **Actions** are API tool calls that transform state
- **Evaluation** compares final state to goal state

### 2. State Management (`src/saas_bench/domains/databricks/state.py`)

The `DatabricksState` is a Pydantic model that aggregates all resources:

- **Catalogs**: Unity Catalog catalogs with ownership and properties
- **Schemas**: Database schemas within catalogs
- **Tables**: Tables with columns, data rows, and metadata
- **Notebooks**: Databricks notebooks with language and content
- **Clusters**: Compute clusters with configuration
- **Jobs**: Scheduled jobs with tasks and schedules
- **Permissions**: Access control entries (ACLs)

All models are **frozen** (immutable) - state updates create new objects rather than modifying existing ones.

### 3. API Tools (`src/saas_bench/domains/databricks/tools.py`)

Pure Python functions that implement Databricks operations:

- Each function signature: `(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]`
- Returns new state and API response
- Examples: `create_catalog`, `create_schema`, `create_table`, `insert_into_table`, `query_table`, `grant_privilege`, `create_notebook`, `create_cluster`, `create_job`

### 4. Tool Registry (`src/saas_bench/domains/databricks/registry.py`)

- `TOOL_REGISTRY`: Dictionary mapping tool names to functions
- `get_tool_spec()` / `get_all_tool_specs()`: Generate OpenAPI-style JSON schemas for agent discovery

### 5. Policy System (`src/saas_bench/domains/databricks/policy.py`)

Enforces constraints and validation rules:

- Resource name validation (catalogs, schemas, tables)
- Cluster count limits
- Permission validation
- `get_policy_document()`: Returns markdown policy document for agents

### 6. Environment (`src/saas_bench/core/environment.py`)

The `Environment` class orchestrates agent interactions:

- Maintains current state (`_state: DatabricksState`)
- Tracks conversation history (`_conversation_history`)
- Records state snapshots (`_state_snapshots`)
- `execute_tool()`: Executes tool calls and updates state immutably
- `get_state()`: Returns current state
- `get_tool_specs()`: Returns available tool specifications

### 7. Evaluation (`src/saas_bench/core/evaluation.py`)

The `evaluate_task()` function compares final state to goal state:

- **Success determination**: Checks for missing resources, incorrect tables, missing permissions
- **Score calculation**: Percentage of checks passed (0.0-1.0)
- **Milestones**: Partial credit for achieved sub-goals
- **Minefields**: Critical failures (e.g., unexpected permissions granted)
- Returns `EvaluationResult` with success, score, milestones, minefields, and differences

## Workflow Generation Pipeline

### 1. Web Scraping (`src/saas_bench/tutorial_processor/scraper.py`)

`scrape_tutorial()` function:

- Fetches HTML from Databricks documentation URLs
- Uses BeautifulSoup to parse and clean content
- Removes navigation, headers, footers, scripts, styles
- Extracts main content with titles, prerequisites, and step-by-step instructions

### 2. LLM-Based Extraction (`src/saas_bench/tutorial_processor/workflow_extractor.py`)

`extract_workflow()` function:

- Uses Grok (via OpenAI SDK) to transform unstructured tutorial text into structured `Workflow` objects
- System prompt guides LLM to:
  - Identify prerequisites
  - Break down steps
  - Map SQL/UI actions to API tools
  - Specify expected state changes
  - Define initial and goal states
- Generates sequential workflow IDs (databricks-001, databricks-002, etc.)

**Workflow Structure:**

- `WorkflowStep`: step_id, description, method (sql/ui/api), sql_command, api_call, expected_state_change, verification
- `Workflow`: id, source_url, title, description, prerequisites, initial_state, goal_state, steps

### 3. LLM Client (`src/saas_bench/tutorial_processor/llm_client.py`)

`GrokClient` class:

- Wraps OpenAI SDK for Grok models
- Supports structured output with Pydantic models
- Fallback mechanism: tries beta API first, then JSON mode with schema instructions

### 4. Serialization (`src/saas_bench/tutorial_processor/workflow_serializer.py`)

- `serialize_to_yaml()`: Converts `Workflow` Pydantic objects to YAML files
- `generate_workflow_filename()`: Creates standard filenames

## CLI Tools

### 1. Batch Tutorial Processing (`scripts/analyze_tutorials_batch.py`)

Orchestrates the full pipeline:

- Processes multiple tutorial URLs
- Scrapes → Extracts → Serializes workflows
- With `--analyze` flag: Also analyzes resource types and generates schema recommendations

### 2. Workflow Validation (`scripts/validate_workflows.py`)

- Validates workflow YAML structure (Pydantic schema)
- Validates `initial_state` and `goal_state` against `DatabricksState` schema
- Can skip state validation with `--skip-state-validation`

### 3. State Schema Analysis (`scripts/update_state_from_workflows.py`)

- Analyzes existing workflow YAML files
- Extracts resource types and properties from `initial_state`, `goal_state`, `expected_state_change`
- Compares findings against current `DatabricksState` schema
- Generates JSON analysis and markdown recommendations for missing types/properties

### 4. YAML Loading (`src/saas_bench/utils/yaml_loader.py`)

- `load_workflow()`: Loads single workflow YAML into `Workflow` model
- `load_all_workflows()`: Loads all workflows from directory
- `validate_state_dict()`: Ensures state dictionaries conform to `DatabricksState` schema

## Workflow Format

Workflows are stored as YAML files in `workflows/databricks/`:

id: databricks-001
title: "Create a Table"
source_url: "<https://docs.databricks.com/>..."
platforms: ["databricks"]
description: "..."
prerequisites: [...]
initial_state:
  catalogs: {...}
  schemas: {...}

# ... other resources

goal_state:
  catalogs: {...}
  tables: {...}

# ... desired end state

steps:

- step_id: 1
    description: "..."
    method: "sql"  # or "ui" or "api"
    sql_command: "CREATE TABLE ..."
    api_call:
      tool: "create_table"
      parameters: {...}
    expected_state_change: {...}
    verification: {...}## Key Design Principles

1. **Immutability**: All state updates create new objects
2. **Pure Functions**: API tools have no side effects
3. **Type Safety**: Pydantic models throughout
4. **Modularity**: Clear separation between tutorial processing, domain logic, and evaluation
5. **Extensibility**: Schema can evolve as new resource types are discovered

## Dependencies

- **pydantic**: State models and validation
- **openai**: LLM client for workflow extraction
- **beautifulsoup4**: Web scraping
- **requests**: HTTP requests
- **pyyaml**: YAML parsing
- **python-dotenv**: Environment variable management
- **fastapi/uvicorn**: Web API (for visualization, excluded from this overview)

## Testing

Test files in `tests/`:

- `test_databricks_state.py`: State model tests
- `test_databricks_tools.py`: Tool function tests
- `test_environment.py`: Environment orchestration tests
- `test_evaluation.py`: Evaluation logic tests

## Future Phases

- **Phase 2**: Multi-platform support (Snowflake, Salesforce)
- **Phase 3**: Difficulty scaling (user personas, failure injection, dynamic constraints)
- **Phase 4**: Validation & baseline establishment
