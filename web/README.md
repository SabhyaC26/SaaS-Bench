# SaaS-Bench Workflow Visualization

React frontend for visualizing Databricks workflows and state transitions.

## Setup

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

The frontend will run on `http://localhost:5173` (Vite default port).

## Backend Setup

Make sure the FastAPI backend is running:

```bash
# From the project root
python -m uvicorn saas_bench.web.api:app --reload
```

The backend runs on `http://localhost:8000` by default. The Vite dev server is configured to proxy `/api` requests to the backend.

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory. The FastAPI backend can serve these static files in production.

## Features

- **Workflow Selection**: Browse and select from available workflows
- **Interactive Step Navigation**: Click on workflow steps to see state transitions
- **State Visualization**: Hierarchical view of Databricks state (catalogs, schemas, tables, notebooks, clusters)
- **State Transitions**: Side-by-side comparison showing what changed between steps
- **Initial/Goal State**: View initial and goal states independently
