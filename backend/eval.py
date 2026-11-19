"""Evaluation harness for the mock agent.

Runs N sample instructions through the agent and computes tool-selection accuracy.
"""

import json
from pathlib import Path
from typing import Any

from app.agent import propose_actions

EVAL_CASES: list[tuple[str, str]] = [
    # (instruction, expected_tool)
    ("schedule a study session for sql joins", "schedule_study_session"),
    ("plan a 4 week learning roadmap for ml", "draft_learning_plan"),
    ("create a practice quiz for python", "generate_quiz"),
    ("schedule a sprint study session for react hooks", "schedule_study_session"),
    ("draft a study plan for system design", "draft_learning_plan"),
    ("generate quiz for docker internals", "generate_quiz"),
    ("schedule study session for algorithms", "schedule_study_session"),
    ("make a practice exam for databases", "generate_quiz"),
    ("plan my interview prep roadmap", "draft_learning_plan"),
    ("schedule a focused session for networking", "schedule_study_session"),
    ("generate quiz for operating systems", "generate_quiz"),
    ("plan deep learning study roadmap", "draft_learning_plan"),
    ("schedule study session for git", "schedule_study_session"),
    ("practice quiz for python oop", "generate_quiz"),
    ("draft learning path for cloud computing", "draft_learning_plan"),
    ("schedule session for math fundamentals", "schedule_study_session"),
    ("make exam for sql", "generate_quiz"),
    ("plan data science learning roadmap", "draft_learning_plan"),
    ("schedule study sprint for security", "schedule_study_session"),
    ("practice quiz for linux", "generate_quiz"),
]


def run_eval() -> dict[str, Any]:
    results = []
    for i, (instruction, expected_tool) in enumerate(EVAL_CASES, start=1):
        actions = propose_actions(instruction)
        proposed_tools = sorted({a["tool_name"] for a in actions})
        correct = expected_tool in proposed_tools
        results.append(
            {
                "id": i,
                "instruction": instruction,
                "expected_tool": expected_tool,
                "proposed_tools": proposed_tools,
                "correct": correct,
            }
        )

    correct_count = sum(1 for r in results if r["correct"])
    accuracy = correct_count / len(results) if results else 0.0
    return {
        "total": len(results),
        "correct": correct_count,
        "accuracy": accuracy,
        "results": results,
    }


if __name__ == "__main__":
    out = run_eval()
    print(f"Agent accuracy: {out['correct']}/{out['total']} = {out['accuracy']:.2%}")
    for r in out["results"]:
        print(f"{r['id']}. {'PASS' if r['correct'] else 'FAIL'} | {r['instruction']} -> expected {r['expected_tool']}, got {r['proposed_tools']}")
    Path("eval_results.json").write_text(json.dumps(out, indent=2))
    print("Wrote eval_results.json")
