import sys
from pathlib import Path

import nbformat

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from check_notebook import (
    check_no_direct_llm,
    check_no_local_data_paths,
    check_no_pip,
    check_pairs,
    check_seam,
    check_seam_drift,
)
from edits import Module
from seam import SEAM_BASE, SEAM_LLM


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


def test_markdown_mentioning_the_local_path_is_a_violation():
    nb = _nb([("code", SEAM_BASE), ("markdown", "locally the file is at ../data/x.csv")])
    assert len(check_no_local_data_paths(nb)) == 1


def test_markdown_may_say_data_home_instead():
    nb = _nb([("code", SEAM_BASE), ("markdown", "locally the file is at DATA_HOME + 'x.csv'")])
    assert check_no_local_data_paths(nb) == []


def test_ai_examples_literal_in_code_is_a_violation():
    nb = _nb([("code", SEAM_BASE),
              ("code", 'open("../ai_examples/skills/x/SKILL.md")')])
    assert len(check_no_local_data_paths(nb)) == 1


def test_bare_dot_data_literal_in_code_is_a_violation():
    nb = _nb([("code", SEAM_BASE), ("code", 'datasets.CIFAR10("./data")')])
    assert len(check_no_local_data_paths(nb)) == 1


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


def test_seam_drift_is_clean_when_the_seam_matches_its_module():
    nb = _nb([("code", SEAM_BASE), ("code", "x = 1")])
    module = Module("notebooks/w.ipynb", None, "base", [], [], [])
    assert check_seam_drift(nb, module) == []


def test_seam_drift_flags_an_edited_seam_cell():
    edited = SEAM_BASE.replace("os.makedirs(WORK_HOME", "# tampered\nos.makedirs(WORK_HOME")
    nb = _nb([("code", edited), ("code", "x = 1")])
    module = Module("notebooks/w.ipynb", None, "base", [], [], [])
    assert len(check_seam_drift(nb, module)) == 1


def test_seam_drift_flags_the_wrong_flavour():
    nb = _nb([("code", SEAM_BASE), ("code", "x = 1")])
    module = Module("notebooks/w.ipynb", "answers/w.ipynb", "llm", [], [], [])
    assert len(check_seam_drift(nb, module)) == 1


def test_seam_drift_is_a_noop_without_a_matching_module():
    nb = _nb([("code", SEAM_BASE), ("code", "x = 1")])
    assert check_seam_drift(nb, None) == []


def test_check_pairs_flags_a_seam_flavour_mismatch(tmp_path):
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "answers").mkdir()
    import nbformat as nbf
    nbf.write(_nb([("code", SEAM_BASE)]), str(tmp_path / "notebooks" / "w.ipynb"))
    nbf.write(_nb([("code", SEAM_LLM)]), str(tmp_path / "answers" / "a.ipynb"))
    modules = [Module("notebooks/w.ipynb", "answers/a.ipynb", "base", [], [], [])]
    out = check_pairs(tmp_path, modules=modules)
    assert len(out) == 1
    assert "base" in out[0] and "llm" in out[0]


def test_check_pairs_is_clean_when_flavours_match(tmp_path):
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "answers").mkdir()
    import nbformat as nbf
    nbf.write(_nb([("code", SEAM_BASE)]), str(tmp_path / "notebooks" / "w.ipynb"))
    nbf.write(_nb([("code", SEAM_BASE)]), str(tmp_path / "answers" / "a.ipynb"))
    modules = [Module("notebooks/w.ipynb", "answers/a.ipynb", "base", [], [], [])]
    assert check_pairs(tmp_path, modules=modules) == []


def test_check_pairs_skips_modules_with_no_answer(tmp_path):
    (tmp_path / "notebooks").mkdir()
    import nbformat as nbf
    nbf.write(_nb([("code", "x = 1")]), str(tmp_path / "notebooks" / "w.ipynb"))
    modules = [Module("notebooks/w.ipynb", None, "base", [], [], [])]
    assert check_pairs(tmp_path, modules=modules) == []
