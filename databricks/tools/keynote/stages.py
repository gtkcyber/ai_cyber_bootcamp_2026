"""What is on the canvas after each click.

A Keynote slide with builds is one page in the export but several in the
room: the objects that build in are absent until their click. `Slide.chunks`
(model.py) lists the clicks in order, each a tuple of the build events that
fire together. This module turns that into one `Stage` per page the deck
needs: the state before any click, then the state after every click that
changed something visible.

Every event in this course is a build *in* (model.py reads Keynote's
animationType, and nothing here builds out), but the arithmetic handles out
events too so a future deck cannot silently render wrong.

"By Paragraph" and "By Highlighted Bullet" deliveries reveal one text object a
paragraph at a time. Keynote stores them as one build spread over several
chunks, each chunk referencing the same drawable, so the drawable is visible
from its first chunk with one more paragraph per chunk. Highlighted-bullet
delivery also dims the paragraphs already shown; that dimming is not
reproduced, the reveal order is.
"""

from __future__ import annotations

from dataclasses import dataclass, field

ALL_AT_ONCE = "All at Once"


@dataclass(frozen=True)
class Stage:
    """The drawables on the canvas at one point in the click sequence.

    `paragraphs` maps a drawable revealed paragraph by paragraph to how many
    of its paragraphs are showing; a drawable absent from it shows all.
    """
    visible: frozenset[str]
    paragraphs: dict[str, int] = field(default_factory=dict)

    def __hash__(self):
        return hash((self.visible, tuple(sorted(self.paragraphs.items()))))


def stages(drawable_ids, chunks) -> list[Stage]:
    """One Stage per page: initial state, then each click that changed the canvas.

    A drawable that builds in is off the initial canvas; an out event removes
    it again. Clicks that change nothing visible (none in this course, but a
    Keynote action build would be one) add no page. The last stage is the
    finished slide.
    """
    built_in = {event.drawable for chunk in chunks for event in chunk if event.type == "in"}
    visible = set(drawable_ids) - built_in
    paragraphs: dict[str, int] = {}
    result = [Stage(frozenset(visible), dict(paragraphs))]
    for chunk in chunks:
        for event in chunk:
            if event.type == "in":
                visible.add(event.drawable)
                if event.delivery != ALL_AT_ONCE:
                    paragraphs[event.drawable] = paragraphs.get(event.drawable, 0) + 1
            elif event.type == "out":
                visible.discard(event.drawable)
                paragraphs.pop(event.drawable, None)
        stage = Stage(frozenset(visible), dict(paragraphs))
        if stage != result[-1]:
            result.append(stage)
    return result
