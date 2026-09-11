#!/usr/bin/env python3
"""Build the AI Cyber Bootcamp reveal decks from the Keynote PDF exports.

    .venv/bin/python databricks/tools/build_decks.py --all
    .venv/bin/python databricks/tools/build_decks.py --deck 08-deep-learning

Each PDF page becomes a 1600x900 WebP. Consecutive pages that are stages of
one Keynote build collapse into a single reveal slide whose earlier stages are
fragments layered under the finished page, so advancing replays what the room
saw. A deck built from its Keynote file says which pages are stages in
databricks/keynote/<slug>.json, and that manifest also places the movies and
YouTube embeds on their slides. Without one the stages are inferred from the
page text, and that classification is written once to
databricks/pages/<slug>.json and never rewritten, because a human correction
there has to survive a rebuild.
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


def save_pages(root, slug, pdf_name, pages, manifest=False):
    """Write the classification. (path, written?).

    An inferred classification is never overwritten: the file is the human
    override surface, and someone who flips a kind must not lose that edit to
    the next rebuild. A classification dictated by a Keynote manifest is
    derived, so it is rewritten every build and marked as such.
    """
    path = pages_path(root, slug)
    if path.exists() and not manifest:
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"slug": slug, "pdf": pdf_name, "page_count": len(pages),
               "manifest": manifest, "pages": pages}
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


# ---------------------------------------------------------------- manifest
#
# A deck built from its Keynote file carries databricks/keynote/<slug>.json,
# written by the Keynote build step: every PDF page mapped to the Keynote slide
# and build stage it renders, plus the movies and YouTube embeds the slides
# carry. Where it exists it is the truth and the word-overlap classifier above
# is not consulted -- Keynote knows which pages are stages of one slide, the
# text heuristic only guesses. Media boxes are fractions of the Keynote canvas,
# so they place the same way on the pixel-pinned deck and the fluid reading
# copy.
MEDIA_KINDS = ("movie", "youtube")
YOUTUBE_EMBED = "https://www.youtube-nocookie.com/embed/{id}"


def manifest_path(root, slug):
    return Path(root) / "databricks" / "keynote" / f"{slug}.json"


def load_manifest(root, slug):
    """The validated Keynote manifest for a slug, or None without one."""
    path = manifest_path(root, slug)
    if not path.exists():
        return None
    manifest = json.loads(path.read_text(encoding="utf-8"))
    _validate_manifest(manifest, path)
    return manifest


def _validate_manifest(manifest, path):
    """A manifest that is not exactly one page per PDF page, in order, with
    complete stage runs, would build a deck that lies about its slides."""
    entries = manifest["pages"]
    if [e["page"] for e in entries] != list(range(1, manifest["page_count"] + 1)):
        raise ValueError(f"{path}: pages must run 1..{manifest['page_count']} in order")
    runs = {}
    for entry in entries:
        runs.setdefault(entry["slide"], []).append((entry["stage"], entry["stages"]))
    if list(runs) != sorted(runs):
        raise ValueError(f"{path}: slides are out of order")
    for slide, run in runs.items():
        count = run[0][1]
        if [s for s, _ in run] != list(range(count)) or any(c != count for _, c in run):
            raise ValueError(f"{path}: slide {slide} stages are not 0..{count - 1}")
    for item in manifest.get("media", []):
        if item["kind"] not in MEDIA_KINDS:
            raise ValueError(f"{path}: unknown media kind {item['kind']!r}")
        if item["slide"] not in runs:
            raise ValueError(f"{path}: media on slide {item['slide']}, which has no page")
        box = item["box"]
        if len(box) != 4 or not all(0 <= value <= 1 for value in box):
            raise ValueError(f"{path}: media box {box} is not four canvas fractions")
        if not item.get("src" if item["kind"] == "movie" else "id"):
            raise ValueError(f"{path}: {item['kind']} on slide {item['slide']} has no source")


def manifest_kinds(manifest):
    """A stage before the finished page is 'build'; the finished page is 'slide'."""
    return ["build" if e["stage"] < e["stages"] - 1 else "slide"
            for e in manifest["pages"]]


def manifest_pages(manifest, pdf_path):
    """The classification the manifest dictates, in the classifier's shape plus
    the Keynote slide number. Text still comes from the PDF: it is the alt text
    and the unresolved report."""
    with pymupdf.open(pdf_path) as doc:
        if doc.page_count != manifest["page_count"]:
            raise ValueError(f"{pdf_path.name} has {doc.page_count} pages, "
                             f"the manifest says {manifest['page_count']}")
        texts = [" ".join(page.get_text("text").split()) for page in doc]
    kinds = manifest_kinds(manifest)
    return [{"page": entry["page"], "kind": kind, "group": gid,
             "slide": entry["slide"], "text": text}
            for entry, kind, gid, text
            in zip(manifest["pages"], kinds, group_ids(kinds), texts)]


def manifest_media(manifest):
    """{Keynote slide number: [media items]} in manifest order."""
    by_slide = {}
    for item in manifest.get("media", []):
        by_slide.setdefault(item["slide"], []).append(item)
    return by_slide


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


# -------------------------------------------------------------------- emit
#
# The skeleton is the reference course's deck head and tail with the markdown
# textarea replaced by literal sections, because these slides are images and
# there is no markdown to parse. Reveal, its theme and its plugins stay pinned
# to 5.2.1 on the CDN, and the markdown plugin stays loaded because deck.js's
# default plugin list names it.
COURSE_NAME = "AI Cyber Bootcamp 2026"

SKELETON = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, \
maximum-scale=1.0, user-scalable=no">
  <title>{title}</title>

  <!-- reveal.js, basic setup: CDN, pinned, no build step, runs from file:// -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/theme/white.css" id="theme">
  <!-- Shared across every deck in the course. Sixteen decks, one look. -->
  <link rel="stylesheet" href="../assets/reveal-a11y/helper.css">
  <link rel="stylesheet" href="../assets/course.css">
</head>
<body>
<div class="reveal">
<div class="slides">
{sections}
</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reveal.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/plugin/markdown/markdown.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/plugin/highlight/highlight.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/plugin/notes/notes.js"></script>
<script src="../assets/deck.js"></script>
<script>
  CourseDeck.start();
</script>
</body>
</html>
"""

ALT_LIMIT = 180


def _alt_text(page):
    """The words on the page, for a reader who cannot see it.

    The note is the real explanation, but a screen reader in slide mode never
    reaches the note, so the slide's own text is the best alt available.
    """
    text = " ".join(page.get("text", "").split())[:ALT_LIMIT]
    return html.escape(text or f"Slide {page['page']}", quote=True)


def _style(box):
    """Inline position for a media box, as percentages of the page stack."""
    left, top, width, height = (f"{value * 100:.2f}%" for value in box)
    return f"left:{left};top:{top};width:{width};height:{height}"


def _media_html(item, fragment_index):
    """A movie or YouTube embed over the finished page. Sources ride in
    data-src so reveal loads them only when the slide is near; preload and
    lazy loading keep the reading copy just as cheap until somebody plays."""
    css_class = "media" if fragment_index is None else "media fragment"
    order = "" if fragment_index is None else f' data-fragment-index="{fragment_index}"'
    style = _style(item["box"])
    if item["kind"] == "movie":
        poster = (f' poster="{html.escape(item["poster"], quote=True)}"'
                  if item.get("poster") else "")
        return (f'      <video class="{css_class}" '
                f'data-src="{html.escape(item["src"], quote=True)}"{poster}{order} '
                f'controls preload="none" playsinline style="{style}"></video>')
    return (f'      <iframe class="{css_class}" '
            f'data-src="{YOUTUBE_EMBED.format(id=html.escape(item["id"], quote=True))}"'
            f'{order} title="YouTube video" loading="lazy" allow="fullscreen" '
            f'allowfullscreen style="{style}"></iframe>')


def _section(stages, note, media=()):
    """One reveal slide: the group's pages stacked, its media, then the note.

    The group's first page is the base layer and each later stage is a
    fragment above it, so one keypress per stage replays the build and the
    finished page ends up on top. Reading mode strips the fragment class but
    not the stacking order, so it shows the finished page. data-page carries
    the PDF page number of the finished page, which is what the deployed
    app's tutor reads to know which page is on screen.

    Media belong to the finished page. On a slide with build stages they are
    fragments too, sharing the last stage's index so they arrive with it:
    reveal orders explicitly indexed fragments before unindexed ones, so once
    one element carries an index every element in the section must.
    """
    explicit = bool(media) and len(stages) > 1
    layers = []
    for index, page in enumerate(stages):
        css_class = "page" if index == 0 else "page fragment"
        order = f' data-fragment-index="{index - 1}"' if explicit and index else ""
        layers.append(f'      <img class="{css_class}" '
                      f'src="pages/p{page["page"]:03d}.webp"{order} '
                      f'alt="{_alt_text(page)}">')
    last = len(stages) - 2 if explicit else None
    layers.extend(_media_html(item, last) for item in media)
    body = "\n".join(layers)
    rendered = (f'<p class="unresolved">{UNRESOLVED}</p>'
                if note.strip() == UNRESOLVED else note_html(note))
    aside = (f'    <aside class="notes">\n      {rendered}\n    </aside>\n'
             if rendered else "")
    final_page = stages[-1]["page"]
    return (f'  <section data-page="{final_page}">\n'
            f'    <div class="page-stack">\n{body}\n    </div>\n'
            f"{aside}"
            f"  </section>")


def emit_deck(root, slug, title, pages, notes, media=None):
    """Write decks/<slug>/index.html. Returns the path.

    `media` is manifest_media()'s mapping; pages from a manifest carry their
    Keynote slide number, which is what it is keyed by.
    """
    media = media or {}
    by_group = {}
    for page in pages:
        by_group.setdefault(page["group"], []).append(page)

    sections = []
    for gid in sorted(by_group):
        stages = sorted(by_group[gid], key=lambda p: p["page"])
        items = media.get(stages[-1].get("slide"), ())
        sections.append(_section(stages, notes.get(stages[-1]["page"], ""), items))

    path = Path(root) / "decks" / slug / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        SKELETON.format(title=f"{COURSE_NAME} &mdash; {title}",
                        sections="\n".join(sections)),
        encoding="utf-8")
    return path


# --------------------------------------------------------------------- cli


def pdf_for(root, slug):
    """The Keynote export behind a slug."""
    for path in sorted((Path(root) / "slides").glob("*.pdf")):
        if slug_for(path.name) == slug:
            return path
    raise ValueError(f"no PDF in slides/ maps to slug {slug!r}")


def build_deck(root, pdf_path):
    """Render, classify, emit. Returns the counts Task 13 records."""
    root = Path(root)
    slug = slug_for(pdf_path.name)
    title = title_for(pdf_path.name)

    written = render_pages(pdf_path, root / "decks" / slug / "pages")
    manifest = load_manifest(root, slug)
    if manifest:
        _, created = save_pages(root, slug, pdf_path.name,
                                manifest_pages(manifest, pdf_path), manifest=True)
    else:
        _, created = save_pages(root, slug, pdf_path.name, classify_pages(pdf_path))
    payload = load_pages(root, slug)
    pages = payload["pages"]
    notes = load_notes(root, slug)
    media = manifest_media(manifest) if manifest else {}
    index = emit_deck(root, slug, title, pages, notes, media)

    kinds = [page["kind"] for page in pages]
    finals = final_pages(pages)
    unresolved = sum(1 for page in finals
                     if notes.get(page, "").strip() == UNRESOLVED)
    return {
        "slug": slug,
        "title": title,
        "pdf_pages": len(pages),
        "final_slides": len(finals),
        "fragments": len(pages) - len(finals),
        "unsure": kinds.count("unsure"),
        "notes_written": sum(1 for page in finals if page in notes),
        "unresolved": unresolved,
        "classification_created": created,
        "manifest": manifest is not None,
        "media": sum(len(items) for items in media.values()),
        "pages_written": len(written),
        "index": index,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(REPO_ROOT),
                        help="course repo root (default: this file's repo)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--deck", help="one deck slug, e.g. 08-deep-learning")
    group.add_argument("--all", action="store_true", help="every deck")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if args.deck:
        pdfs = [pdf_for(root, args.deck)]
    else:
        pdfs = sorted((root / "slides").glob("*.pdf"))

    print(f"{'deck':<52} {'pages':>5} {'slides':>6} {'frags':>5} "
          f"{'unsure':>6} {'notes':>5} {'media':>5} {'from':>8}")
    for pdf_path in pdfs:
        result = build_deck(root, pdf_path)
        print(f"{result['slug']:<52} {result['pdf_pages']:>5} "
              f"{result['final_slides']:>6} {result['fragments']:>5} "
              f"{result['unsure']:>6} {result['notes_written']:>5} "
              f"{result['media']:>5} "
              f"{'keynote' if result['manifest'] else 'text':>8}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
