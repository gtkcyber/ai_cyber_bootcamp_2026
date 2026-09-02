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
