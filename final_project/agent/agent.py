"""Agent loop — STUB.

This file is intentionally incomplete. Your task is to implement the agent.
The interface (class name + run() signature) is fixed so main.py and the
grading harness can invoke it. Everything inside the class is yours to design.

Design decisions you must make (and justify in DESIGN.md):

1. Agent pattern. ReAct? Plan-and-Execute? Multi-agent? Pick one and explain
   why it fits Juice Shop.

2. Loop termination. Max steps? Stop when scoreboard shows N solved? Stop when
   the LLM emits a 'done' signal? Consider cost.

3. Context management. Naive approaches grow messages unboundedly and blow the
   context window within ~40 turns. You need a strategy: summarization, scratchpad,
   selective retention, vector memory — your call.

4. Tool-call error handling. What happens when a tool raises? What does the LLM
   see? How many retries?

5. Progress tracking. How does the agent know what it has already tried? How
   does it know which challenges exist and which it has solved?

You may (and should) add helper modules, state classes, and sub-agents. Anything
under agent/ that is not a protected file is yours to restructure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .llm import LLMClient, Message
from .tools import REGISTRY


class PentestAgent:
    def __init__(
        self,
        llm: LLMClient,
        target_url: str,
        max_steps: int = 100,
        log_dir: Path | None = None,
    ) -> None:
        self.llm = llm
        self.target_url = target_url
        self.max_steps = max_steps
        self.log_dir = log_dir
        self.registry = REGISTRY

        # TODO: initialize your state — messages, scratchpad, progress tracking
        raise NotImplementedError(
            "Implement PentestAgent.__init__ — initialize your state here."
        )

    def run(self) -> dict[str, Any]:
        """Run the agent until completion.

        Must return a summary dict with at least:
            {
                "steps_taken": int,
                "tool_calls": int,
                "final_message": str,
            }

        main.py will pass this summary to the report generator (which you will
        also implement — see the generate_report() TODO below).
        """
        # TODO: implement the agent loop.
        #
        # Suggested skeleton (you are NOT required to follow it):
        #
        #   for step in range(self.max_steps):
        #       response = self.llm.complete(
        #           messages=self._compose_messages(),
        #           tools=self.registry.openai_schemas(),
        #       )
        #       if not response.tool_calls:
        #           self._handle_final_message(response)
        #           break
        #       for tc in response.tool_calls:
        #           result = self._invoke_tool(tc)
        #           self._record_tool_result(tc, result)
        raise NotImplementedError("Implement PentestAgent.run")

    def generate_report(self, output_path: Path) -> None:
        """Generate the final pentest report at output_path.

        This is called by main.py after run() completes. The rubric expects the
        report to be grouped by vulnerability class, include evidence captured
        during the run, and include specific remediation advice.

        You have several options:
        - Ask the LLM to write the report from a summary of what happened.
        - Collect findings in a structured list during the run and template
          them into Markdown.
        - Hybrid: structured findings + LLM-generated prose per finding.
        """
        raise NotImplementedError("Implement PentestAgent.generate_report")
