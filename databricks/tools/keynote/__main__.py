"""Inspect a decoded Keynote deck.

    .venv/bin/python -m keynote inspect "slides/Module 3 - Feature Engineering.key"
    .venv/bin/python -m keynote inspect Module14.key --json out/14.json

Prints a per-slide summary (number, title, drawable count, chunks and their
build events, movies, web videos, tables); `--json` additionally dumps the
full model as JSON.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

from keynote.model import Deck, load_deck


def _to_jsonable(value):
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: _to_jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (tuple, list)):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    return value


def _print_summary(deck: Deck) -> None:
    print(f"{deck.name}  ({len(deck.slides)} slides)")
    for slide in deck.slides:
        label = f"#{slide.number}" if slide.number is not None else "(skipped)"
        title = slide.title or "(untitled)"
        print(f"\n{label} {title!r}  drawables={len(slide.drawables)}")
        for index, chunk in enumerate(slide.chunks, start=1):
            events = ", ".join(f"{e.type}:{e.effect}@{e.drawable}" for e in chunk)
            print(f"  chunk {index}: {events}")
        for movie in slide.movies:
            print(f"  movie: {movie.data_path}")
        for video in slide.web_videos:
            print(f"  web video: {video.url} ({video.video_id})")
        for table in slide.tables:
            print(f"  table: {table.rows}x{table.columns}"
                  f" header={table.header_rows}x{table.header_columns}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m keynote",
                                     description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="summarize a decoded deck")
    inspect_parser.add_argument("key", type=Path, help="a .key file or directory package")
    inspect_parser.add_argument("--json", type=Path,
                                help="dump the model as JSON to this path")

    args = parser.parse_args(argv)
    deck = load_deck(args.key)
    _print_summary(deck)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(_to_jsonable(deck), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
