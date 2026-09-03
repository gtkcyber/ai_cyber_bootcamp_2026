"""The tutor's stance, and budgeted assembly of the messages it is sent.

Order in the user message, deliberately: the deck and slide the student has
open, then that slide's own note, then the rest of the deck's notes, then the
question. The pinned note leads because "what does this slide mean" is the
commonest question a student asks with a deck open, and the model should not
have to hunt for the one note that answers it.

The skill index rides in the system message rather than the user message so the
whole system block is byte-identical across a conversation, which is what makes
it cacheable at $0.03/M instead of $0.14/M.
"""
from __future__ import annotations

# Cost ceiling, not a context limit -- the endpoint has 1M. At $0.14/M input a
# full-budget question costs about $0.0045 in and $0.00025 out, the top of the
# spec's $0.001-$0.006 band; a cached prefix puts a repeat near the bottom.
BUDGET_TOKENS = 32_000

# The real index is about 4,300 tokens across 60 entries. The cap is headroom,
# enforced so a future subskill cannot silently push the deck notes out.
SKILL_INDEX_MAX_TOKENS = 6_000

# About 40 slides of notes. A longer deck is cut at a slide boundary.
DECK_NOTES_MAX_TOKENS = 6_000

# Roughly eight short turns, reserved before the material is fitted so a long
# deck can never crowd out the conversation.
HISTORY_RESERVE_TOKENS = 2_000

# A question is the one part of the prompt a student writes, and the whole user
# block is re-sent on every turn of the tool loop -- so a pasted notebook is
# paid for up to five times. routes.py refuses a longer question with a 413;
# this is the same cap enforced where the prompt is actually assembled.
MAX_QUESTION_CHARS = 4_000

SYSTEM_STANCE = """You are the tutor for AI Cyber Bootcamp 2026, a five-day course that goes from pandas and exploratory analysis through classical machine learning to LLM agents, with every lab set on a security problem.

What you do:
- Explain. Take the student's question, name the idea underneath it, and answer from the course's own material and from your skill library.
- Ground the answer. The deck the student has open, its speaker notes and the labs are the course's language; use them, and say which slide or worksheet you are drawing on.
- Say when something is outside the course. Name the nearest thing the course does cover rather than inventing a lesson it does not teach.

What you do not do:
- You do not hand over a finished solution as the first move on a lab exercise. Explain the idea, point at the cell, give the next step. If the student pastes their own attempt, say what is wrong with it.
- The answer notebooks are NOT secret in this course; they ship alongside the worksheets and every student can open them. So if a student asks you outright for the answer, show it and explain why it works. Refusing something they can read for themselves wastes their time.
- You do not invent data, file names, results or numbers that are not in the material you were given or that you loaded.

Your tools, and when to reach for them:
- load_skill(name) — the system message lists every skill and what it covers. Load one when its description matches the question.
- read_reference(name) — a reference document from the same library.
- read_lab(worksheet, answers) — a worksheet notebook as text, or its answer notebook with answers=true.
- read_deck_notes(deck) — the speaker notes of a deck other than the open one; the open deck's notes are already below.
Call at most a few tools, then answer. Do not narrate the tool calls.

How you write:
- Plain sentences. No greeting, no praise for the question, no closing offer.
- Short paragraphs. Lists only for genuinely parallel items. Code only when the question is about code.
- Markdown is fine: bold, lists, fenced code."""


def estimate_tokens(text: str) -> int:
    """Four characters to a token. An estimate; the budget has an order of
    magnitude of headroom against the endpoint's real context, so a tokenizer
    dependency would buy precision nothing here needs."""
    return max(1, len(text or "") // 4)


def render_index(entries) -> str:
    """The skill index as one line per entry, capped."""
    lines, running = [], 0
    for entry in entries:
        kind = "" if entry["kind"] == "skill" else " (reference)"
        line = f"- {entry['name']}{kind}: {entry['description']}"
        cost = estimate_tokens(line)
        if running + cost > SKILL_INDEX_MAX_TOKENS:
            lines.append(f"- [{len(entries) - len(lines)} more entries not listed]")
            break
        lines.append(line)
        running += cost
    return "\n".join(lines)


def build_system(index_text: str) -> str:
    return (
        f"{SYSTEM_STANCE}\n\n"
        "Your skill library. Each line is a name you can pass to load_skill, or to "
        "read_reference where it says reference, and what it covers:\n\n"
        f"{index_text}"
    )


# Exported for tests and for anything that wants the stance without an index.
SYSTEM = build_system("- ds-evaluate: (index rendered per request)")


MATERIAL_TRUNCATED = "[deck notes truncated to fit the prompt budget]"


def _truncate_notes(notes: str, max_tokens: int) -> str:
    """Cut deck notes at a slide boundary, never mid-sentence."""
    if max_tokens <= 0:
        return ""
    if estimate_tokens(notes) <= max_tokens:
        return notes
    kept, running = [], 0
    for block in notes.split("\n\n"):
        cost = estimate_tokens(block)
        if running + cost > max_tokens:
            break
        kept.append(block)
        running += cost
    return "\n\n".join(kept + [MATERIAL_TRUNCATED])


def _truncate_text(text: str, max_tokens: int) -> str:
    """Cut one note, which has no internal boundary to cut on."""
    if max_tokens <= 0:
        return ""
    if estimate_tokens(text) <= max_tokens:
        return text
    return text[:max_tokens * 4].rstrip() + " " + MATERIAL_TRUNCATED


def _truncate_question(question: str) -> str:
    if len(question) <= MAX_QUESTION_CHARS:
        return question
    return (question[:MAX_QUESTION_CHARS].rstrip()
            + "\n\n[question trimmed to the prompt budget]")


def _render_user_block(question: str, deck, slide, deck_notes, pinned_note, *,
                       material_tokens: int) -> str:
    """The user message. `material_tokens` caps the notes, labels included.

    The pinned note is fitted first because it leads, and the rest of the deck
    takes what is left of the allowance -- so a long deck loses its tail rather
    than the one note the student is looking at.
    """
    lines = []
    if deck:
        where = f"The student has deck {deck} open"
        if slide:
            where += f", at slide {slide}"
        lines += [where + ".", ""]
    left = material_tokens
    if pinned_note:
        label = "Speaker note for the slide currently open:"
        left -= estimate_tokens(label)
        pinned = _truncate_text(pinned_note, left)
        if pinned:
            lines += [label, "", pinned, ""]
            left -= estimate_tokens(pinned)
    if deck_notes:
        label = "Speaker notes for the whole open deck:"
        left -= estimate_tokens(label)
        notes = _truncate_notes(deck_notes, min(DECK_NOTES_MAX_TOKENS, left))
        if notes:
            lines += [label, "", notes, ""]
    lines.append(f"Question: {question}")
    return "\n".join(lines)


def _fit_history(history, allowance: int) -> tuple[list[dict], int]:
    """The most recent turns that fit, oldest dropped first."""
    kept, spent = [], 0
    for turn in reversed(history or []):
        entry = {"role": turn["role"], "content": turn["content"]}
        cost = estimate_tokens(entry["content"])
        if spent + cost > allowance:
            break
        kept.append(entry)
        spent += cost
    kept.reverse()
    return kept, spent


def build_messages(question: str, *, index_entries, deck, slide, deck_notes,
                   pinned_note, history, budget_tokens: int = BUDGET_TOKENS) -> list[dict]:
    question = _truncate_question(question)
    system = build_system(render_index(index_entries))

    # The budget is 6K index + 6K deck notes + 2K history + 12K of tool results,
    # and the order matters: history's share is reserved BEFORE the material is
    # fitted, so the material takes the remainder. Fitting history from what the
    # material leaves over inverts that, and a long deck then crowds out the
    # recent turns the student is following up on. The reserve is held back
    # whether or not this conversation has any history to put in it, which keeps
    # the material's allowance the same from the first question to the last.
    kept, spent = _fit_history(history, HISTORY_RESERVE_TOKENS)

    def render(material: int) -> str:
        return _render_user_block(question, deck, slide, deck_notes, pinned_note,
                                  material_tokens=material)

    fixed = estimate_tokens(system) + HISTORY_RESERVE_TOKENS + estimate_tokens(render(0))
    material = max(0, budget_tokens - fixed)
    user = render(material)

    # estimate_tokens floors each part it measures, so a block assembled from
    # several parts can measure a few tokens more than the parts it was fitted
    # from. One corrective pass settles it; the check below is what guarantees it.
    over = estimate_tokens(system) + estimate_tokens(user) + HISTORY_RESERVE_TOKENS - budget_tokens
    if over > 0:
        user = render(max(0, material - over))

    total = estimate_tokens(system) + estimate_tokens(user) + spent
    if total > budget_tokens:
        # Only reachable on a budget too small to hold the stance and the index
        # at all: a caller's mistake, and better raised than silently overspent.
        raise ValueError(
            f"assembled prompt is {total} tokens against a budget of {budget_tokens}")

    return [{"role": "system", "content": system}, *kept, {"role": "user", "content": user}]
