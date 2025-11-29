"""Tool registry for Databricks API tools."""

from typing import Callable, Dict

from . import tools

# Map tool names to their functions
TOOL_REGISTRY: Dict[str, Callable] = {
    "use_catalog": tools.use_catalog,
    "list_catalogs": tools.list_catalogs,
    "create_catalog": tools.create_catalog,
    "list_schemas": tools.list_schemas,
    "create_schema": tools.create_schema,
    "list_tables": tools.list_tables,
    "create_table": tools.create_table,
    "insert_into_table": tools.insert_into_table,
    "query_table": tools.query_table,
    "grant_privilege": tools.grant_privilege,
    "revoke_privilege": tools.revoke_privilege,
    "create_notebook": tools.create_notebook,
    "list_notebooks": tools.list_notebooks,
    "run_notebook_cell": tools.run_notebook_cell,
    "create_visualization": tools.create_visualization,
    "list_clusters": tools.list_clusters,
    "create_cluster": tools.create_cluster,
    "attach_to_cluster": tools.attach_to_cluster,
    "list_jobs": tools.list_jobs,
    "create_job": tools.create_job,
}


def get_tool_spec(tool_name: str) -> Dict:
    """Get tool specification including parameters schema."""
    specs = {
        "use_catalog": {
            "name": "use_catalog",
            "description": "Set the active catalog context",
            "parameters": {
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "Name of the catalog to use"},
                },
                "required": ["catalog_name"],
            },
        },
        "list_catalogs": {
            "name": "list_catalogs",
            "description": "List all catalogs in the workspace",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        "create_catalog": {
            "name": "create_catalog",
            "description": "Create a new Unity Catalog catalog",
            "parameters": {
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "Name of the catalog"},
                    "owner": {"type": "string", "description": "Owner of the catalog", "default": "admin"},
                    "comment": {"type": "string", "description": "Comment describing the catalog"},
                },
                "required": ["catalog_name"],
            },
        },
        "list_schemas": {
            "name": "list_schemas",
            "description": "List all schemas in a catalog",
            "parameters": {
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "Name of the catalog"},
                },
                "required": ["catalog_name"],
            },
        },
        "create_schema": {
            "name": "create_schema",
            "description": "Create a schema in a catalog",
            "parameters": {
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "Name of the catalog"},
                    "schema_name": {"type": "string", "description": "Name of the schema"},
                    "owner": {"type": "string", "description": "Owner of the schema", "default": "admin"},
                    "comment": {"type": "string", "description": "Comment describing the schema"},
                },
                "required": ["catalog_name", "schema_name"],
            },
        },
        "list_tables": {
            "name": "list_tables",
            "description": "List all tables in a catalog.schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "Name of the catalog"},
                    "schema_name": {"type": "string", "description": "Name of the schema"},
                },
                "required": ["catalog_name", "schema_name"],
            },
        },
        "create_table": {
            "name": "create_table",
            "description": "Create a table with schema in a catalog.schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "Name of the catalog"},
                    "schema_name": {"type": "string", "description": "Name of the schema"},
                    "table_name": {"type": "string", "description": "Name of the table"},
                    "columns": {
                        "type": "array",
                        "description": "List of column definitions",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string", "default": "STRING"},
                                "nullable": {"type": "boolean", "default": True},
                                "comment": {"type": "string"},
                            },
                            "required": ["name"],
                        },
                    },
                    "owner": {"type": "string", "description": "Owner of the table", "default": "admin"},
                },
                "required": ["catalog_name", "schema_name", "table_name", "columns"],
            },
        },
        "insert_into_table": {
            "name": "insert_into_table",
            "description": "Insert data rows into a table",
            "parameters": {
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "Name of the catalog"},
                    "schema_name": {"type": "string", "description": "Name of the schema"},
                    "table_name": {"type": "string", "description": "Name of the table"},
                    "rows": {
                        "type": "array",
                        "description": "List of rows to insert (each row is a list of values)",
                        "items": {"type": "array"},
                    },
                },
                "required": ["catalog_name", "schema_name", "table_name", "rows"],
            },
        },
        "query_table": {
            "name": "query_table",
            "description": "Query a table (SELECT operation)",
            "parameters": {
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "Name of the catalog"},
                    "schema_name": {"type": "string", "description": "Name of the schema"},
                    "table_name": {"type": "string", "description": "Name of the table"},
                    "query": {"type": "string", "description": "Optional filter query"},
                },
                "required": ["catalog_name", "schema_name", "table_name"],
            },
        },
        "grant_privilege": {
            "name": "grant_privilege",
            "description": "Grant a privilege to a principal on a securable",
            "parameters": {
                "type": "object",
                "properties": {
                    "privilege": {
                        "type": "string",
                        "description": "Privilege to grant (e.g., SELECT, INSERT, ALL_PRIVILEGES)",
                    },
                    "securable_type": {
                        "type": "string",
                        "description": "Type of securable (TABLE, CATALOG, SCHEMA)",
                    },
                    "securable_name": {
                        "type": "string",
                        "description": "Full name of securable (e.g., catalog.schema.table)",
                    },
                    "principal": {"type": "string", "description": "User or group name"},
                },
                "required": ["privilege", "securable_type", "securable_name", "principal"],
            },
        },
        "revoke_privilege": {
            "name": "revoke_privilege",
            "description": "Revoke a privilege from a principal",
            "parameters": {
                "type": "object",
                "properties": {
                    "privilege": {"type": "string", "description": "Privilege to revoke"},
                    "securable_name": {"type": "string", "description": "Full name of securable"},
                    "principal": {"type": "string", "description": "User or group name"},
                },
                "required": ["privilege", "securable_name", "principal"],
            },
        },
        "create_notebook": {
            "name": "create_notebook",
            "description": "Create a new notebook",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the notebook"},
                    "language": {
                        "type": "string",
                        "description": "Notebook language",
                        "enum": ["sql", "python", "scala", "r"],
                        "default": "python",
                    },
                },
                "required": ["path"],
            },
        },
        "list_notebooks": {
            "name": "list_notebooks",
            "description": "List all notebooks",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        "run_notebook_cell": {
            "name": "run_notebook_cell",
            "description": "Execute a notebook cell",
            "parameters": {
                "type": "object",
                "properties": {
                    "notebook_path": {"type": "string", "description": "Path to the notebook"},
                    "cell_content": {"type": "string", "description": "Content of the cell to execute"},
                },
                "required": ["notebook_path", "cell_content"],
            },
        },
        "create_visualization": {
            "name": "create_visualization",
            "description": "Create a visualization in a notebook",
            "parameters": {
                "type": "object",
                "properties": {
                    "notebook_path": {"type": "string", "description": "Path to the notebook"},
                    "visualization_type": {
                        "type": "string",
                        "description": "Type of visualization",
                        "enum": ["bar", "line", "pie", "scatter"],
                        "default": "bar",
                    },
                    "x_column": {"type": "string", "description": "Column for X axis"},
                    "y_column": {"type": "string", "description": "Column for Y axis"},
                    "group_by": {"type": "string", "description": "Column to group by"},
                },
                "required": ["notebook_path"],
            },
        },
        "list_clusters": {
            "name": "list_clusters",
            "description": "List all compute clusters",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        "create_cluster": {
            "name": "create_cluster",
            "description": "Create a compute cluster",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the cluster"},
                    "node_type": {"type": "string", "description": "Node type", "default": "i3.xlarge"},
                    "num_workers": {"type": "integer", "description": "Number of worker nodes", "default": 1},
                    "spark_version": {"type": "string", "description": "Spark version", "default": "13.3.x-scala2.12"},
                },
                "required": ["name"],
            },
        },
        "attach_to_cluster": {
            "name": "attach_to_cluster",
            "description": "Attach a notebook to a cluster",
            "parameters": {
                "type": "object",
                "properties": {
                    "notebook_path": {"type": "string", "description": "Path to the notebook"},
                    "cluster_id": {"type": "string", "description": "ID of the cluster"},
                },
                "required": ["notebook_path", "cluster_id"],
            },
        },
        "list_jobs": {
            "name": "list_jobs",
            "description": "List all scheduled jobs",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        "create_job": {
            "name": "create_job",
            "description": "Create a scheduled job",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the job"},
                    "schedule": {"type": "string", "description": "Cron expression for schedule"},
                    "tasks": {
                        "type": "array",
                        "description": "List of tasks for the job",
                        "items": {"type": "object"},
                    },
                },
                "required": ["name"],
            },
        },
    }

    if tool_name not in specs:
        raise ValueError(f"Unknown tool: {tool_name}")

    return specs[tool_name]


def get_all_tool_specs() -> list[Dict]:
    """Get specifications for all tools."""
    return [get_tool_spec(name) for name in TOOL_REGISTRY.keys()]

