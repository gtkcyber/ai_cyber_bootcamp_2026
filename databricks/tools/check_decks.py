#!/usr/bin/env python3
"""Gate for the bootcamp decks. Run it before a deck is shown to anybody.

    .venv/bin/python databricks/tools/check_decks.py                 # every deck
    .venv/bin/python databricks/tools/check_decks.py --deck 08-deep-learning
    .venv/bin/python databricks/tools/check_decks.py --ship          # no UNRESOLVED
    .venv/bin/python databricks/tools/check_decks.py --unresolved    # the report

Exit status is the number of hard failures, capped at 125.

What it does not check: reveal's overflow guard, which measures live DOM in a
browser and has no browser here. Its arithmetic is covered instead -- every
page image is exactly the canvas size, so an image slide cannot clip. The
runtime guard is watched during the deployed-app spot check.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_decks import (PAGE_HEIGHT, PAGE_WIDTH, REPO_ROOT, UNRESOLVED,
                         load_manifest, manifest_kinds,
                         COURSE_NAME, final_pages, load_notes, load_pages,
                         pages_path)
from checks import prose

IMG_RE = re.compile(r'<img class="page(?: fragment)?" src="([^"]+)"')
MEDIA_RE = re.compile(r'<(?:video|iframe) class="media(?: fragment)?"')
LOCAL_MEDIA_RE = re.compile(r'(?:data-src|poster)="(media/[^"]+)"')
# emit_deck stamps every <section> with data-page="N", so the tag is never
# the bare four characters "<section>" in a real build; match the opening
# tag itself rather than any one attribute on it.
SECTION_RE = re.compile(r"<section\b")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
EXIT_CAP = 125


def deck_slugs(root):
    meta = Path(root) / "databricks" / "pages"
    return sorted(path.stem for path in meta.glob("*.json"))


def check_deck(root, slug, ship=False):
    """(failures, warnings) for one deck. Both are lists of prefixed strings."""
    root = Path(root)
    failures, warnings = [], []
    where = f"{slug}:"

    if not pages_path(root, slug).exists():
        return [f"{where} databricks/pages/{slug}.json is missing"], []
    payload = load_pages(root, slug)
    pages = payload["pages"]
    finals = final_pages(pages)

    # A manifest deck's classification is derived from the manifest, so the
    # two disagreeing means the deck was not rebuilt after the manifest changed.
    manifest = load_manifest(root, slug)
    if manifest and (not payload.get("manifest")
                     or [p["kind"] for p in pages] != manifest_kinds(manifest)):
        failures.append(f"{where} classification does not match the Keynote "
                        f"manifest; rebuild the deck")

    unsure = [page["page"] for page in pages if page["kind"] == "unsure"]
    if unsure:
        warnings.append(f"{where} {len(unsure)} unsure page(s) never reviewed: "
                        f"{', '.join(str(n) for n in unsure)}")

    index_path = root / "decks" / slug / "index.html"
    if not index_path.is_file():
        return failures + [f"{where} decks/{slug}/index.html is missing"], warnings
    markup = index_path.read_text(encoding="utf-8")

    title = TITLE_RE.search(markup)
    if not title or not title.group(1).startswith(f"{COURSE_NAME} &mdash; "):
        got = title.group(1) if title else "(none)"
        failures.append(f"{where} title is {got!r}, expected "
                        f"'{COURSE_NAME} &mdash; <name>'")

    sections = len(SECTION_RE.findall(markup))
    if sections != len(finals):
        failures.append(f"{where} {sections} <section> in the deck, "
                        f"{len(finals)} final slide(s) in the classification")

    sources = IMG_RE.findall(markup)
    if len(sources) != len(pages):
        failures.append(f"{where} {len(sources)} page image(s) in the deck, "
                        f"{len(pages)} page(s) in the PDF")

    for source in sources:
        image_path = index_path.parent / source
        if not image_path.is_file():
            failures.append(f"{where} {source} is referenced and missing")
            continue
        with Image.open(image_path) as image:
            if image.size != (PAGE_WIDTH, PAGE_HEIGHT):
                failures.append(
                    f"{where} {source} is {image.size[0]}x{image.size[1]}, "
                    f"expected {PAGE_WIDTH}x{PAGE_HEIGHT}")

    expected_media = len(manifest.get("media", [])) if manifest else 0
    if len(MEDIA_RE.findall(markup)) != expected_media:
        failures.append(f"{where} {len(MEDIA_RE.findall(markup))} media element(s) "
                        f"in the deck, {expected_media} in the manifest")
    for source in LOCAL_MEDIA_RE.findall(markup):
        if not (index_path.parent / source).is_file():
            failures.append(f"{where} {source} is referenced and missing")

    try:
        notes = load_notes(root, slug)
    except ValueError as bad_file:
        # One malformed notes file must not stop the other fifteen decks
        # from being checked.
        return failures + [f"{where} {bad_file}"], warnings
    for page in finals:
        body = notes.get(page, "").strip()
        if not body:
            failures.append(f"{where} page {page} has no note and no "
                            f"{UNRESOLVED} marker")
            continue
        if body == UNRESOLVED:
            message = f"{where} page {page} is still {UNRESOLVED}"
            (failures if ship else warnings).append(message)
            continue
        for finding in prose.check_note(body):
            failures.append(f"{where} page {page}: {finding}")

    orphans = sorted(set(notes) - set(finals))
    if orphans:
        failures.append(f"{where} note(s) for non-final page(s): "
                        f"{', '.join(str(n) for n in orphans)}")
    return failures, warnings


def unresolved_rows(root, slugs):
    """(slug, page, the words on that slide) for every unresolved note."""
    rows = []
    for slug in slugs:
        payload = load_pages(root, slug)
        text = {page["page"]: page["text"] for page in payload["pages"]}
        notes = load_notes(root, slug)
        for page in final_pages(payload["pages"]):
            if notes.get(page, "").strip() == UNRESOLVED:
                rows.append((slug, page, text.get(page, "")))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(REPO_ROOT))
    parser.add_argument("--deck", help="one deck slug (default: all of them)")
    parser.add_argument("--ship", action="store_true",
                        help=f"treat {UNRESOLVED} as a failure")
    parser.add_argument("--unresolved", action="store_true",
                        help="print the unresolved report and stop")
    args = parser.parse_args(argv)

    root = Path(args.root)
    slugs = [args.deck] if args.deck else deck_slugs(root)

    if args.unresolved:
        rows = unresolved_rows(root, slugs)
        for slug, page, text in rows:
            print(f"{slug}\tp{page:03d}\t{text[:160]}")
        print(f"\n{len(rows)} unresolved slide(s) across {len(slugs)} deck(s)",
              file=sys.stderr)
        return 0

    failures, warnings = [], []
    for slug in slugs:
        deck_failures, deck_warnings = check_deck(root, slug, ship=args.ship)
        failures += deck_failures
        warnings += deck_warnings

    for warning in warnings:
        print(f"  WARN  {warning}")
    for failure in failures:
        print(f"  FAIL  {failure}")
    print(f"\n{len(slugs)} deck(s): {len(failures)} failure(s), "
          f"{len(warnings)} warning(s)")
    return min(len(failures), EXIT_CAP)


if __name__ == "__main__":
    sys.exit(main())
