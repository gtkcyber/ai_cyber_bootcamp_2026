#!/usr/bin/env python3
"""Build the AI Cyber Bootcamp reveal decks from the Keynote PDF exports.

    .venv/bin/python databricks/tools/build_decks.py --all
    .venv/bin/python databricks/tools/build_decks.py --deck 08-deep-learning

Each PDF page becomes a 1600x900 WebP. Consecutive pages that are stages of
one Keynote build collapse into a single reveal slide whose earlier stages are
fragments layered under the finished page, so advancing replays what the room
saw. The classification is written once to databricks/pages/<slug>.json and
never rewritten, because a human correction there has to survive a rebuild.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pymupdf
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]

MODULE_RE = re.compile(r"^Module\s+(\d{1,2})\s*[-–—:]?\s*(.+)$")
FINAL_PROJECT_NUMBER = 15


def _slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def slug_for(pdf_name: str) -> str:
    """'Module 3 - Feature Engineering.pdf' -> '03-feature-engineering'.

    The Final Project is not a module and has no number of its own; it sorts
    last, so it takes 15.
    """
    stem = Path(pdf_name).stem.strip()
    if stem.lower() == "final project":
        return f"{FINAL_PROJECT_NUMBER:02d}-final-project"
    match = MODULE_RE.match(stem)
    if not match:
        raise ValueError(f"cannot derive a deck slug from {pdf_name!r}")
    return f"{int(match.group(1)):02d}-{_slugify(match.group(2))}"


def title_for(pdf_name: str) -> str:
    """The part of the deck's <title> after the em dash."""
    stem = Path(pdf_name).stem.strip()
    if stem.lower() == "final project":
        return "Final Project"
    match = MODULE_RE.match(stem)
    if not match:
        raise ValueError(f"cannot derive a deck title from {pdf_name!r}")
    return f"Module {int(match.group(1))}: {' '.join(match.group(2).split())}"


# The reveal canvas and the page images are the same size on purpose: a slide
# that is exactly the canvas cannot trip deck.js's overflow guard.
PAGE_WIDTH = 1600
PAGE_HEIGHT = 900
WEBP_QUALITY = 82


def render_pages(pdf_path, out_dir, width=PAGE_WIDTH, height=PAGE_HEIGHT,
                 quality=WEBP_QUALITY):
    """Render every page of one PDF to <out_dir>/pNNN.webp. Returns the paths.

    PyMuPDF has no WebP writer of its own -- Pixmap.tobytes accepts png, pnm,
    pgm, ppm, pbm, pam, tga, psd and ps and nothing else -- so the pixmap goes
    through Pillow. method=6 is the encoder's slowest and best setting; at
    roughly 0.13 s a page over 1,269 pages that is under three minutes for the
    whole course, and it makes the output reproducible.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    with pymupdf.open(pdf_path) as doc:
        for number, page in enumerate(doc, start=1):
            matrix = pymupdf.Matrix(width / page.rect.width,
                                    height / page.rect.height)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height),
                                    pixmap.samples)
            path = out_dir / f"p{number:03d}.webp"
            image.save(path, "WEBP", quality=quality, method=6)
            written.append(path)
    return written


# ---------------------------------------------------------------- classify
#
# Keynote did not export build stages as position-stable pages. Measuring the
# real files: the earlier page's text sits at the same coordinates on the
# later page in zero pairs across three probed decks, because the author
# re-laid each stage out by hand -- Module 1 pages 10 and 11 are one slide
# with one line added and every element moves 254 points up between them. No
# deck carries a repeating slide-number placeholder either. What survives is
# the words: on a genuine continuation every word of the earlier page
# reappears on the later one, and the later one says more.
#
# Thresholds, each measured rather than picked:
#
#   BUILD_THRESHOLD 0.95  Genuine continuations in Module 1 score 0.95 to
#                         1.00. The one that scores 0.92 (page 132 into 133)
#                         is a stage the author reflowed, and it is the reason
#                         the band below exists rather than the reason to
#                         lower the bar.
#   UNSURE_THRESHOLD 0.70 Below this the pages share only stock vocabulary.
#   MIN_STAGE_TOKENS 3    A full-bleed section divider carries nothing but the
#                         deck footer, which chrome-stripping removes, leaving
#                         zero content words. Three keeps
#                         `series.value_counts()` -- a real one-line stage.
#   MAX_GROWTH 5.0        A page that grows more than fivefold is the title
#                         card pattern: a heading alone, then the heading over
#                         a full slide. Section break or build stage is not
#                         decidable from the PDF, so it goes to a human.
#   CHROME_SHARE 0.8      A word on four fifths of the pages is furniture.
#                         "GTK Cyber" is on every page of fifteen decks.
#   MIN_CHROME_PAGES 4    Below four pages, "four fifths of the pages" is
#                         "nearly all of them", so two pages that really are
#                         stages of one build would have their shared words
#                         stripped as furniture and look unrelated. The
#                         smallest real deck is seven pages, so this floor
#                         never fires on the course and only keeps small
#                         fixtures honest.
BUILD_THRESHOLD = 0.95
UNSURE_THRESHOLD = 0.70
MIN_STAGE_TOKENS = 3
MAX_GROWTH = 5.0
CHROME_SHARE = 0.8
MIN_CHROME_PAGES = 4

WORD_RE = re.compile(r"[a-z0-9]+")


def _page_facts(doc):
    """Words, image identities and raw text, one entry per page.

    Image identity comes from get_image_info(hashes=True), which gives an MD5
    of the pixels and a placement rectangle. It cannot come from get_images()
    xrefs: Keynote re-embeds the same bitmap on every page it appears on, so
    two pages showing one picture carry two different xrefs.
    """
    facts = []
    for page in doc:
        text = page.get_text("text")
        facts.append({
            "tokens": Counter(WORD_RE.findall(text.lower())),
            "images": Counter(
                (info["digest"], round(info["bbox"][0] / 2),
                 round(info["bbox"][1] / 2))
                for info in page.get_image_info(hashes=True)),
            "text": " ".join(text.split()),
        })
    return facts


def _strip_chrome(facts):
    """Drop words that appear on most pages: they are the deck's furniture.

    Fifteen of the sixteen decks stamp 'GTK Cyber' on every page. Counted as
    content it would make every sparse page look like a stage of the next one.
    The four-page floor stops the share test from swallowing everything two
    pages happen to share. Returns the words removed, for the record.
    """
    seen = Counter()
    for fact in facts:
        seen.update(set(fact["tokens"]))
    chrome = {word for word, pages in seen.items()
              if pages >= max(MIN_CHROME_PAGES, CHROME_SHARE * len(facts))}
    for fact in facts:
        for word in chrome:
            del fact["tokens"][word]
    return sorted(chrome)


def _containment(earlier, later):
    """Fraction of the earlier page's words that reappear on the later one."""
    if not earlier:
        return 1.0
    return sum((earlier & later).values()) / sum(earlier.values())


def _kind(earlier, later):
    """Is `earlier` a build stage that continues into `later`?"""
    n_earlier = sum(earlier["tokens"].values())
    n_later = sum(later["tokens"].values())
    if n_later <= n_earlier:
        return "slide"
    overlap = _containment(earlier["tokens"], later["tokens"])
    if overlap >= BUILD_THRESHOLD:
        if n_earlier < MIN_STAGE_TOKENS:
            return "slide"
        if len(later["images"]) < len(earlier["images"]):
            return "slide"
        return "build" if n_later <= MAX_GROWTH * n_earlier else "unsure"
    if overlap >= UNSURE_THRESHOLD:
        return "unsure"
    return "slide"


def group_ids(kinds):
    """One group id per page. A 'build' page joins the page after it.

    'unsure' ends its group: an unreviewed deck is over-split rather than
    over-merged, because a wrongly split build shows two static slides while a
    wrongly merged pair hides a slide behind a fragment click.
    """
    ids, current = [], 1
    for kind in kinds:
        ids.append(current)
        if kind != "build":
            current += 1
    return ids


def classify_pages(pdf_path):
    """One dict per page: {page, kind, group, text}, page numbers 1-based."""
    with pymupdf.open(pdf_path) as doc:
        facts = _page_facts(doc)
    _strip_chrome(facts)
    kinds = ["slide"] * len(facts)
    for index in range(len(facts) - 1):
        kinds[index] = _kind(facts[index], facts[index + 1])
    return [
        {"page": index + 1, "kind": kind, "group": gid, "text": facts[index]["text"]}
        for index, (kind, gid) in enumerate(zip(kinds, group_ids(kinds)))
    ]


def final_pages(pages):
    """The last page of each group: the page the reader ends up looking at."""
    last = {}
    for page in pages:
        last[page["group"]] = page["page"]
    return [last[gid] for gid in sorted(last)]


def pages_path(root, slug):
    return Path(root) / "databricks" / "pages" / f"{slug}.json"


def save_pages(root, slug, pdf_name, pages):
    """Write the classification if it is not already there. (path, written?).

    Never overwrites. The file is the human override surface: someone who
    flips a kind must not lose that edit to the next rebuild.
    """
    path = pages_path(root, slug)
    if path.exists():
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"slug": slug, "pdf": pdf_name, "page_count": len(pages),
               "pages": pages}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path, True


def load_pages(root, slug):
    """Read the classification, recomputing `group` from `kind`.

    A hand edit changes `kind` and leaves `group` stale, so the stored group
    is informational only and the derived one is what the build uses.
    """
    payload = json.loads(pages_path(root, slug).read_text(encoding="utf-8"))
    pages = payload["pages"]
    for page, gid in zip(pages, group_ids([p["kind"] for p in pages])):
        page["group"] = gid
    return payload


# ------------------------------------------------------------------- notes
#
# One markdown file per deck, one '## Page N' section per final slide, N being
# the PDF page number of the slide the reader ends up looking at. UNRESOLVED
# as the whole body is the writer saying the talking points are not inferable
# from the slide -- which goes to Curtis rather than getting invented.
UNRESOLVED = "UNRESOLVED"

NOTE_HEADING_RE = re.compile(r"^##\s+Page\s+(\d+)\s*$", re.M)
CODE_SPAN_RE = re.compile(r"`([^`]+)`")


def notes_path(root, slug):
    return Path(root) / "databricks" / "notes" / f"{slug}.md"


def load_notes(root, slug):
    """{final page number: note body}. A missing file is an empty mapping."""
    path = notes_path(root, slug)
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    headings = list(NOTE_HEADING_RE.finditer(text))
    notes = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        page = int(heading.group(1))
        if page in notes:
            raise ValueError(f"{path}: page {page} has two '## Page' headings")
        notes[page] = text[heading.end():end].strip()
    return notes


def _inline(text):
    return CODE_SPAN_RE.sub(lambda m: f"<code>{m.group(1)}</code>",
                            html.escape(text, quote=False))


def note_html(body):
    """Paragraphs, dash lists and inline code. Deliberately not a markdown
    engine: the notes register bans everything richer, and a dependency for
    two constructs is not worth carrying."""
    body = body.strip()
    if not body:
        return ""
    blocks = []
    for block in re.split(r"\n\s*\n", body):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if all(line.startswith("- ") for line in lines):
            items = "".join(f"<li>{_inline(line[2:])}</li>" for line in lines)
            blocks.append(f"<ul>{items}</ul>")
        else:
            blocks.append(f"<p>{_inline(' '.join(lines))}</p>")
    return "\n".join(blocks)
