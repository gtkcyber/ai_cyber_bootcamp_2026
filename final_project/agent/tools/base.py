"""Tool protocol, registry, and @tool decorator.

Students: you register tools with @tool and the JSON schema is derived from your
Pydantic model or type hints. You do NOT need to modify this file — add new
tools as new modules in agent/tools/ and import them in agent/tools/__init__.py.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, get_type_hints

from pydantic import BaseModel


@dataclass
class Tool:
    name: str
    description: str
    parameters_schema: dict[str, Any]
    func: Callable[..., Any]

    def openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }

    def invoke(self, arguments: dict[str, Any]) -> Any:
        sig = inspect.signature(self.func)
        accepted = {k: v for k, v in arguments.items() if k in sig.parameters}
        return self.func(**accepted)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def all(self) -> list[Tool]:
        return list(self._tools.values())

    def openai_schemas(self) -> list[dict[str, Any]]:
        return [t.openai_schema() for t in self._tools.values()]


REGISTRY = ToolRegistry()


def tool(
    name: str | None = None,
    description: str | None = None,
    params: type[BaseModel] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a function as a tool.

    Usage with a Pydantic params model (preferred — clearer schemas):

        class MyParams(BaseModel):
            path: str = Field(..., description="URL path")
            verb: str = "GET"

        @tool(description="Fetches a page.", params=MyParams)
        def fetch(path: str, verb: str = "GET") -> str:
            ...

    Usage with bare type hints (ok for simple tools):

        @tool(description="Echo a string.")
        def echo(s: str) -> str:
            return s
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        tool_name = name or func.__name__
        doc = description or (func.__doc__ or "").strip() or tool_name
        if params is not None:
            schema = params.model_json_schema()
            schema.pop("title", None)
        else:
            schema = _schema_from_hints(func)
        REGISTRY.register(
            Tool(
                name=tool_name,
                description=doc,
                parameters_schema=schema,
                func=func,
            )
        )
        return func

    return decorator


_SIMPLE_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean"}


def _schema_from_hints(func: Callable[..., Any]) -> dict[str, Any]:
    hints = get_type_hints(func)
    hints.pop("return", None)
    sig = inspect.signature(func)
    properties: dict[str, Any] = {}
    required: list[str] = []
    for pname, param in sig.parameters.items():
        hint = hints.get(pname, str)
        properties[pname] = {"type": _SIMPLE_TYPES.get(hint, "string")}
        if param.default is inspect.Parameter.empty:
            required.append(pname)
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }
