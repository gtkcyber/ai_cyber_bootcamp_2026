import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import pytest  # noqa: E402

from tutor.prompt import (  # noqa: E402
    BUDGET_TOKENS,
    MAX_QUESTION_CHARS,
    DECK_NOTES_MAX_TOKENS,
    HISTORY_RESERVE_TOKENS,
    SKILL_INDEX_MAX_TOKENS,
    SYSTEM,
    build_messages,
    estimate_tokens,
    render_index,
)

INDEX = [
    {"kind": "skill", "name": "ds-evaluate", "description": "Metric-to-cost matching."},
    {"kind": "skill", "name": "course-module-04", "description": "Module 4, Supervised ML."},
    {"kind": "reference", "name": "metric-selection", "description": "Pick a metric."},
]


def _messages(**kw):
    base = dict(question="why?", index_entries=INDEX, deck="04-supervised-machine-learning",
                slide=2, deck_notes="Slide 1: opening\n\nSlide 2: splits leak",
                pinned_note="splits leak", history=[])
    base.update(kw)
    return build_messages(**base)


# --- the stance ----------------------------------------------------------

def test_system_names_the_course():
    assert "AI Cyber Bootcamp 2026" in SYSTEM


def test_system_says_it_explains_rather_than_hands_over_graded_work():
    lowered = SYSTEM.lower()
    assert "explain" in lowered
    assert "hand" in lowered or "give you the finished" in lowered


def test_system_says_the_answers_are_not_secret():
    assert "not secret" in SYSTEM.lower()


def test_system_tells_the_model_the_tools_exist():
    for tool in ("load_skill", "read_reference", "read_lab", "read_deck_notes"):
        assert tool in SYSTEM


# --- the index -----------------------------------------------------------

def test_render_index_is_one_compact_line_per_entry():
    lines = [ln for ln in render_index(INDEX).splitlines() if ln.strip()]
    assert len(lines) == 3
    assert lines[0].startswith("- ds-evaluate")
    assert "Metric-to-cost matching." in lines[0]


def test_render_index_marks_references_apart_from_skills():
    text = render_index(INDEX)
    assert "reference" in text.lower()


def test_render_index_is_capped():
    big = [{"kind": "skill", "name": f"ds-{i:03d}", "description": "x" * 400} for i in range(400)]
    assert estimate_tokens(render_index(big)) <= SKILL_INDEX_MAX_TOKENS + 50


# --- assembly ------------------------------------------------------------

def test_system_is_first_and_the_question_is_last():
    messages = _messages()
    assert messages[0]["role"] == "system"
    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"].rstrip().endswith("why?")


def test_the_index_rides_in_the_system_message():
    assert "ds-evaluate" in _messages()[0]["content"]


def test_the_open_deck_and_slide_are_named():
    content = _messages()[-1]["content"]
    assert "04-supervised-machine-learning" in content
    assert "slide 2" in content.lower()


def test_the_pinned_note_comes_before_the_rest_of_the_notes():
    content = _messages()[-1]["content"]
    assert content.index("splits leak") < content.index("Slide 1: opening")


def test_the_pinned_note_is_labelled_as_the_open_slide():
    assert "currently open" in _messages()[-1]["content"].lower()


def test_no_deck_open_still_builds_a_prompt():
    content = _messages(deck=None, slide=None, deck_notes=None, pinned_note=None)[-1]["content"]
    assert "why?" in content
    assert "slide" not in content.lower()


def test_history_sits_between_system_and_question():
    history = [{"role": "user", "content": "first"},
               {"role": "assistant", "content": "reply"}]
    messages = _messages(history=history)
    assert [m["role"] for m in messages] == ["system", "user", "assistant", "user"]


def test_history_entries_are_stripped_to_role_and_content():
    history = [{"role": "user", "content": "q", "citations": [{"x": 1}], "ts": "t"}]
    assert _messages(history=history)[1] == {"role": "user", "content": "q"}


def test_history_is_dropped_oldest_first_when_it_will_not_fit():
    history = [{"role": "user", "content": "old " * 4000},
               {"role": "assistant", "content": "recent"}]
    kept = [m["content"] for m in _messages(history=history)[1:-1]]
    assert "recent" in kept
    assert not any(c.startswith("old ") for c in kept)


def test_long_deck_notes_are_truncated_with_a_marker():
    notes = "\n\n".join(f"Slide {i}: " + "word " * 200 for i in range(200))
    content = _messages(deck_notes=notes)[-1]["content"]
    assert estimate_tokens(content) <= BUDGET_TOKENS
    assert "truncated" in content.lower()


def test_a_full_prompt_stays_inside_the_budget():
    notes = "\n\n".join(f"Slide {i}: " + "word " * 200 for i in range(200))
    history = [{"role": "user", "content": "q " * 2000} for _ in range(20)]
    messages = _messages(deck_notes=notes, history=history)
    assert sum(estimate_tokens(m["content"]) for m in messages) <= BUDGET_TOKENS


def test_the_budget_leaves_room_for_four_capped_tool_results():
    from tutor.skills import MAX_MATERIAL_CHARS
    fixed = SKILL_INDEX_MAX_TOKENS + DECK_NOTES_MAX_TOKENS + HISTORY_RESERVE_TOKENS
    tools = 4 * (MAX_MATERIAL_CHARS // 4)
    assert fixed + tools <= BUDGET_TOKENS


def test_estimate_tokens_is_never_zero():
    assert estimate_tokens("") >= 1


def test_a_question_longer_than_the_cap_is_trimmed_with_a_marker():
    content = _messages(question="x" * (MAX_QUESTION_CHARS + 5_000))[-1]["content"]
    assert "trimmed" in content.lower()
    assert content.count("x") <= MAX_QUESTION_CHARS


def test_the_user_block_is_refused_when_it_cannot_be_made_to_fit():
    """The budget is a guarantee, not a hope: an impossible one is an error."""
    with pytest.raises(ValueError):
        _messages(budget_tokens=10)


def test_the_assembled_prompt_fits_the_budget_with_an_oversized_question():
    notes = "\n\n".join(f"Slide {i}: " + "word " * 200 for i in range(200))
    messages = _messages(question="x" * 40_000, deck_notes=notes)
    assert sum(estimate_tokens(m["content"]) for m in messages) <= BUDGET_TOKENS


def test_history_gets_its_reserve_before_the_material_is_fitted():
    """The plan's table is 6K index + 6K notes + 2K history + 12K tool results.
    Fitting history from what the material leaves over inverts that: a long deck
    eats the conversation the student is following up on."""
    notes = "\n\n".join(f"Slide {i}: " + "word " * 200 for i in range(200))
    history = [{"role": "user" if i % 2 == 0 else "assistant", "content": "q " * 500}
               for i in range(12)]
    budget = 7_500
    messages = _messages(deck_notes=notes, history=history, budget_tokens=budget)
    reserved = sum(estimate_tokens(m["content"]) for m in messages[1:-1])
    assert reserved > HISTORY_RESERVE_TOKENS * 0.9, f"history squeezed to {reserved}"
    assert sum(estimate_tokens(m["content"]) for m in messages) <= budget
    assert "truncated" in messages[-1]["content"].lower(), "the deck should shrink, not history"


def test_the_material_allowance_is_what_the_budget_leaves_after_the_reserve():
    """Below the deck-notes cap it is the budget that binds, minus the reserve."""
    notes = "\n\n".join(f"Slide {i}: " + "word " * 200 for i in range(200))
    budget = 8_000
    messages = _messages(deck_notes=notes, history=[], budget_tokens=budget)
    room = budget - estimate_tokens(messages[0]["content"]) - HISTORY_RESERVE_TOKENS
    assert room < DECK_NOTES_MAX_TOKENS, "pick a budget where the reserve is what binds"
    # The reserve is held back even with an empty conversation, and the material
    # takes everything else rather than stopping short of it.
    assert room - 200 < estimate_tokens(messages[-1]["content"]) <= room
