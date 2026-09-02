"""Prose checks: defects an author would hear, not see.

  PROSE-1  a preposition takes a contracted "is" as its object

"The fix for that's not scales", "one route between it's a configuration
drift". Both are real, both shipped, and neither a figure gate nor a style
scorer can see them — a contraction is invisible to stylometry and legal to
a parser. They surface only when somebody reads the line out loud, which is
the test speaker notes are supposed to be held to and the one nothing else
automates.

Narrow on purpose. "it's to produce telemetry" is the same defect and is NOT
checked, because "it's to be expected" is fine and a gate that cries wolf
gets ignored on the day it is right.

Only words that are ALWAYS prepositions belong in the list. Every word that
can also subordinate a clause takes a contraction perfectly well — "after
it's gone", "since that's true", "before it's cut" — and listing one cost
this check a false positive on a correct line the first time it ran. Same
reason "like" and "than" are absent: "like that's going to help" is ordinary
speech. "for" is a preposition here but a conjunction after a comma, so the
lookbehind skips both a sentence boundary and a comma.
"""
# Vendored verbatim from ~/.claude/skills/reveal-deck/scripts/checks/prose.py
# on 2026-09-02. The skill lives outside this repo, so the gate carries its own
# copy. Fix a defect upstream first, then recopy.

from __future__ import annotations

import re

PREPOSITIONS = (
    "of to in on at by with from into onto upon over under through across "
    "against without within between among about for"
).split()
CONTRACTED_OBJECT = re.compile(
    r"(?<![.!?,]\s)\b(" + "|".join(PREPOSITIONS) + r")\s+(it's|that's)\b", re.I
)


def check_note(note: str) -> list[str]:
    """Findings for one slide's note text. Caller prefixes location.

    Cues are stage directions and fenced blocks are notation; neither is
    prose anybody reads aloud to a room.
    """
    note = re.sub(r"<div\b[^>]*\bclass=\"[^\"]*\bcue\b.*?</div>", "", note, flags=re.S)
    note = re.sub(r"```.*?```|`[^`]*`", "", note, flags=re.S)
    return [
        f"{prep!r} takes a contracted verb as its object in "
        f"'{prep} {contraction}'. Read it aloud; it is not a sentence."
        for prep, contraction in CONTRACTED_OBJECT.findall(note)
    ]
