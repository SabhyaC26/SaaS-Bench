"""Environment class for orchestrating agent-user-API interaction."""

from typing import Dict, List

from ..domains.databricks.registry import TOOL_REGISTRY, get_all_tool_specs
from ..domains.databricks.state import DatabricksState


class Environment:
    """Orchestrates state transitions and tool execution."""

    def __init__(self, initial_state: DatabricksState | None = None):
        """Initialize environment with optional initial state."""
        self._state = initial_state or DatabricksState()
        self._conversation_history: List[Dict] = []
        self._state_snapshots: List[DatabricksState] = [self._state]

    def execute_tool(self, tool_name: str, args: Dict) -> Dict:
        """Execute a tool and update state."""
        if tool_name not in TOOL_REGISTRY:
            return {"error": f"Unknown tool: {tool_name}"}

        tool_func = TOOL_REGISTRY[tool_name]

        # Execute tool function
        try:
            new_state, response = tool_func(self._state, args)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

        # Update state immutably
        self._state = new_state
        self._state_snapshots.append(new_state)

        # Record in conversation history
        self._conversation_history.append(
            {
                "type": "tool_call",
                "tool": tool_name,
                "args": args,
                "response": response,
            }
        )

        return response

    def get_state(self) -> DatabricksState:
        """Get current state."""
        return self._state

    def reset(self, initial_state: DatabricksState | None = None):
        """Reset environment to initial state."""
        self._state = initial_state or DatabricksState()
        self._conversation_history = []
        self._state_snapshots = [self._state]

    def get_tool_specs(self) -> List[Dict]:
        """Get specifications for all available tools."""
        return get_all_tool_specs()

    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self._conversation_history.copy()

    def get_state_snapshots(self) -> List[DatabricksState]:
        """Get state snapshots for debugging."""
        return self._state_snapshots.copy()

    def add_user_message(self, message: str):
        """Add a user message to conversation history."""
        self._conversation_history.append({"type": "user_message", "content": message})

    def add_agent_message(self, message: str):
        """Add an agent message to conversation history."""
        self._conversation_history.append({"type": "agent_message", "content": message})

