import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from seam import SEAM_BASE, SEAM_END, SEAM_LLM, SEAM_START, seam_text


def test_base_seam_is_the_spec_text():
    assert SEAM_BASE.startswith(SEAM_START)
    assert SEAM_BASE.rstrip().endswith(SEAM_END)
    assert 'DATA_HOME = os.environ.get("COURSE_DATA_HOME", "/Volumes/ai_cyber_bootcamp/course/data/")' in SEAM_BASE
    assert 'WORK_HOME = os.path.abspath("../work") + "/"' in SEAM_BASE
    assert 'DATA_HOME = "../data/"' in SEAM_BASE
    assert "def handoff(name):" in SEAM_BASE


def test_base_seam_compiles_and_runs_locally(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ns = {}
    exec(compile(SEAM_BASE, "seam", "exec"), ns)
    assert ns["ON_DATABRICKS"] is False
    assert ns["DATA_HOME"] == "../data/"
    assert ns["WORK_HOME"] == "../data/"
    assert ns["handoff"]("nope.csv") == "../data/nope.csv"


def test_llm_seam_defines_both_helpers():
    assert "def make_client():" in SEAM_LLM
    assert "def make_llm(" in SEAM_LLM
    assert "databricks-deepseek-v4-flash-0731" in SEAM_LLM
    assert "https://api.anthropic.com/v1/" in SEAM_LLM
    assert "apiToken().get()" in SEAM_LLM


def test_seam_text_composes():
    assert seam_text(with_llm=False) == SEAM_BASE
    combined = seam_text(with_llm=True)
    assert combined.startswith(SEAM_START)
    assert combined.rstrip().endswith(SEAM_END)
    assert combined.count(SEAM_START) == 1
    assert combined.count(SEAM_END) == 1


import nbformat
import pytest

from seam import EditError, Sub, apply_subs, upsert_seam


def _nb(sources):
    nb = nbformat.v4.new_notebook()
    for kind, src in sources:
        nb.cells.append(
            nbformat.v4.new_code_cell(src) if kind == "code"
            else nbformat.v4.new_markdown_cell(src)
        )
    return nb


def test_seam_goes_after_a_leading_markdown_title():
    nb = _nb([("markdown", "# Worksheet 3.1"), ("code", "import pandas as pd")])
    assert upsert_seam(nb, with_llm=False) is True
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[1].source.startswith(SEAM_START)
    assert nb.cells[2].source == "import pandas as pd"


def test_seam_goes_first_when_the_notebook_opens_with_code():
    nb = _nb([("code", "import pandas as pd")])
    upsert_seam(nb, with_llm=False)
    assert nb.cells[0].source.startswith(SEAM_START)


def test_upsert_is_idempotent():
    nb = _nb([("markdown", "# t"), ("code", "x = 1")])
    upsert_seam(nb, with_llm=False)
    before = [c.source for c in nb.cells]
    assert upsert_seam(nb, with_llm=False) is False
    assert [c.source for c in nb.cells] == before
    assert sum(SEAM_START in c.source for c in nb.cells) == 1


def test_upsert_replaces_an_outdated_seam():
    nb = _nb([("markdown", "# t"), ("code", "x = 1")])
    upsert_seam(nb, with_llm=False)
    assert upsert_seam(nb, with_llm=True) is True
    assert sum(SEAM_START in c.source for c in nb.cells) == 1
    assert "def make_llm(" in nb.cells[1].source


def test_two_seam_cells_is_a_hard_failure():
    nb = _nb([("code", SEAM_BASE), ("code", SEAM_BASE)])
    with pytest.raises(EditError, match="2 seam cells"):
        upsert_seam(nb, with_llm=False)


def test_apply_subs_rewrites_exactly_once():
    nb = _nb([("code", "df = pd.read_csv(f'{DATA_HOME}/a.csv')")])
    n = apply_subs(nb, [Sub("f'{DATA_HOME}/a.csv'", "f'{DATA_HOME}a.csv'")])
    assert n == 1
    assert nb.cells[0].source == "df = pd.read_csv(f'{DATA_HOME}a.csv')"


def test_apply_subs_is_idempotent_when_already_applied():
    nb = _nb([("code", "df = pd.read_csv(f'{DATA_HOME}a.csv')")])
    assert apply_subs(nb, [Sub("f'{DATA_HOME}/a.csv'", "f'{DATA_HOME}a.csv'")]) == 0


def test_unknown_shape_fails_loudly():
    nb = _nb([("code", "df = pd.read_csv('somewhere/else.csv')")])
    with pytest.raises(EditError, match="found 0 times, new text found 0 times"):
        apply_subs(nb, [Sub("f'{DATA_HOME}/a.csv'", "f'{DATA_HOME}a.csv'")])


def test_wrong_count_fails_loudly():
    nb = _nb([("code", "a = X\nb = X")])
    with pytest.raises(EditError, match="expected 1"):
        apply_subs(nb, [Sub("X", "Y")])


def test_markdown_subs_only_touch_markdown_cells():
    nb = _nb([("markdown", "see ../data/x.zip"), ("code", "p = '../data/x.zip'")])
    apply_subs(nb, [Sub("../data/x.zip", "the volume", kind="markdown")])
    assert nb.cells[0].source == "see the volume"
    assert nb.cells[1].source == "p = '../data/x.zip'"


def test_apply_subs_ignores_the_seam_cells_own_text():
    # SEAM_LLM's make_llm() fallback branch itself contains the literal text
    # "from langchain_anthropic import ChatAnthropic" — apply_subs must not count or
    # rewrite that occurrence, only the notebook's own import line.
    nb = _nb([("code", SEAM_LLM),
              ("code", "from langchain_anthropic import ChatAnthropic\nllm = ChatAnthropic(model=X)")])
    n = apply_subs(nb, [Sub("from langchain_anthropic import ChatAnthropic", "# swapped")])
    assert n == 1
    assert "from langchain_anthropic import ChatAnthropic" in nb.cells[0].source  # seam untouched
    assert nb.cells[1].source == "# swapped\nllm = ChatAnthropic(model=X)"


from seam import insert_before_seam

PIP = '%pip install "setuptools<58" tpot\ndbutils.library.restartPython()'


def test_pre_cell_lands_immediately_before_the_seam():
    nb = _nb([("markdown", "# t"), ("code", "x = 1")])
    upsert_seam(nb, with_llm=False)
    assert insert_before_seam(nb, PIP) is True
    assert nb.cells[1].source == PIP
    assert nb.cells[2].source.startswith(SEAM_START)


def test_pre_cell_insert_is_idempotent():
    nb = _nb([("markdown", "# t"), ("code", "x = 1")])
    upsert_seam(nb, with_llm=False)
    insert_before_seam(nb, PIP)
    assert insert_before_seam(nb, PIP) is False
    assert sum(c.source == PIP for c in nb.cells) == 1


def test_pre_cell_needs_a_seam():
    nb = _nb([("code", "x = 1")])
    with pytest.raises(EditError, match="no seam cell"):
        insert_before_seam(nb, PIP)
