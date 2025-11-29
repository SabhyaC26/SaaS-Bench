"""Tests for evaluation logic."""

from saas_bench.core.evaluation import evaluate_task
from saas_bench.domains.databricks.state import Catalog, DatabricksState, Table
from saas_bench.domains.databricks.state import Column


def test_evaluation_success():
    """Test successful evaluation."""
    # Create goal state
    goal_state = DatabricksState()
    goal_state = goal_state.model_copy(
        update={
            "catalogs": {
                "test_catalog": Catalog(name="test_catalog", owner="admin"),
            }
        }
    )

    # Create final state matching goal
    final_state = DatabricksState()
    final_state = final_state.model_copy(
        update={
            "catalogs": {
                "test_catalog": Catalog(name="test_catalog", owner="admin"),
            }
        }
    )

    result = evaluate_task(final_state, goal_state)
    assert result.success is True
    assert result.score == 1.0


def test_evaluation_missing_resource():
    """Test evaluation with missing resources."""
    # Create goal state with catalog
    goal_state = DatabricksState()
    goal_state = goal_state.model_copy(
        update={
            "catalogs": {
                "test_catalog": Catalog(name="test_catalog", owner="admin"),
            }
        }
    )

    # Create final state without catalog
    final_state = DatabricksState()

    result = evaluate_task(final_state, goal_state)
    assert result.success is False
    assert result.score < 1.0
    assert len(result.differences["missing_catalogs"]) > 0


def test_evaluation_table_schema_mismatch():
    """Test evaluation with incorrect table schema."""
    # Create goal state with table
    goal_state = DatabricksState()
    goal_table = Table(
        catalog_name="test_catalog",
        schema_name="default",
        table_name="users",
        columns=[Column(name="id", type="INT"), Column(name="name", type="STRING")],
        owner="admin",
    )
    goal_state = goal_state.model_copy(
        update={"tables": {"test_catalog.default.users": goal_table}}
    )

    # Create final state with different schema
    final_state = DatabricksState()
    final_table = Table(
        catalog_name="test_catalog",
        schema_name="default",
        table_name="users",
        columns=[Column(name="id", type="STRING")],  # Wrong type
        owner="admin",
    )
    final_state = final_state.model_copy(
        update={"tables": {"test_catalog.default.users": final_table}}
    )

    result = evaluate_task(final_state, goal_state)
    assert result.success is False
    assert len(result.differences["incorrect_tables"]) > 0

