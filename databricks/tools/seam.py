"""The notebook data seam: one marker-commented cell per worksheet and answer.

SEAM_BASE is the spec's data-loader block verbatim
(docs/specs/2026-09-02-bootcamp-databricks-port-design.md, "Notebook seam").
SEAM_LLM is the Modules 10-13 extension: make_client() for the OpenAI SDK and
make_llm() for LangChain, each with a local branch and a Databricks branch.
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
