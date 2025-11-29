"""Tests for Environment class."""

from saas_bench.core.environment import Environment
from saas_bench.domains.databricks.state import DatabricksState


def test_environment_initialization():
    """Test environment initialization."""
    env = Environment()
    assert env.get_state() is not None
    assert len(env.get_conversation_history()) == 0


def test_execute_tool():
    """Test executing a tool."""
    env = Environment()
    response = env.execute_tool("create_catalog", {"catalog_name": "test_catalog"})

    assert response["success"] is True
    assert "test_catalog" in env.get_state().catalogs


def test_conversation_history():
    """Test conversation history tracking."""
    env = Environment()
    env.add_user_message("Create a catalog called test")
    env.execute_tool("create_catalog", {"catalog_name": "test_catalog"})

    history = env.get_conversation_history()
    assert len(history) == 2
    assert history[0]["type"] == "user_message"
    assert history[1]["type"] == "tool_call"


def test_reset():
    """Test resetting environment."""
    env = Environment()
    env.execute_tool("create_catalog", {"catalog_name": "test_catalog"})
    assert len(env.get_state().catalogs) == 1

    env.reset()
    assert len(env.get_state().catalogs) == 0
    assert len(env.get_conversation_history()) == 0


def test_get_tool_specs():
    """Test getting tool specifications."""
    env = Environment()
    specs = env.get_tool_specs()

    assert len(specs) > 0
    assert any(spec["name"] == "create_catalog" for spec in specs)

