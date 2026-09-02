"""The model call: a hand-built OpenAI client and a capped tool loop.

CLIENT. `Tutor.from_workspace` builds a plain `openai.OpenAI` by hand -- it does
NOT use the SDK's serving-endpoints OpenAI-client helper. That method is
deprecated in `databricks-sdk` 0.133 and hard-imports the real `httpx` package
to build its Bearer-auth transport; `openai` 3.x depends on `httpx`'s successor
package `httpx2` and does not install `httpx` at all, so the bare call raises
`ModuleNotFoundError: No module named 'httpx'` -- exactly what a fresh pip
install of this app's requirements hits in production, not a quirk of one venv.
The fix is to drop the helper: `OpenAI(base_url=f"{w.config.host}/serving-endpoints",
api_key=token)` where `token` is a zero-arg callable reading
`w.config.authenticate()`'s Authorization header. `openai.OpenAI` accepts
`api_key` as `str | Callable[[], str] | None`, so every request pulls a fresh
token through the workspace client's own refresh -- what the helper did
internally -- with no `httpx` at all. Authenticated as whichever principal `w`
is: the app's own service principal at runtime, a CLI profile locally.

REASONING EFFORT. `reasoning_effort` is a TOP-LEVEL request field, not nested,
and it is sent on every call. Per
https://docs.databricks.com/aws/en/machine-learning/model-serving/query-reason-models
this endpoint is hybrid-reasoning and defaults to `max` when reasoning_effort is
omitted; DeepSeek V4 Flash (0731) accepts `low`, `high` and `max`, and anything
else falls back to `max`. Omitting it would silently buy the most expensive
setting, so spec decision 5's `low` is always explicit. It goes through
`extra_body` because the openai client's typed signature does not carry it on
every version; extra_body lands it at the top level of the JSON body.

NO STREAMING. A tool loop makes up to five model calls and only the last writes
prose, so streaming the intermediate turns shows a student nothing. The loop runs
non-streaming and the route emits the finished text as one SSE frame, which the
front end's accumulate-then-render path already handles. It also hands back
`response.usage`, which the deployment notes' cost line needs.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from openai import OpenAI

from tutor.files import MissingFile

logger = logging.getLogger(__name__)

MAX_TOOL_CALLS = 4
MAX_OUTPUT_TOKENS = 900
REASONING_EFFORT = "low"
TEMPERATURE = 0.2
EMPTY_ANSWER = "I could not put an answer together for that. Ask again, or narrow the question."

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": (
                "Read the full text of one skill from the tutor's library. The system prompt "
                "lists every skill's name and description; call this when a skill's description "
                "says it covers the question and you need its actual guidance."),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string",
                             "description": "Exact skill name from the index, e.g. ds-evaluate or course-module-04."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_reference",
            "description": "Read one reference document from the tutor's library, e.g. metric-selection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string",
                             "description": "Exact reference name from the index."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_lab",
            "description": (
                "Read a course worksheet notebook as text: its markdown and code cells in order. "
                "Set answers=true to read the matching answer notebook instead -- answers are not "
                "secret in this course."),
            "parameters": {
                "type": "object",
                "properties": {
                    "worksheet": {"type": "string",
                                  "description": "Worksheet number such as 4.2, or a full filename."},
                    "answers": {"type": "boolean",
                                "description": "Read the answer notebook rather than the worksheet."},
                },
                "required": ["worksheet"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_deck_notes",
            "description": (
                "Read the speaker notes of a deck, slide by slide. The notes for the deck the "
                "student currently has open are already in the prompt; call this for a different deck."),
            "parameters": {
                "type": "object",
                "properties": {
                    "deck": {"type": "string",
                             "description": "Deck folder id, e.g. 04-supervised-machine-learning."},
                },
                "required": ["deck"],
            },
        },
    },
]


class Toolbox:
    """Dispatch from a tool name to the library or the course material.

    A tool never raises into the loop: a bad name or a missing file comes back as
    a sentence the model can read and recover from, because a raised exception
    would lose the whole answer over a typo the model could have fixed itself.
    """

    def __init__(self, library, material):
        self.library = library
        self.material = material
        self.sources: list[dict] = []

    def schemas(self) -> list[dict]:
        return TOOL_SCHEMAS

    def call(self, name: str, arguments: dict) -> str:
        try:
            if name == "load_skill":
                key = arguments["name"]
                out = self.library.load_skill(key)
                self._record("skill", key)
            elif name == "read_reference":
                key = arguments["name"]
                out = self.library.read_reference(key)
                self._record("reference", key)
            elif name == "read_lab":
                key = arguments["worksheet"]
                out = self.material.read_lab(key, answers=bool(arguments.get("answers")))
                self._record("answer" if arguments.get("answers") else "lab", key)
            elif name == "read_deck_notes":
                key = arguments["deck"]
                out = self.material.render_deck_notes(key)
                self._record("deck", key)
            else:
                return f"Unknown tool {name!r}. Use one of: " + ", ".join(
                    t["function"]["name"] for t in TOOL_SCHEMAS)
        except KeyError as e:
            return f"Missing required argument {e.args[0]!r} for {name}."
        except MissingFile as e:
            return str(e)
        except Exception:
            logger.exception("tool %s failed with %r", name, arguments)
            return f"{name} failed. Answer from what you already have."
        return out

    def _record(self, kind: str, name: str) -> None:
        entry = {"kind": kind, "name": name}
        if entry not in self.sources:
            self.sources.append(entry)


@dataclass(frozen=True)
class Answer:
    text: str
    sources: list[dict] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    tool_calls: list[str] = field(default_factory=list)


class Tutor:
    def __init__(self, client, model: str, toolbox: Toolbox, *,
                 max_tool_calls: int = MAX_TOOL_CALLS,
                 max_output_tokens: int = MAX_OUTPUT_TOKENS,
                 reasoning_effort: str = REASONING_EFFORT):
        self.client = client
        self.model = model
        self.toolbox = toolbox
        self.max_tool_calls = max_tool_calls
        self.max_output_tokens = max_output_tokens
        self.reasoning_effort = reasoning_effort

    @classmethod
    def from_workspace(cls, w, endpoint: str, toolbox: Toolbox, **kw) -> "Tutor":
        def token() -> str:
            return w.config.authenticate()["Authorization"].split(" ", 1)[1]

        client = OpenAI(base_url=f"{w.config.host}/serving-endpoints", api_key=token)
        return cls(client, endpoint, toolbox, **kw)

    def _complete(self, messages: list[dict], *, with_tools: bool):
        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_output_tokens,
            "temperature": TEMPERATURE,
            "extra_body": {"reasoning_effort": self.reasoning_effort},
        }
        if with_tools:
            kwargs["tools"] = self.toolbox.schemas()
            kwargs["tool_choice"] = "auto"
        return self.client.chat.completions.create(**kwargs)

    def answer(self, messages: list[dict]) -> Answer:
        convo = list(messages)
        used: list[str] = []
        prompt_tokens = completion_tokens = turns = 0

        while True:
            budget_left = self.max_tool_calls - len(used)
            with_tools = budget_left > 0
            response = self._complete(convo, with_tools=with_tools)
            turns += 1
            usage = getattr(response, "usage", None)
            if usage is not None:
                prompt_tokens += getattr(usage, "prompt_tokens", 0) or 0
                completion_tokens += getattr(usage, "completion_tokens", 0) or 0

            message = response.choices[0].message
            # Once the budget is spent the turn is made without tools, so that
            # turn is the last one: anything tool-shaped in a reply to a request
            # that offered no tools is not actionable, and honouring it would let
            # a model that keeps asking spin the loop forever.
            calls = list(getattr(message, "tool_calls", None) or []) if with_tools else []
            if not calls:
                text = (message.content or "").strip() or EMPTY_ANSWER
                return Answer(
                    text=text, sources=list(self.toolbox.sources),
                    usage={"prompt_tokens": prompt_tokens,
                           "completion_tokens": completion_tokens, "turns": turns},
                    tool_calls=used,
                )

            # The assistant turn must be echoed back with its tool_calls before
            # the tool results, or the endpoint rejects the orphaned tool role.
            convo.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [{"id": c.id, "type": "function",
                                "function": {"name": c.function.name,
                                             "arguments": c.function.arguments}} for c in calls],
            })

            for call in calls[:budget_left]:
                name = call.function.name
                try:
                    arguments = json.loads(call.function.arguments or "{}")
                except ValueError:
                    arguments = {}
                result = self.toolbox.call(name, arguments)
                label = next(iter(arguments.values()), "") if arguments else ""
                used.append(f"{name}:{label}" if label else name)
                convo.append({"role": "tool", "tool_call_id": call.id,
                              "name": name, "content": result})

            for call in calls[budget_left:]:
                convo.append({"role": "tool", "tool_call_id": call.id, "name": call.function.name,
                              "content": "Tool budget spent. Answer from what you have."})
