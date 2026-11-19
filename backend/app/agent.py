"""Mock LLM agent for the prototype.

Maps a natural-language instruction to proposed tool calls.
In the final version this calls the OpenAI API with function/tool calling;
for now it uses a deterministic keyword-based MOCK that returns realistic proposals.
"""

from typing import Any

MOCK_AGENT_NAME = "mock-agent-v1"

MOCK_TOOLS = [
    {
        "name": "schedule_study_session",
        "description": "Schedule a focused study session for a topic",
        "keywords": ["schedule", "study", "session", "sprint", "plan", "calendar"],
    },
    {
        "name": "generate_quiz",
        "description": "Generate a practice quiz for a topic",
        "keywords": ["quiz", "test", "practice", "exam"],
    },
    {
        "name": "draft_learning_plan",
        "description": "Draft a learning plan / roadmap",
        "keywords": ["plan", "roadmap", "path", "roadmap"],
    },
]


def propose_actions(instruction: str, max_actions: int = 3) -> list[dict[str, Any]]:
    """Return 1-3 proposed tool calls for the instruction (MOCK)."""
    lowered = instruction.lower()
    actions: list[dict[str, Any]] = []

    for tool in MOCK_TOOLS:
        if any(k in lowered for k in tool["keywords"]):
            actions.append(
                {
                    "tool_name": tool["name"],
                    "tool_args": {
                        "instruction": instruction,
                        "topic": instruction,
                        "max_questions": 5,
                    },
                    "rationale": f"MOCK: instruction keywords matched tool '{tool['name']}'",
                }
            )
            if len(actions) >= max_actions:
                break

    if not actions:
        actions.append(
            {
                "tool_name": "draft_learning_plan",
                "tool_args": {"instruction": instruction},
                "rationale": "MOCK: fallback - no keyword match, default plan tool",
            }
        )

    return actions


def execute_tool(tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
    """MOCK executor: pretends to execute the tool action."""
    return {
        "status": "simulated",
        "tool": tool_name,
        "args": tool_args,
        "message": f"MOCK executor: would execute '{tool_name}'",
    }
