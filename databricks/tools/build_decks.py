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
