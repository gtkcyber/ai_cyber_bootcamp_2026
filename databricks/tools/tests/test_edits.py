import sys
from pathlib import Path

import nbformat
import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from edits import MODULES, Module, _matches_only, port
from seam import SEAM_START, EditError, Sub

REPO = TOOLS.parents[1]


def test_every_declared_file_exists():
    missing = []
    for m in MODULES:
        for rel in (m.worksheet, m.answer):
            if rel and not (REPO / rel).exists():
                missing.append(rel)
    assert missing == []


def test_no_duplicate_entries():
    names = [m.worksheet for m in MODULES]
    assert len(names) == len(set(names))


def test_port_applies_seam_and_subs(tmp_path):
    ws = tmp_path / "notebooks" / "w.ipynb"
    ws.parent.mkdir(parents=True)
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_markdown_cell("# title"))
    nb.cells.append(nbformat.v4.new_code_cell("DATA_HOME = '../data'\nx = 1"))
    nbformat.write(nb, str(ws))
    m = Module("notebooks/w.ipynb", None, "base",
               [Sub("DATA_HOME = '../data'", "# DATA_HOME comes from the data-loader cell")],
               [], [])
    port(m, tmp_path, check_only=False)
    out = nbformat.read(str(ws), as_version=4)
    assert SEAM_START in out.cells[1].source
    assert "DATA_HOME = '../data'" not in out.cells[2].source


def test_port_check_only_does_not_write(tmp_path):
    ws = tmp_path / "notebooks" / "w.ipynb"
    ws.parent.mkdir(parents=True)
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell("x = 1"))
    nbformat.write(nb, str(ws))
    before = ws.read_text()
    port(Module("notebooks/w.ipynb", None, "base", [], [], []), tmp_path, check_only=True)
    assert ws.read_text() == before


def test_port_reports_a_bad_table_entry(tmp_path):
    ws = tmp_path / "notebooks" / "w.ipynb"
    ws.parent.mkdir(parents=True)
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell("x = 1"))
    nbformat.write(nb, str(ws))
    m = Module("notebooks/w.ipynb", None, "base", [Sub("NOPE", "nope")], [], [])
    with pytest.raises(EditError):
        port(m, tmp_path, check_only=True)


def test_only_selects_the_numbered_module_by_exact_boundary():
    m = Module("notebooks/Worksheet_1.1_x.ipynb", "answers/Worksheet_1.1_x-Answers.ipynb", "base")
    assert _matches_only(m, "1.1") is True


def test_only_does_not_confuse_1_1_with_11_1():
    m = Module("notebooks/Worksheet_11.1_x.ipynb", "answers/Worksheet_11.1_x-Answers.ipynb", "base")
    assert _matches_only(m, "1.1") is False


def test_only_selects_a_module_with_no_worksheet_name():
    m = Module("answers/openai_api_fundamentals_answers.ipynb", None, "llm")
    assert _matches_only(m, "openai_api_fundamentals") is True


def test_only_does_not_select_an_unrelated_module():
    m = Module("notebooks/Worksheet_1.1_x.ipynb", "answers/Worksheet_1.1_x-Answers.ipynb", "base")
    assert _matches_only(m, "4.1") is False


def test_the_answer_only_module_is_in_the_real_table():
    assert any(m.answer is None and "Worksheet_" not in m.worksheet for m in MODULES)
