"""The notebook data seam: one marker-commented cell per worksheet and answer.

SEAM_BASE is the spec's data-loader block verbatim
(docs/specs/2026-09-02-bootcamp-databricks-port-design.md, "Notebook seam").
SEAM_LLM is the Modules 10-13 extension: make_client() for the OpenAI SDK and
make_llm() for LangChain, each with a local branch and a Databricks branch. It also
carries SKILLS_HOME, the one path Module 11.2 needs into the ai_examples skill that
ships with the course data on Databricks but stays at its original repo path locally.
"""

SEAM_START = "# --- data-loader (local files / Databricks volume) ---"
SEAM_END = "# --- end data-loader ---"

_BODY = '''import os
try:
    dbutils  # defined only on Databricks
    DATA_HOME = os.environ.get("COURSE_DATA_HOME", "/Volumes/ai_cyber_bootcamp/course/data/")
    WORK_HOME = os.path.abspath("../work") + "/"
    ON_DATABRICKS = True
except NameError:
    DATA_HOME = "../data/"
    WORK_HOME = DATA_HOME
    ON_DATABRICKS = False
os.makedirs(WORK_HOME, exist_ok=True)

def handoff(name):
    """Output of an earlier worksheet: the student's own copy if it exists, else the shipped one."""
    p = WORK_HOME + name
    return p if os.path.exists(p) else DATA_HOME + name
'''

_LLM_BODY = '''
COURSE_LLM_MODEL = (
    os.environ.get("COURSE_LLM_ENDPOINT", "databricks-deepseek-v4-flash-0731")
    if ON_DATABRICKS
    else os.environ.get("COURSE_LLM_MODEL", "claude-opus-4-8")
)

# Vision calls: the default endpoint above is text-only, so image cells pass this
# model explicitly to make_client()'s caller instead of COURSE_LLM_MODEL.
COURSE_LLM_VISION_MODEL = (
    os.environ.get("COURSE_LLM_VISION_ENDPOINT", "databricks-glm-5-3-flash")
    if ON_DATABRICKS
    else os.environ.get("COURSE_LLM_MODEL", "claude-opus-4-8")
)

# Module 11.2 reads one ai_examples skill file. ai_examples/ itself is out of scope
# for the port, so the volume ships only that one file, under DATA_HOME/skills/;
# locally the file is still at its original repo path.
SKILLS_HOME = DATA_HOME + "skills/" if ON_DATABRICKS else "../ai_examples/skills/"


def make_client():
    """OpenAI-compatible chat client: Anthropic locally, the workspace endpoint on Databricks."""
    from openai import OpenAI
    if ON_DATABRICKS:
        ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
        return OpenAI(api_key=ctx.apiToken().get(),
                      base_url=f"{ctx.apiUrl().get()}/serving-endpoints")
    from dotenv import load_dotenv
    load_dotenv()
    return OpenAI(api_key=os.environ["ANTHROPIC_API_KEY"],
                  base_url="https://api.anthropic.com/v1/")


def make_llm(**kwargs):
    """LangChain chat model: ChatDatabricks on Databricks, ChatAnthropic locally."""
    if ON_DATABRICKS:
        from databricks_langchain import ChatDatabricks
        return ChatDatabricks(endpoint=COURSE_LLM_MODEL, **kwargs)
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(model=COURSE_LLM_MODEL, **kwargs)
'''

SEAM_BASE = f"{SEAM_START}\n{_BODY}{SEAM_END}\n"
SEAM_LLM = f"{SEAM_START}\n{_BODY}{_LLM_BODY}{SEAM_END}\n"


def seam_text(with_llm: bool = False) -> str:
    """The seam cell source for one notebook."""
    return SEAM_LLM if with_llm else SEAM_BASE


from dataclasses import dataclass

import nbformat


class EditError(Exception):
    """A notebook did not have the shape the substitution table says it has."""


@dataclass(frozen=True)
class Sub:
    """One exact substitution. `count` is how many times `old` must appear."""

    old: str
    new: str
    count: int = 1
    kind: str = "code"  # "code" or "markdown"


def load(path):
    with open(path, encoding="utf-8") as fh:
        return nbformat.read(fh, as_version=4)


def save(path, nb):
    with open(path, "w", encoding="utf-8") as fh:
        nbformat.write(nb, fh)


def _seam_indices(nb):
    return [i for i, c in enumerate(nb.cells)
            if c.cell_type == "code" and SEAM_START in c.source]


def upsert_seam(nb, with_llm: bool = False) -> bool:
    """Insert the seam cell, or replace an outdated one. True if the notebook changed."""
    wanted = seam_text(with_llm)
    found = _seam_indices(nb)
    if len(found) > 1:
        raise EditError(f"{len(found)} seam cells in one notebook: indices {found}")
    if found:
        cell = nb.cells[found[0]]
        if cell.source == wanted:
            return False
        cell.source = wanted
        return True
    # Insert after a leading run of markdown (the title block), else at the top.
    at = 0
    while at < len(nb.cells) and nb.cells[at].cell_type == "markdown":
        at += 1
    nb.cells.insert(at, nbformat.v4.new_code_cell(wanted))
    return True


def apply_subs(nb, subs) -> int:
    """Apply each Sub across the notebook. Idempotent; any surprise is an EditError.

    The seam cell is excluded from every scan: it is a protected unit written only by
    upsert_seam, and the LLM seam's own make_llm() fallback branch contains the literal
    text `from langchain_anthropic import ChatAnthropic`, which would otherwise double-
    count (and, worse, get rewritten) alongside a notebook's own matching import line.
    """
    applied = 0
    for sub in subs:
        cells = [c for c in nb.cells if c.cell_type == sub.kind and SEAM_START not in c.source]
        hits = sum(c.source.count(sub.old) for c in cells)
        if hits == 0:
            already = sum(c.source.count(sub.new) for c in cells)
            if already >= sub.count:
                continue  # already applied — idempotent re-run
            raise EditError(
                f"old text {sub.old!r} found 0 times, new text found "
                f"{already} times (expected {sub.count})"
            )
        if hits != sub.count:
            raise EditError(f"old text {sub.old!r} found {hits} times, expected {sub.count}")
        for c in cells:
            if sub.old in c.source:
                c.source = c.source.replace(sub.old, sub.new)
        applied += 1
    return applied


def insert_before_seam(nb, source: str) -> bool:
    """Put `source` in its own code cell immediately before the seam cell.

    Used for the one sanctioned notebook-scoped install (Module 4.3): it has to run
    before the seam, because dbutils.library.restartPython() clears everything
    defined so far. Idempotent on the exact source text.
    """
    found = _seam_indices(nb)
    if not found:
        raise EditError("no seam cell to insert before")
    if any(c.cell_type == "code" and c.source == source for c in nb.cells):
        return False
    nb.cells.insert(found[0], nbformat.v4.new_code_cell(source))
    return True
