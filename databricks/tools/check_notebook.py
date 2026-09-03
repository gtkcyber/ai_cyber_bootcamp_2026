#!/usr/bin/env python3
"""Gate for the Databricks port of the bootcamp notebooks.

CLI (from the course repo root):
    .venv/bin/python databricks/tools/check_notebook.py notebooks/*.ipynb answers/*.ipynb
    .venv/bin/python databricks/tools/check_notebook.py --all

Exit code is the number of violations (capped at 255). 0 means clean.

Rules:
  1. seam            the marker-commented data-loader cell appears exactly once
  2. seam-drift      the seam cell's source equals seam_text() for the notebook's
                     declared flavour in edits.py's MODULES table
  3. data-paths      no '../data' literal in a code cell outside the seam cell, no
                     '../ai_examples' or './data' literal in a code cell, and no
                     '../data' mention in a markdown cell
  4. pip             no !pip / %pip in a code cell outside the seam cell,
                     except Module 4.3's sanctioned TPOT install
  5. llm             no ChatAnthropic( / anthropic.Anthropic( / langchain_anthropic
                     import outside the seam cell
  6. pairs           every worksheet and its answer carry the same seam flavour;
                     runs whenever more than one notebook is checked
"""

import glob
import sys
from pathlib import Path

import nbformat

sys.path.insert(0, str(Path(__file__).resolve().parent))

from seam import SEAM_END, SEAM_START, seam_text

# Module 4.3 only (spec Decision 12): TPOT needs an old setuptools, which no
# cluster library can express, so that one notebook installs it notebook-scoped.
TPOT_PIP = '%pip install "setuptools<58" tpot'
TPOT_NOTEBOOK = "Worksheet_4.3_Automate_It_All"

CODE_LITERALS = ("'../data", '"../data', "'./data", '"./data', "'../ai_examples", '"../ai_examples')
MARKDOWN_LITERALS = ("../data",)
PIP_TOKENS = ("!pip", "%pip", "!conda", "%conda")
LLM_TOKENS = ("ChatAnthropic(", "anthropic.Anthropic(", "langchain_anthropic")


def load_notebook(path_str: str):
    path = Path(path_str)
    if not path.is_file():
        print(f"ERROR: not a file: {path_str}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(path, encoding="utf-8") as fh:
            return nbformat.read(fh, as_version=4)
    except (ValueError, OSError) as exc:
        print(f"ERROR: cannot read {path_str}: {exc}", file=sys.stderr)
        sys.exit(2)


def _is_seam(cell) -> bool:
    return cell.cell_type == "code" and SEAM_START in cell.source


def _body_cells(nb):
    """Every code cell that is not the seam cell, with its index."""
    return [(i, c) for i, c in enumerate(nb.cells)
            if c.cell_type == "code" and not _is_seam(c)]


def check_seam(nb) -> list:
    seams = [i for i, c in enumerate(nb.cells) if _is_seam(c)]
    if not seams:
        return ["seam: no data-loader cell"]
    if len(seams) > 1:
        return [f"seam: {len(seams)} data-loader cells at indices {seams}"]
    if SEAM_END not in nb.cells[seams[0]].source:
        return [f"seam: cell {seams[0]} has a start marker but no end marker"]
    return []


def check_no_local_data_paths(nb) -> list:
    out = []
    for i, cell in _body_cells(nb):
        for line in cell.source.splitlines():
            if any(lit in line for lit in CODE_LITERALS):
                out.append(f"data-paths: cell {i}: {line.strip()[:100]}")
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "markdown":
            continue
        for line in cell.source.splitlines():
            if any(lit in line for lit in MARKDOWN_LITERALS):
                out.append(f"data-paths: cell {i} (markdown): {line.strip()[:100]}")
    return out


def _module_for(root: Path, path_str: str):
    """The MODULES entry whose worksheet or answer resolves to path_str, or None."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from edits import MODULES

    try:
        rel = str(Path(path_str).resolve().relative_to(root))
    except ValueError:
        rel = path_str
    for module in MODULES:
        if module.worksheet == rel or module.answer == rel:
            return module
    return None


def check_seam_drift(nb, module) -> list:
    """The seam cell's source must equal seam_text() for the module's declared flavour."""
    if module is None or module.seam == "none":
        return []
    seams = [c for c in nb.cells if _is_seam(c)]
    if len(seams) != 1:
        return []  # check_seam already reports a missing/duplicate seam
    wanted = seam_text(with_llm=(module.seam == "llm"))
    if seams[0].source != wanted:
        return ["seam-drift: seam cell does not match seam_text() for this module"]
    return []


def check_no_pip(nb, name: str) -> list:
    allow_tpot = TPOT_NOTEBOOK in name
    out = []
    for i, cell in _body_cells(nb):
        for line in cell.source.splitlines():
            stripped = line.strip()
            if not any(stripped.startswith(tok) for tok in PIP_TOKENS):
                continue
            if allow_tpot and stripped == TPOT_PIP:
                continue
            out.append(f"pip: cell {i}: {stripped[:100]}")
    return out


def check_no_direct_llm(nb) -> list:
    out = []
    for i, cell in _body_cells(nb):
        for line in cell.source.splitlines():
            if line.lstrip().startswith("#"):
                continue
            for token in LLM_TOKENS:
                if token in line:
                    out.append(f"llm: cell {i}: {line.strip()[:100]}")
                    break
    return out


def check_pairs(root: Path, modules=None) -> list:
    """Every worksheet and its answer must carry the same seam flavour."""
    if modules is None:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from edits import MODULES as modules

    out = []
    for module in modules:
        if not module.answer:
            continue
        flavours = []
        for rel in (module.worksheet, module.answer):
            nb = load_notebook(root / rel)
            seam = next((c.source for c in nb.cells if _is_seam(c)), "")
            flavours.append("llm" if "def make_llm(" in seam else
                            "base" if seam else "none")
        if flavours[0] != flavours[1]:
            out.append(f"pairs: {module.worksheet} is {flavours[0]} but its "
                       f"answer is {flavours[1]}")
    return out


def main() -> int:
    args = sys.argv[1:]
    root = Path(__file__).resolve().parents[2]
    if args == ["--all"]:
        paths = sorted(glob.glob(str(root / "notebooks" / "*.ipynb"))) + \
                sorted(glob.glob(str(root / "answers" / "*.ipynb")))
    elif args:
        paths = args
    else:
        print("Usage: check_notebook.py <notebook.ipynb> [more...] | --all")
        return 2

    total = 0
    for path_str in paths:
        nb = load_notebook(path_str)
        name = Path(path_str).name
        module = _module_for(root, path_str)
        violations = (check_seam(nb)
                      + check_seam_drift(nb, module)
                      + check_no_local_data_paths(nb)
                      + check_no_pip(nb, name)
                      + check_no_direct_llm(nb))
        if violations:
            print(f"\n[FAIL] {path_str}")
            for v in violations:
                print(f"  {v}")
            total += len(violations)
        else:
            print(f"[OK]   {path_str}")

    if len(paths) > 1:
        pair_violations = check_pairs(root)
        for v in pair_violations:
            print(f"  {v}")
        total += len(pair_violations)

    print(f"\n{total} violation(s)")
    return min(total, 255)


if __name__ == "__main__":
    raise SystemExit(main())
