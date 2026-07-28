"""Provider-agnostic LLM client with tool-calling support.

Built on LiteLLM, which normalizes OpenAI / Anthropic / Google / Azure / Ollama /
Groq / Together and ~100 other providers to an OpenAI-compatible interface.

DO NOT MODIFY this file as part of your submission — the grading harness depends
on its signatures. If you need provider-specific behavior, pass extra kwargs
through `complete()`; they forward to litellm.completion verbatim.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import litellm
from dotenv import load_dotenv

load_dotenv()

litellm.drop_params = True


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class Message:
    role: str
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None

    def to_api(self) -> dict[str, Any]:
        msg: dict[str, Any] = {"role": self.role}
        if self.content is not None:
            msg["content"] = self.content
        if self.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments),
                    },
                }
                for tc in self.tool_calls
            ]
        if self.tool_call_id is not None:
            msg["tool_call_id"] = self.tool_call_id
        if self.name is not None:
            msg["name"] = self.name
        return msg


class LLMClient:
    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
    ):
        self.model = model or os.environ.get("LLM_MODEL")
        if not self.model:
            raise RuntimeError(
                "No LLM_MODEL configured. Set it in .env "
                "(e.g. LLM_MODEL=anthropic/claude-sonnet-4-5)."
            )
        t = temperature if temperature is not None else os.environ.get("LLM_TEMPERATURE")
        self.temperature = float(t) if t is not None else 0.2

    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Message:
        """Send one round to the model. Returns the assistant message (which may
        contain tool_calls). Caller is responsible for executing tool calls and
        appending tool-result messages before calling complete() again."""
        payload = [m.to_api() for m in messages]
        response = litellm.completion(
            model=self.model,
            messages=payload,
            tools=tools,
            temperature=self.temperature,
            **kwargs,
        )
        choice = response.choices[0].message
        tool_calls: list[ToolCall] = []
        for tc in getattr(choice, "tool_calls", None) or []:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {"__raw__": tc.function.arguments}
            tool_calls.append(
                ToolCall(id=tc.id, name=tc.function.name, arguments=args)
            )
        return Message(
            role="assistant",
            content=choice.content,
            tool_calls=tool_calls,
        )
