import sys
from pathlib import Path

import nbformat

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from check_notebook import (
    check_no_direct_llm,
    check_no_local_data_paths,
    check_no_pip,
    check_seam,
)
from seam import SEAM_BASE


def _nb(sources):
    nb = nbformat.v4.new_notebook()
    for kind, src in sources:
        nb.cells.append(
            nbformat.v4.new_code_cell(src) if kind == "code"
            else nbformat.v4.new_markdown_cell(src)
        )
    return nb


def test_seam_missing_is_a_violation():
    assert len(check_seam(_nb([("code", "x = 1")]))) == 1


def test_seam_twice_is_a_violation():
    assert len(check_seam(_nb([("code", SEAM_BASE), ("code", SEAM_BASE)]))) == 1


def test_seam_once_is_clean():
    assert check_seam(_nb([("code", SEAM_BASE), ("code", "x = 1")])) == []


def test_local_data_literal_outside_the_seam_is_a_violation():
    nb = _nb([("code", SEAM_BASE), ("code", "pd.read_csv('../data/x.csv')")])
    assert len(check_no_local_data_paths(nb)) == 1


def test_local_data_literal_inside_the_seam_is_fine():
    assert check_no_local_data_paths(_nb([("code", SEAM_BASE)])) == []


def test_markdown_may_mention_the_local_path():
    nb = _nb([("code", SEAM_BASE), ("markdown", "locally the file is at ../data/x.csv")])
    assert check_no_local_data_paths(nb) == []


def test_pip_outside_the_seam_is_a_violation():
    nb = _nb([("code", SEAM_BASE), ("code", "!pip install foo")])
    assert len(check_no_pip(nb, "Worksheet_1.1_x.ipynb")) == 1


def test_the_tpot_pip_is_allowed_in_4_3_only():
    line = '%pip install "setuptools<58" tpot'
    nb = _nb([("code", SEAM_BASE), ("code", line)])
    assert check_no_pip(nb, "Worksheet_4.3_Automate_It_All.ipynb") == []
    assert len(check_no_pip(nb, "Worksheet_5.1_Clustering.ipynb")) == 1


def test_direct_llm_construction_is_a_violation():
    nb = _nb([("code", SEAM_BASE), ("code", 'llm = ChatAnthropic(model="x")')])
    assert len(check_no_direct_llm(nb)) == 1


def test_seam_may_name_chatanthropic():
    from seam import SEAM_LLM
    assert check_no_direct_llm(_nb([("code", SEAM_LLM)])) == []
