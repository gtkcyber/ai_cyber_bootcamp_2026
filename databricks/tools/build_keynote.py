#!/usr/bin/env python3
"""Build a course deck from its Keynote file, no Mac involved.

    .venv/bin/python databricks/tools/build_keynote.py "slides/keynote/Module 11 - AI Components.key"
    .venv/bin/python databricks/tools/build_keynote.py --all slides/keynote

Writes slides/<Module>.pdf (one page per build stage), databricks/keynote/
<slug>.json (the manifest build_decks.py groups and places media by) and
decks/<slug>/media/, then rebuilds the reveal deck. Needs Docker: the first
run builds the bootcamp-keynote image from databricks/tools/keynote/docker.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_decks import REPO_ROOT  # noqa: E402
from keynote.build import build  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("key", type=Path, help="a .key file or package, or with --all a folder of them")
    parser.add_argument("--all", action="store_true", help="build every .key in the folder")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="course repo root")
    parser.add_argument("--work", type=Path, help="keep intermediate files here instead of a temp dir")
    args = parser.parse_args(argv)

    keys = sorted(args.key.glob("*.key")) if args.all else [args.key]
    for key in keys:
        result = build(key, args.root, args.work / key.stem if args.work else None)
        print(f"{result['slug']:<44} {result['pdf_pages']:>5} pages "
              f"{result['final_slides']:>4} slides {result['fragments']:>4} stages "
              f"{result['media']:>2} media {len(result['losses']):>3} losses")
        for loss in result["losses"]:
            print(f"    slide {loss['slide']:>3} {loss['kind']}: {loss['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
