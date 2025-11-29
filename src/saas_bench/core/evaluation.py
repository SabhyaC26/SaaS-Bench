"""Evaluation logic for comparing final state to goal state."""

from typing import Dict, List

from pydantic import BaseModel

from ..domains.databricks.state import DatabricksState


class EvaluationResult(BaseModel):
    """Result of task evaluation."""

    success: bool
    score: float  # 0.0-1.0
    milestones_achieved: List[str]
    minefields_triggered: List[str]
    differences: Dict

    model_config = {"frozen": True}


def evaluate_task(
    final_state: DatabricksState, goal_state: DatabricksState
) -> EvaluationResult:
    """Compare final state to goal state and determine success."""
    differences: Dict = {
        "missing_catalogs": [],
        "missing_schemas": [],
        "missing_tables": [],
        "missing_notebooks": [],
        "missing_permissions": [],
        "incorrect_tables": [],
        "extra_resources": {},
    }
    milestones_achieved: List[str] = []
    minefields_triggered: List[str] = []

    # Check catalogs
    for catalog_name, goal_catalog in goal_state.catalogs.items():
        if catalog_name not in final_state.catalogs:
            differences["missing_catalogs"].append(catalog_name)
        else:
            milestones_achieved.append(f"Catalog '{catalog_name}' exists")

    # Check schemas
    for schema_key, goal_schema in goal_state.schemas.items():
        if schema_key not in final_state.schemas:
            differences["missing_schemas"].append(schema_key)
        else:
            milestones_achieved.append(f"Schema '{schema_key}' exists")

    # Check tables
    for table_key, goal_table in goal_state.tables.items():
        if table_key not in final_state.tables:
            differences["missing_tables"].append(table_key)
        else:
            final_table = final_state.tables[table_key]
            # Check table schema (columns)
            goal_columns = {col.name: col for col in goal_table.columns}
            final_columns = {col.name: col for col in final_table.columns}

            if goal_columns != final_columns:
                differences["incorrect_tables"].append(
                    {
                        "table": table_key,
                        "issue": "Column schema mismatch",
                        "expected": {name: col.type for name, col in goal_columns.items()},
                        "actual": {name: col.type for name, col in final_columns.items()},
                    }
                )
            else:
                milestones_achieved.append(f"Table '{table_key}' created with correct schema")

            # Check table data (if goal state specifies data)
            if goal_table.data:
                if len(final_table.data) < len(goal_table.data):
                    differences["incorrect_tables"].append(
                        {
                            "table": table_key,
                            "issue": "Insufficient data rows",
                            "expected_rows": len(goal_table.data),
                            "actual_rows": len(final_table.data),
                        }
                    )
                else:
                    milestones_achieved.append(f"Table '{table_key}' has data inserted")

    # Check notebooks
    for notebook_path, goal_notebook in goal_state.notebooks.items():
        if notebook_path not in final_state.notebooks:
            differences["missing_notebooks"].append(notebook_path)
        else:
            milestones_achieved.append(f"Notebook '{notebook_path}' created")

    # Check permissions
    goal_permissions = {
        (p.principal, p.privilege, p.securable_name) for p in goal_state.permissions
    }
    final_permissions = {
        (p.principal, p.privilege, p.securable_name) for p in final_state.permissions
    }

    missing_perms = goal_permissions - final_permissions
    if missing_perms:
        differences["missing_permissions"] = [
            f"{principal} - {privilege} on {securable}" for principal, privilege, securable in missing_perms
        ]
    else:
        milestones_achieved.append("All required permissions granted")

    # Check for extra resources (optional - may want to allow extras)
    extra_catalogs = set(final_state.catalogs.keys()) - set(goal_state.catalogs.keys())
    extra_tables = set(final_state.tables.keys()) - set(goal_state.tables.keys())
    if extra_catalogs or extra_tables:
        differences["extra_resources"] = {
            "catalogs": list(extra_catalogs),
            "tables": list(extra_tables),
        }

    # Calculate success
    has_missing_resources = (
        differences["missing_catalogs"]
        or differences["missing_schemas"]
        or differences["missing_tables"]
        or differences["missing_notebooks"]
    )
    has_incorrect_tables = bool(differences["incorrect_tables"])
    has_missing_permissions = bool(differences["missing_permissions"])

    success = not (has_missing_resources or has_incorrect_tables or has_missing_permissions)

    # Calculate score (partial credit)
    total_checks = (
        len(goal_state.catalogs)
        + len(goal_state.schemas)
        + len(goal_state.tables)
        + len(goal_state.notebooks)
        + len(goal_state.permissions)
    )
    passed_checks = len(milestones_achieved)
    score = passed_checks / total_checks if total_checks > 0 else 1.0

    # Check for minefields (critical violations)
    # Example: Wrong permissions granted
    extra_perms = final_permissions - goal_permissions
    if extra_perms:
        minefields_triggered.append(
            f"Unexpected permissions granted: {extra_perms}"
        )

    return EvaluationResult(
        success=success,
        score=score,
        milestones_achieved=milestones_achieved,
        minefields_triggered=minefields_triggered,
        differences=differences,
    )

