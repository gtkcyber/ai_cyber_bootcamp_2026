#!/usr/bin/env python3
"""Move a deck's notes from the pages of its text-classified build to the pages
of its Keynote-manifest build.

    .venv/bin/python databricks/tools/rekey_notes.py --deck 11-ai-components --manifests DIR
    .venv/bin/python databricks/tools/rekey_notes.py --all --manifests DIR

Run it once per deck, after `build_keynote.py` has produced the manifest and
before that build's classification replaces the text-classified one in
databricks/pages/ (the tool refuses a classification that already comes from
a manifest). Every course deck's old PDF had exactly one page per Keynote
slide, so old page p is Keynote slide p, and the note keyed to p moves to the
finished page of slide p in the manifest. Where the text classifier had
merged consecutive slides into one build and the note sat on the last of
them, each slide now gets that note, and the report names them so a human
can split the talk track.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_decks import (REPO_ROOT, _validate_manifest, final_pages,  # noqa: E402
                         load_notes, load_pages, notes_path)


def finished_pages(manifest) -> dict[int, int]:
    """{Keynote slide number: the page showing its finished state}."""
    return {entry["slide"]: entry["page"] for entry in manifest["pages"]
            if entry["stage"] == entry["stages"] - 1}


def rekey(pages, notes, manifest) -> tuple[dict[int, str], list[tuple[int, int]]]:
    """(new notes keyed by new page, the (old page, new page) pairs that
    received a copy of a note written for a build they were merged into)."""
    finished = finished_pages(manifest)
    groups: dict[int, list[int]] = {}
    for page in pages:
        groups.setdefault(page["group"], []).append(page["page"])
    moved, copied = {}, []
    for members in groups.values():
        last = max(members)
        note = notes.get(last)
        if note is None:
            continue
        for old in members:
            moved[finished[old]] = note
            if old != last:
                copied.append((old, finished[old]))
    return moved, copied


def write_notes(path: Path, notes: dict[int, str]) -> None:
    sections = [f"## Page {page}\n\n{notes[page].strip()}\n" for page in sorted(notes)]
    path.write_text("\n".join(sections), encoding="utf-8")


def rekey_deck(root: Path, slug: str, manifests: Path) -> dict:
    payload = load_pages(root, slug)
    if payload.get("manifest"):
        raise SystemExit(f"{slug}: databricks/pages/{slug}.json already comes from a manifest; "
                         f"the notes were re-keyed before")
    manifest = read_manifest(manifests, slug)
    pages = payload["pages"]
    if len(finished_pages(manifest)) != len(pages):
        raise SystemExit(f"{slug}: {len(pages)} old pages but the manifest has "
                         f"{len(finished_pages(manifest))} slides; old page p is not slide p")
    notes = load_notes(root, slug)
    moved, copied = rekey(pages, notes, manifest)
    write_notes(notes_path(root, slug), moved)
    return {"slug": slug, "notes": len(moved), "copied": copied,
            "orphans": sorted(set(notes) - set(final_pages(pages)))}


def read_manifest(directory: Path, slug: str):
    path = directory / f"{slug}.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    _validate_manifest(manifest, path)
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--manifests", type=Path,
                        help="folder of <slug>.json manifests (default: <root>/databricks/keynote)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--deck")
    group.add_argument("--all", action="store_true")
    args = parser.parse_args(argv)
    manifests = args.manifests or args.root / "databricks" / "keynote"
    slugs = [args.deck] if args.deck else sorted(p.stem for p in manifests.glob("*.json"))
    for slug in slugs:
        result = rekey_deck(args.root, slug, manifests)
        print(f"{slug:<48} {result['notes']:>4} notes  {len(result['copied']):>3} copied from a merged build")
        for old, new in result["copied"]:
            print(f"    old page {old} (now page {new}) carries the note of the build it was merged into")
        for page in result["orphans"]:
            print(f"    old note for page {page} was not on a final page and was dropped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
