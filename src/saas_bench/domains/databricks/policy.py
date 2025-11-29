"""Policy document and validation for Databricks operations."""

import re
from typing import Dict

from .state import DatabricksState


class Policy:
    """Policy validation for Databricks operations."""

    MAX_CATALOG_NAME_LENGTH = 255
    MAX_SCHEMA_NAME_LENGTH = 255
    MAX_TABLE_NAME_LENGTH = 255
    MAX_CLUSTERS_PER_WORKSPACE = 100

    @staticmethod
    def validate_catalog_name(name: str) -> tuple[bool, str]:
        """Validate catalog name against naming conventions."""
        if not name:
            return False, "Catalog name cannot be empty"
        if len(name) > Policy.MAX_CATALOG_NAME_LENGTH:
            return False, f"Catalog name exceeds maximum length of {Policy.MAX_CATALOG_NAME_LENGTH}"
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Catalog name must contain only alphanumeric characters and underscores"
        return True, ""

    @staticmethod
    def validate_schema_name(name: str) -> tuple[bool, str]:
        """Validate schema name against naming conventions."""
        if not name:
            return False, "Schema name cannot be empty"
        if len(name) > Policy.MAX_SCHEMA_NAME_LENGTH:
            return False, f"Schema name exceeds maximum length of {Policy.MAX_SCHEMA_NAME_LENGTH}"
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Schema name must contain only alphanumeric characters and underscores"
        return True, ""

    @staticmethod
    def validate_table_name(name: str) -> tuple[bool, str]:
        """Validate table name against naming conventions."""
        if not name:
            return False, "Table name cannot be empty"
        if len(name) > Policy.MAX_TABLE_NAME_LENGTH:
            return False, f"Table name exceeds maximum length of {Policy.MAX_TABLE_NAME_LENGTH}"
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Table name must contain only alphanumeric characters and underscores"
        return True, ""

    @staticmethod
    def validate_cluster_count(state: DatabricksState) -> tuple[bool, str]:
        """Validate that cluster count doesn't exceed limit."""
        if len(state.clusters) >= Policy.MAX_CLUSTERS_PER_WORKSPACE:
            return False, f"Maximum number of clusters ({Policy.MAX_CLUSTERS_PER_WORKSPACE}) exceeded"
        return True, ""

    @staticmethod
    def validate_action(state: DatabricksState, action: Dict) -> tuple[bool, str]:
        """Validate if an action violates policy."""
        action_type = action.get("type")
        args = action.get("args", {})

        if action_type == "create_catalog":
            catalog_name = args.get("catalog_name")
            if catalog_name:
                valid, msg = Policy.validate_catalog_name(catalog_name)
                if not valid:
                    return False, msg

        elif action_type == "create_schema":
            schema_name = args.get("schema_name")
            if schema_name:
                valid, msg = Policy.validate_schema_name(schema_name)
                if not valid:
                    return False, msg

        elif action_type == "create_table":
            table_name = args.get("table_name")
            if table_name:
                valid, msg = Policy.validate_table_name(table_name)
                if not valid:
                    return False, msg

        elif action_type == "create_cluster":
            valid, msg = Policy.validate_cluster_count(state)
            if not valid:
                return False, msg

        return True, ""

    @staticmethod
    def get_policy_document() -> str:
        """Return policy document text for agents."""
        return """# Databricks Workspace Policy

## Naming Conventions

### Catalogs
- Names must contain only alphanumeric characters and underscores
- Maximum length: 255 characters
- Examples: `main`, `sales_data`, `analytics_2024`

### Schemas
- Names must contain only alphanumeric characters and underscores
- Maximum length: 255 characters
- Examples: `default`, `staging`, `production`

### Tables
- Names must contain only alphanumeric characters and underscores
- Maximum length: 255 characters
- Examples: `customers`, `orders_2024`, `user_profiles`

## Unity Catalog Requirements

### Hierarchy
- Tables must be created within an existing catalog and schema
- Full table name format: `catalog.schema.table`
- Permissions follow the catalog → schema → table hierarchy

### Ownership
- Resources are owned by the creator by default
- Only owners can grant permissions on their resources
- Ownership can be transferred (not covered in this policy)

## Compute Usage Limits

### Clusters
- Maximum clusters per workspace: 100
- Cluster names should follow naming conventions
- Clusters should be terminated when not in use to save costs

## Security Constraints

### Permissions
- Permissions are granted at the catalog, schema, or table level
- Common privileges: SELECT, INSERT, MODIFY, ALL_PRIVILEGES
- Only resource owners can grant permissions
- Permissions cascade appropriately (catalog permissions apply to schemas and tables)

### Best Practices
- Use least privilege principle
- Grant only necessary permissions
- Regularly review and audit permissions
- Use groups for permission management when possible

## Data Quality

### Tables
- Tables should have descriptive column names
- Use appropriate data types for columns
- Add comments to tables and columns for documentation
- Validate data before insertion

## Operational Guidelines

### Notebooks
- Use descriptive notebook paths
- Attach notebooks to appropriate clusters
- Clean up unused notebooks regularly

### Jobs
- Use descriptive job names
- Set appropriate schedules for recurring jobs
- Monitor job execution and failures
"""

