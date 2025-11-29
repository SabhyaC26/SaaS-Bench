"""Tests for Databricks state schema."""

import pytest

from saas_bench.domains.databricks.state import (
    Catalog,
    Column,
    DatabricksState,
    Schema,
    Table,
)


def test_catalog_creation():
    """Test creating a catalog."""
    catalog = Catalog(name="test_catalog", owner="admin", comment="Test catalog")
    assert catalog.name == "test_catalog"
    assert catalog.owner == "admin"
    assert catalog.comment == "Test catalog"


def test_schema_creation():
    """Test creating a schema."""
    schema = Schema(catalog_name="test_catalog", schema_name="default", owner="admin")
    assert schema.catalog_name == "test_catalog"
    assert schema.schema_name == "default"


def test_table_creation():
    """Test creating a table with columns."""
    columns = [
        Column(name="id", type="INT", nullable=False),
        Column(name="name", type="STRING", nullable=True),
    ]
    table = Table(
        catalog_name="test_catalog",
        schema_name="default",
        table_name="users",
        columns=columns,
        owner="admin",
    )
    assert table.table_name == "users"
    assert len(table.columns) == 2
    assert table.columns[0].name == "id"


def test_databricks_state():
    """Test DatabricksState container."""
    state = DatabricksState()
    assert len(state.catalogs) == 0
    assert len(state.tables) == 0

    # Test schema key generation
    assert state.get_schema_key("catalog1", "schema1") == "catalog1.schema1"

    # Test table key generation
    assert state.get_table_key("catalog1", "schema1", "table1") == "catalog1.schema1.table1"


def test_state_immutability():
    """Test that state updates create new objects."""
    state1 = DatabricksState()
    catalog = Catalog(name="test", owner="admin")

    # Create new state with catalog
    state2 = state1.model_copy(update={"catalogs": {"test": catalog}})

    assert len(state1.catalogs) == 0
    assert len(state2.catalogs) == 1
    assert state1 is not state2

