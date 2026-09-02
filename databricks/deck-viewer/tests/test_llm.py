import json
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from tutor.files import LocalFiles  # noqa: E402
from tutor.llm import TOOL_SCHEMAS, Answer, Toolbox, Tutor  # noqa: E402
from tutor.skills import CourseMaterial, SkillLibrary  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def toolbox():
    return Toolbox(
        library=SkillLibrary.load(LocalFiles(FIXTURES), "/skills"),
        material=CourseMaterial(
            files=LocalFiles(FIXTURES), labs_path="/labs", answers_path="/answers",
            decks_path="/decks", deck_files=LocalFiles(FIXTURES)),
    )


def _tool_call(id_, name, args):
    return SimpleNamespace(id=id_, type="function",
                           function=SimpleNamespace(name=name, arguments=json.dumps(args)))


def _reply(content=None, tool_calls=None, prompt=100, completion=20):
    message = SimpleNamespace(role="assistant", content=content, tool_calls=tool_calls or None)
    return SimpleNamespace(
        choices=[SimpleNamespace(message=message, finish_reason="stop" if content else "tool_calls")],
        usage=SimpleNamespace(prompt_tokens=prompt, completion_tokens=completion,
                              total_tokens=prompt + completion))


class FakeCompletions:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.replies.pop(0)


class FakeClient:
    def __init__(self, replies):
        self.chat = SimpleNamespace(completions=FakeCompletions(replies))


def _tutor(toolbox, replies, **kw):
    client = FakeClient(replies)
    return Tutor(client, "databricks-deepseek-v4-flash-0731", toolbox, **kw), client


# --- schemas -------------------------------------------------------------

def test_four_tools_are_declared():
    assert {t["function"]["name"] for t in TOOL_SCHEMAS} == {
        "load_skill", "read_reference", "read_lab", "read_deck_notes"}


def test_every_schema_is_a_well_formed_function_definition():
    for t in TOOL_SCHEMAS:
        assert t["type"] == "function"
        fn = t["function"]
        assert fn["description"] and fn["parameters"]["type"] == "object"
        assert fn["parameters"]["required"]
        for prop in fn["parameters"]["properties"].values():
            assert prop["type"] and prop["description"]


def test_read_lab_schema_exposes_the_answers_flag():
    fn = next(t["function"] for t in TOOL_SCHEMAS if t["function"]["name"] == "read_lab")
    assert "answers" in fn["parameters"]["properties"]
    assert fn["parameters"]["properties"]["answers"]["type"] == "boolean"


# --- the toolbox ---------------------------------------------------------

def test_toolbox_dispatches_load_skill(toolbox):
    assert "PR-AUC" in toolbox.call("load_skill", {"name": "ds-evaluate"}, [])


def test_toolbox_dispatches_read_lab(toolbox):
    assert "GridSearchCV" in toolbox.call("read_lab", {"worksheet": "4.2"}, [])


def test_toolbox_dispatches_read_deck_notes(toolbox):
    assert "Slide 1" in toolbox.call("read_deck_notes", {"deck": "04-supervised-machine-learning"}, [])


def test_toolbox_turns_a_missing_file_into_a_message_not_an_exception(toolbox):
    out = toolbox.call("load_skill", {"name": "ds-nope"}, [])
    assert "no skill" in out.lower()


def test_toolbox_rejects_an_unknown_tool(toolbox):
    assert "unknown tool" in toolbox.call("rm_rf", {}, []).lower()


def test_toolbox_handles_a_missing_argument(toolbox):
    assert "missing" in toolbox.call("load_skill", {}, []).lower()


def test_toolbox_records_what_it_served_in_the_callers_list(toolbox):
    sources = []
    toolbox.call("load_skill", {"name": "ds-evaluate"}, sources)
    toolbox.call("read_lab", {"worksheet": "4.2"}, sources)
    assert [s["name"] for s in sources] == ["ds-evaluate", "4.2"]
    assert [s["kind"] for s in sources] == ["skill", "lab"]


def test_the_toolbox_keeps_no_source_state_of_its_own(toolbox):
    toolbox.call("load_skill", {"name": "ds-evaluate"}, [])
    assert not hasattr(toolbox, "sources")


# --- the loop ------------------------------------------------------------

def test_a_direct_answer_makes_one_call(toolbox):
    tutor, client = _tutor(toolbox, [_reply(content="Because the classes are imbalanced.")])
    answer = tutor.answer([{"role": "user", "content": "why?"}])
    assert isinstance(answer, Answer)
    assert answer.text == "Because the classes are imbalanced."
    assert answer.tool_calls == []
    assert len(client.chat.completions.calls) == 1


def test_a_tool_call_is_executed_and_fed_back(toolbox):
    tutor, client = _tutor(toolbox, [
        _reply(tool_calls=[_tool_call("c1", "load_skill", {"name": "ds-evaluate"})]),
        _reply(content="Use PR-AUC."),
    ])
    answer = tutor.answer([{"role": "user", "content": "which metric?"}])
    assert answer.text == "Use PR-AUC."
    assert answer.tool_calls == ["load_skill:ds-evaluate"]
    second = client.chat.completions.calls[1]["messages"]
    assert second[-1]["role"] == "tool" and second[-1]["tool_call_id"] == "c1"
    assert "PR-AUC" in second[-1]["content"]


def test_two_tool_calls_in_one_turn_both_run(toolbox):
    tutor, client = _tutor(toolbox, [
        _reply(tool_calls=[_tool_call("a", "load_skill", {"name": "ds-evaluate"}),
                           _tool_call("b", "read_lab", {"worksheet": "4.2"})]),
        _reply(content="done"),
    ])
    answer = tutor.answer([{"role": "user", "content": "q"}])
    assert len(answer.tool_calls) == 2
    tool_msgs = [m for m in client.chat.completions.calls[1]["messages"] if m["role"] == "tool"]
    assert {m["tool_call_id"] for m in tool_msgs} == {"a", "b"}


def test_the_loop_stops_at_four_tool_calls(toolbox):
    call = [_tool_call("x", "load_skill", {"name": "ds-evaluate"})]
    tutor, client = _tutor(toolbox, [_reply(tool_calls=call) for _ in range(4)]
                           + [_reply(content="final")])
    answer = tutor.answer([{"role": "user", "content": "q"}])
    assert len(answer.tool_calls) == 4
    assert answer.text == "final"
    # one turn per tool round, plus the forced final turn
    assert len(client.chat.completions.calls) == 5
    assert client.chat.completions.calls[-1].get("tools") is None


def test_a_model_that_keeps_calling_tools_after_they_are_withdrawn_still_stops(toolbox):
    """The budget withdraws the tools; the loop must not wait to be obeyed."""
    call = [_tool_call("x", "load_skill", {"name": "ds-evaluate"})]
    tutor, client = _tutor(toolbox, [_reply(tool_calls=call) for _ in range(20)])
    answer = tutor.answer([{"role": "user", "content": "q"}])
    assert len(answer.tool_calls) == 4
    assert len(client.chat.completions.calls) == 5
    assert answer.text.strip() != ""


def test_reasoning_effort_low_rides_in_extra_body(toolbox):
    tutor, client = _tutor(toolbox, [_reply(content="ok")])
    tutor.answer([{"role": "user", "content": "q"}])
    assert client.chat.completions.calls[0]["extra_body"] == {"reasoning_effort": "low"}


def test_the_model_name_comes_from_the_endpoint_variable(toolbox):
    tutor, client = _tutor(toolbox, [_reply(content="ok")])
    tutor.answer([{"role": "user", "content": "q"}])
    assert client.chat.completions.calls[0]["model"] == "databricks-deepseek-v4-flash-0731"


def test_usage_is_summed_across_every_turn(toolbox):
    tutor, _ = _tutor(toolbox, [
        _reply(tool_calls=[_tool_call("c", "load_skill", {"name": "ds-evaluate"})],
               prompt=1000, completion=10),
        _reply(content="x", prompt=4000, completion=200),
    ])
    answer = tutor.answer([{"role": "user", "content": "q"}])
    assert answer.usage == {"prompt_tokens": 5000, "completion_tokens": 210, "turns": 2}


def test_sources_reach_the_answer(toolbox):
    tutor, _ = _tutor(toolbox, [
        _reply(tool_calls=[_tool_call("c", "read_deck_notes",
                                      {"deck": "04-supervised-machine-learning"})]),
        _reply(content="x"),
    ])
    answer = tutor.answer([{"role": "user", "content": "q"}])
    assert answer.sources == [{"kind": "deck", "name": "04-supervised-machine-learning"}]


def test_an_empty_final_message_does_not_crash(toolbox):
    tutor, _ = _tutor(toolbox, [_reply(content=None)])
    assert tutor.answer([{"role": "user", "content": "q"}]).text.strip() != ""


def test_from_workspace_builds_the_client_without_the_sdk_helper(monkeypatch, toolbox):
    """The SDK's get_open_ai_client hard-imports httpx, which openai 3.x does not install."""
    captured = {}

    class FakeOpenAI:
        def __init__(self, base_url, api_key):
            captured["base_url"] = base_url
            captured["api_key"] = api_key

    monkeypatch.setattr("tutor.llm.OpenAI", FakeOpenAI)
    w = SimpleNamespace(
        config=SimpleNamespace(host="https://example.cloud.databricks.com",
                               authenticate=lambda: {"Authorization": "Bearer tok-123"}),
        serving_endpoints=SimpleNamespace(
            get_open_ai_client=lambda: pytest.fail("must not use the SDK helper")))
    Tutor.from_workspace(w, "databricks-deepseek-v4-flash-0731", toolbox)
    assert captured["base_url"] == "https://example.cloud.databricks.com/serving-endpoints"
    assert callable(captured["api_key"]), "api_key must be a callable so tokens refresh"
    assert captured["api_key"]() == "tok-123"


def test_source_file_never_calls_the_sdk_helper():
    src = (APP_DIR / "tutor" / "llm.py").read_text(encoding="utf-8")
    assert "get_open_ai_client(" not in src.replace("get_open_ai_client`", "")


# --- one collector per answer --------------------------------------------

class InterleavedClient:
    """One client, two conversations, forced to overlap inside the tool loop.

    Each conversation's first turn asks for its own skill; the barrier holds
    both threads at the turn after the tool ran, which is the window in which a
    collector shared by the process mixes the two answers' sources together.
    """

    def __init__(self, barrier):
        self.barrier = barrier
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        messages = kwargs["messages"]
        marker = messages[0]["content"]
        if not any(m["role"] == "tool" for m in messages):
            skill = "ds-evaluate" if marker == "A" else "course-module-04"
            return _reply(tool_calls=[_tool_call(marker, "load_skill", {"name": skill})])
        self.barrier.wait(timeout=5)
        return _reply(content=f"answer {marker}")


def test_two_interleaved_answers_report_disjoint_sources(toolbox):
    """Two students asking at once must not be handed each other's citations."""
    tutor = Tutor(InterleavedClient(threading.Barrier(2)),
                  "databricks-deepseek-v4-flash-0731", toolbox)
    answers = {}

    def ask(marker):
        answers[marker] = tutor.answer([{"role": "user", "content": marker}])

    threads = [threading.Thread(target=ask, args=(m,)) for m in ("A", "B")]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)

    assert answers["A"].sources == [{"kind": "skill", "name": "ds-evaluate"}]
    assert answers["B"].sources == [{"kind": "skill", "name": "course-module-04"}]
