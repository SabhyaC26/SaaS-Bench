"""Databricks API tools as pure functions."""

from typing import Dict, Tuple

from .state import (
    Catalog,
    Cluster,
    DatabricksState,
    Job,
    Notebook,
    Permission,
    Schema,
    Table,
)


def use_catalog(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """Set the active catalog context."""
    catalog_name = args.get("catalog_name")
    if not catalog_name:
        return state, {"error": "catalog_name is required"}

    if catalog_name not in state.catalogs:
        return state, {"error": f"Catalog '{catalog_name}' does not exist"}

    new_state = state.model_copy(update={"active_catalog": catalog_name})
    return new_state, {"success": True, "active_catalog": catalog_name}


def list_catalogs(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """List all catalogs."""
    catalog_list = [
        {
            "name": catalog.name,
            "owner": catalog.owner,
            "comment": catalog.comment,
        }
        for catalog in state.catalogs.values()
    ]
    return state, {"catalogs": catalog_list}


def create_catalog(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """Create a new catalog."""
    catalog_name = args.get("catalog_name")
    owner = args.get("owner", "admin")
    catalog_type = args.get("type")  # "standard", "shared", or "foreign"
    comment = args.get("comment")

    if not catalog_name:
        return state, {"error": "catalog_name is required"}

    if catalog_name in state.catalogs:
        return state, {"error": f"Catalog '{catalog_name}' already exists"}

    new_catalog = Catalog(
        name=catalog_name, owner=owner, type=catalog_type, comment=comment
    )
    new_catalogs = {**state.catalogs, catalog_name: new_catalog}
    new_state = state.model_copy(update={"catalogs": new_catalogs})

    return new_state, {"success": True, "catalog": catalog_name}


def list_schemas(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """List schemas in a catalog."""
    catalog_name = args.get("catalog_name")
    if not catalog_name:
        return state, {"error": "catalog_name is required"}

    if catalog_name not in state.catalogs:
        return state, {"error": f"Catalog '{catalog_name}' does not exist"}

    schema_list = [
        {
            "catalog_name": schema.catalog_name,
            "schema_name": schema.schema_name,
            "owner": schema.owner,
            "comment": schema.comment,
        }
        for key, schema in state.schemas.items()
        if schema.catalog_name == catalog_name
    ]
    return state, {"schemas": schema_list}


def create_schema(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """Create a schema in a catalog."""
    catalog_name = args.get("catalog_name")
    schema_name = args.get("schema_name")
    owner = args.get("owner", "admin")
    comment = args.get("comment")

    if not catalog_name or not schema_name:
        return state, {"error": "catalog_name and schema_name are required"}

    if catalog_name not in state.catalogs:
        return state, {"error": f"Catalog '{catalog_name}' does not exist"}

    schema_key = state.get_schema_key(catalog_name, schema_name)
    if schema_key in state.schemas:
        return state, {"error": f"Schema '{schema_key}' already exists"}

    new_schema = Schema(
        catalog_name=catalog_name,
        schema_name=schema_name,
        owner=owner,
        comment=comment,
    )
    new_schemas = {**state.schemas, schema_key: new_schema}
    new_state = state.model_copy(update={"schemas": new_schemas})

    return new_state, {"success": True, "schema": schema_key}


def list_tables(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """List tables in a catalog.schema."""
    catalog_name = args.get("catalog_name")
    schema_name = args.get("schema_name")

    if not catalog_name or not schema_name:
        return state, {"error": "catalog_name and schema_name are required"}

    schema_key = state.get_schema_key(catalog_name, schema_name)
    if schema_key not in state.schemas:
        return state, {"error": f"Schema '{schema_key}' does not exist"}

    table_list = [
        {
            "catalog_name": table.catalog_name,
            "schema_name": table.schema_name,
            "table_name": table.table_name,
            "owner": table.owner,
            "column_count": len(table.columns),
        }
        for key, table in state.tables.items()
        if table.catalog_name == catalog_name and table.schema_name == schema_name
    ]
    return state, {"tables": table_list}


def create_table(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """Create a table with schema."""
    catalog_name = args.get("catalog_name")
    schema_name = args.get("schema_name")
    table_name = args.get("table_name")
    columns = args.get("columns", [])
    owner = args.get("owner", "admin")

    if not catalog_name or not schema_name or not table_name:
        return state, {
            "error": "catalog_name, schema_name, and table_name are required"
        }

    schema_key = state.get_schema_key(catalog_name, schema_name)
    if schema_key not in state.schemas:
        return state, {"error": f"Schema '{schema_key}' does not exist"}

    table_key = state.get_table_key(catalog_name, schema_name, table_name)
    if table_key in state.tables:
        return state, {"error": f"Table '{table_key}' already exists"}

    # Convert column dicts to Column objects
    from .state import Column

    column_objects = [
        Column(
            name=col.get("name"),
            type=col.get("type", "STRING"),
            nullable=col.get("nullable", True),
            comment=col.get("comment"),
        )
        for col in columns
    ]

    new_table = Table(
        catalog_name=catalog_name,
        schema_name=schema_name,
        table_name=table_name,
        columns=column_objects,
        owner=owner,
    )
    new_tables = {**state.tables, table_key: new_table}
    new_state = state.model_copy(update={"tables": new_tables})

    return new_state, {"success": True, "table": table_key}


def insert_into_table(
    state: DatabricksState, args: Dict
) -> Tuple[DatabricksState, Dict]:
    """Insert data rows into a table."""
    catalog_name = args.get("catalog_name")
    schema_name = args.get("schema_name")
    table_name = args.get("table_name")
    rows = args.get("rows", [])

    if not catalog_name or not schema_name or not table_name:
        return state, {
            "error": "catalog_name, schema_name, and table_name are required"
        }

    table_key = state.get_table_key(catalog_name, schema_name, table_name)
    if table_key not in state.tables:
        return state, {"error": f"Table '{table_key}' does not exist"}

    table = state.tables[table_key]
    if not rows:
        return state, {"error": "No rows provided"}

    # Convert rows to dicts matching column names
    column_names = [col.name for col in table.columns]
    new_rows = []
    for row in rows:
        if len(row) != len(column_names):
            return state, {
                "error": f"Row has {len(row)} values but table has {len(column_names)} columns"
            }
        new_rows.append(dict(zip(column_names, row)))

    # Update table with new data
    updated_data = list(table.data) + new_rows
    updated_table = table.model_copy(update={"data": updated_data})
    new_tables = {**state.tables, table_key: updated_table}
    new_state = state.model_copy(update={"tables": new_tables})

    return new_state, {"success": True, "rows_inserted": len(new_rows)}


def query_table(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """Query a table (SELECT operation)."""
    catalog_name = args.get("catalog_name")
    schema_name = args.get("schema_name")
    table_name = args.get("table_name")
    query = args.get("query")  # Optional filter query

    if not catalog_name or not schema_name or not table_name:
        return state, {
            "error": "catalog_name, schema_name, and table_name are required"
        }

    table_key = state.get_table_key(catalog_name, schema_name, table_name)
    if table_key not in state.tables:
        return state, {"error": f"Table '{table_key}' does not exist"}

    table = state.tables[table_key]
    results = list(table.data)

    # Simple filtering if query provided (basic implementation)
    # In a real system, this would parse SQL WHERE clauses
    if query:
        # For now, just return all data
        # TODO: Implement proper SQL parsing
        pass

    return state, {"results": results, "row_count": len(results)}


def grant_privilege(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """Grant a privilege to a principal."""
    privilege = args.get("privilege")
    securable_type = args.get("securable_type")
    securable_name = args.get("securable_name")
    principal = args.get("principal")

    if not all([privilege, securable_type, securable_name, principal]):
        return state, {
            "error": "privilege, securable_type, securable_name, and principal are required"
        }

    # Check if permission already exists
    existing_permission = next(
        (
            p
            for p in state.permissions
            if p.principal == principal
            and p.securable_name == securable_name
            and p.privilege == privilege
        ),
        None,
    )
    if existing_permission:
        return state, {"error": "Permission already granted"}

    new_permission = Permission(
        principal=principal,
        privilege=privilege,
        securable_type=securable_type,
        securable_name=securable_name,
    )
    new_permissions = list(state.permissions) + [new_permission]
    new_state = state.model_copy(update={"permissions": new_permissions})

    return new_state, {
        "success": True,
        "permission": f"{privilege} on {securable_name} to {principal}",
    }


def revoke_privilege(
    state: DatabricksState, args: Dict
) -> Tuple[DatabricksState, Dict]:
    """Revoke a privilege from a principal."""
    privilege = args.get("privilege")
    securable_name = args.get("securable_name")
    principal = args.get("principal")

    if not all([privilege, securable_name, principal]):
        return state, {"error": "privilege, securable_name, and principal are required"}

    new_permissions = [
        p
        for p in state.permissions
        if not (
            p.principal == principal
            and p.securable_name == securable_name
            and p.privilege == privilege
        )
    ]

    if len(new_permissions) == len(state.permissions):
        return state, {"error": "Permission not found"}

    new_state = state.model_copy(update={"permissions": new_permissions})
    return new_state, {"success": True}


def create_notebook(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """Create a notebook."""
    path = args.get("path")
    language = args.get("language", "python")

    if not path:
        return state, {"error": "path is required"}

    if path in state.notebooks:
        return state, {"error": f"Notebook '{path}' already exists"}

    new_notebook = Notebook(path=path, language=language)
    new_notebooks = {**state.notebooks, path: new_notebook}
    new_state = state.model_copy(update={"notebooks": new_notebooks})

    return new_state, {"success": True, "notebook": path}


def list_notebooks(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """List all notebooks."""
    notebook_list = [
        {
            "path": notebook.path,
            "language": notebook.language,
            "cell_count": len(notebook.cells),
            "attached_cluster": notebook.attached_cluster_id,
        }
        for notebook in state.notebooks.values()
    ]
    return state, {"notebooks": notebook_list}


def run_notebook_cell(
    state: DatabricksState, args: Dict
) -> Tuple[DatabricksState, Dict]:
    """Execute a notebook cell."""
    notebook_path = args.get("notebook_path")
    cell_content = args.get("cell_content")

    if not notebook_path or not cell_content:
        return state, {"error": "notebook_path and cell_content are required"}

    if notebook_path not in state.notebooks:
        return state, {"error": f"Notebook '{notebook_path}' does not exist"}

    notebook = state.notebooks[notebook_path]
    new_cells = list(notebook.cells) + [cell_content]
    updated_notebook = notebook.model_copy(update={"cells": new_cells})
    new_notebooks = {**state.notebooks, notebook_path: updated_notebook}
    new_state = state.model_copy(update={"notebooks": new_notebooks})

    return new_state, {"success": True, "cell_executed": True}


def create_visualization(
    state: DatabricksState, args: Dict
) -> Tuple[DatabricksState, Dict]:
    """Create a visualization in a notebook."""
    notebook_path = args.get("notebook_path")
    visualization_type = args.get("visualization_type", "bar")
    x_column = args.get("x_column")
    y_column = args.get("y_column")
    group_by = args.get("group_by")

    if not notebook_path:
        return state, {"error": "notebook_path is required"}

    if notebook_path not in state.notebooks:
        return state, {"error": f"Notebook '{notebook_path}' does not exist"}

    # Visualization is stored as metadata in notebook cells
    viz_cell = f"VISUALIZATION: type={visualization_type}, x={x_column}, y={y_column}, group_by={group_by}"
    notebook = state.notebooks[notebook_path]
    new_cells = list(notebook.cells) + [viz_cell]
    updated_notebook = notebook.model_copy(update={"cells": new_cells})
    new_notebooks = {**state.notebooks, notebook_path: updated_notebook}
    new_state = state.model_copy(update={"notebooks": new_notebooks})

    return new_state, {"success": True, "visualization_created": True}


def list_clusters(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """List all compute clusters."""
    cluster_list = [
        {
            "cluster_id": cluster.cluster_id,
            "name": cluster.name,
            "state": cluster.state,
            "node_type": cluster.node_type,
            "num_workers": cluster.num_workers,
        }
        for cluster in state.clusters.values()
    ]
    return state, {"clusters": cluster_list}


def create_cluster(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """Create a compute cluster."""
    import uuid

    name = args.get("name")
    node_type = args.get("node_type", "i3.xlarge")
    num_workers = args.get("num_workers", 1)
    spark_version = args.get("spark_version", "13.3.x-scala2.12")

    if not name:
        return state, {"error": "name is required"}

    cluster_id = str(uuid.uuid4())
    new_cluster = Cluster(
        cluster_id=cluster_id,
        name=name,
        state="RUNNING",
        node_type=node_type,
        num_workers=num_workers,
        spark_version=spark_version,
    )
    new_clusters = {**state.clusters, cluster_id: new_cluster}
    new_state = state.model_copy(update={"clusters": new_clusters})

    return new_state, {"success": True, "cluster_id": cluster_id}


def attach_to_cluster(
    state: DatabricksState, args: Dict
) -> Tuple[DatabricksState, Dict]:
    """Attach a notebook to a cluster."""
    notebook_path = args.get("notebook_path")
    cluster_id = args.get("cluster_id")

    if not notebook_path or not cluster_id:
        return state, {"error": "notebook_path and cluster_id are required"}

    if notebook_path not in state.notebooks:
        return state, {"error": f"Notebook '{notebook_path}' does not exist"}

    if cluster_id not in state.clusters:
        return state, {"error": f"Cluster '{cluster_id}' does not exist"}

    notebook = state.notebooks[notebook_path]
    updated_notebook = notebook.model_copy(update={"attached_cluster_id": cluster_id})
    new_notebooks = {**state.notebooks, notebook_path: updated_notebook}
    new_state = state.model_copy(update={"notebooks": new_notebooks})

    return new_state, {"success": True, "attached": True}


def list_jobs(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """List all scheduled jobs."""
    job_list = [
        {
            "job_id": job.job_id,
            "name": job.name,
            "schedule": job.schedule,
            "task_count": len(job.tasks),
        }
        for job in state.jobs.values()
    ]
    return state, {"jobs": job_list}


def create_job(state: DatabricksState, args: Dict) -> Tuple[DatabricksState, Dict]:
    """Create a scheduled job."""
    import uuid

    name = args.get("name")
    schedule = args.get("schedule")
    tasks = args.get("tasks", [])

    if not name:
        return state, {"error": "name is required"}

    job_id = str(uuid.uuid4())
    new_job = Job(job_id=job_id, name=name, schedule=schedule, tasks=tasks)
    new_jobs = {**state.jobs, job_id: new_job}
    new_state = state.model_copy(update={"jobs": new_jobs})

    return new_state, {"success": True, "job_id": job_id}
