"""Tests for Databricks API tools."""

import pytest

from saas_bench.domains.databricks.state import DatabricksState
from saas_bench.domains.databricks import tools


def test_create_catalog():
    """Test creating a catalog."""
    state = DatabricksState()
    new_state, response = tools.create_catalog(state, {"catalog_name": "test_catalog"})

    assert response["success"] is True
    assert "test_catalog" in new_state.catalogs
    assert len(new_state.catalogs) == 1


def test_create_catalog_duplicate():
    """Test creating duplicate catalog fails."""
    state = DatabricksState()
    state, _ = tools.create_catalog(state, {"catalog_name": "test_catalog"})
    _, response = tools.create_catalog(state, {"catalog_name": "test_catalog"})

    assert "error" in response
    assert "already exists" in response["error"]


def test_create_schema():
    """Test creating a schema."""
    state = DatabricksState()
    state, _ = tools.create_catalog(state, {"catalog_name": "test_catalog"})
    new_state, response = tools.create_schema(
        state, {"catalog_name": "test_catalog", "schema_name": "default"}
    )

    assert response["success"] is True
    assert "test_catalog.default" in new_state.schemas


def test_create_schema_missing_catalog():
    """Test creating schema without catalog fails."""
    state = DatabricksState()
    _, response = tools.create_schema(
        state, {"catalog_name": "nonexistent", "schema_name": "default"}
    )

    assert "error" in response
    assert "does not exist" in response["error"]


def test_create_table():
    """Test creating a table."""
    state = DatabricksState()
    state, _ = tools.create_catalog(state, {"catalog_name": "test_catalog"})
    state, _ = tools.create_schema(
        state, {"catalog_name": "test_catalog", "schema_name": "default"}
    )

    columns = [{"name": "id", "type": "INT"}, {"name": "name", "type": "STRING"}]
    new_state, response = tools.create_table(
        state,
        {
            "catalog_name": "test_catalog",
            "schema_name": "default",
            "table_name": "users",
            "columns": columns,
        },
    )

    assert response["success"] is True
    assert "test_catalog.default.users" in new_state.tables


def test_insert_into_table():
    """Test inserting data into a table."""
    state = DatabricksState()
    state, _ = tools.create_catalog(state, {"catalog_name": "test_catalog"})
    state, _ = tools.create_schema(
        state, {"catalog_name": "test_catalog", "schema_name": "default"}
    )
    state, _ = tools.create_table(
        state,
        {
            "catalog_name": "test_catalog",
            "schema_name": "default",
            "table_name": "users",
            "columns": [{"name": "id", "type": "INT"}, {"name": "name", "type": "STRING"}],
        },
    )

    rows = [[1, "Alice"], [2, "Bob"]]
    new_state, response = tools.insert_into_table(
        state,
        {
            "catalog_name": "test_catalog",
            "schema_name": "default",
            "table_name": "users",
            "rows": rows,
        },
    )

    assert response["success"] is True
    assert response["rows_inserted"] == 2
    table = new_state.tables["test_catalog.default.users"]
    assert len(table.data) == 2


def test_grant_privilege():
    """Test granting a privilege."""
    state = DatabricksState()
    state, _ = tools.create_catalog(state, {"catalog_name": "test_catalog"})
    state, _ = tools.create_schema(
        state, {"catalog_name": "test_catalog", "schema_name": "default"}
    )
    state, _ = tools.create_table(
        state,
        {
            "catalog_name": "test_catalog",
            "schema_name": "default",
            "table_name": "users",
            "columns": [{"name": "id", "type": "INT"}],
        },
    )

    new_state, response = tools.grant_privilege(
        state,
        {
            "privilege": "SELECT",
            "securable_type": "TABLE",
            "securable_name": "test_catalog.default.users",
            "principal": "data_consumers",
        },
    )

    assert response["success"] is True
    assert len(new_state.permissions) == 1
    assert new_state.permissions[0].privilege == "SELECT"

